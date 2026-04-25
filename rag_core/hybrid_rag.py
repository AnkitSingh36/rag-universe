"""
rag_core/hybrid_rag.py  ── "The Smart RAG" ──

HOW HYBRID RAG WORKS (explain like you're 14 years old):
─────────────────────────────────────────────────────────
  Naive RAG only understands MEANING.
  BM25 only understands KEYWORDS.
  Hybrid RAG uses BOTH!

  Imagine two librarians helping you find a book:
    📚 Librarian A (BM25): "Looking for the EXACT word you said"
    🧠 Librarian B (Vector): "Looking for books about the SAME IDEA"

  Hybrid RAG asks both, combines their suggestions, gives you the BEST result.

  Example:
    Query: "TSLA earnings"

    BM25 finds:  "TSLA revenue in Q4 was $30B"    (exact keyword match)
    Vector finds: "Tesla reported strong profits"   (same meaning)
    Hybrid gives you: BOTH, ranked best first ✅

  What it's GOOD at:
    ✅ Stock tickers, product codes (TSLA, SKU-123)
    ✅ Names of people, places
    ✅ Technical jargon + casual language
    ✅ Most real-world search tasks

  What it's BAD at:
    ❌ Slower than pure BM25 (adds vector search time)
    ❌ More complex to configure and tune
─────────────────────────────────────────────────────────
"""

import time
from typing import List

import numpy as np
import faiss
from rank_bm25 import BM25Okapi

from .base import BaseRAG, Document, RAGResult
from .utils import chunk_text, embed_texts, demo_generate, try_ollama_generate


class HybridRAG(BaseRAG):
    """
    Hybrid RAG: BM25 keyword search + Vector semantic search, combined.

    Uses Reciprocal Rank Fusion (RRF) to merge results from both.

    RRF formula: score = 1/(60 + rank_in_bm25) + 1/(60 + rank_in_vector)
    This gives credit to docs that appear in BOTH result lists.
    """

    name = "Hybrid RAG"
    description = "Keyword search (BM25) + Semantic search (Vector), combined with RRF fusion."
    emoji = "🟣"
    color = "#8B5CF6"

    def __init__(self, chunk_size: int = 300, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.chunks: List[str] = []
        self.sources: List[str] = []
        self.bm25 = None           # BM25 keyword index
        self.faiss_index = None    # FAISS vector index

    def add_documents(self, texts: List[str], source: str = "document") -> int:
        """
        Build BOTH a BM25 index (keywords) and FAISS index (vectors).
        """
        self.chunks = []
        self.sources = []

        for text in texts:
            new_chunks = chunk_text(text, self.chunk_size, self.overlap)
            self.chunks.extend(new_chunks)
            self.sources.extend([source] * len(new_chunks))

        if not self.chunks:
            return 0

        # Build BM25 index (tokenize each chunk)
        tokenized = [chunk.lower().split() for chunk in self.chunks]
        self.bm25 = BM25Okapi(tokenized)

        # Build FAISS index
        embeddings = embed_texts(self.chunks).astype("float32")
        dim = embeddings.shape[1]
        self.faiss_index = faiss.IndexFlatL2(dim)
        self.faiss_index.add(embeddings)
        self._embeddings = embeddings

        return len(self.chunks)

    def retrieve(self, query: str, top_k: int = 3) -> List[Document]:
        """
        Retrieve using BOTH BM25 and Vector, then fuse results.

        Fusion method: Reciprocal Rank Fusion (RRF)
          - Rank each doc in BM25 results
          - Rank each doc in Vector results
          - Final score = sum of 1/(60 + rank) for each list
          - Higher score = more relevant (appeared near top in both)
        """
        if self.bm25 is None or self.faiss_index is None:
            return []

        n = len(self.chunks)
        k_each = min(top_k * 3, n)   # retrieve more, then fuse

        # ── BM25 retrieval ──────────────────────────
        query_tokens = query.lower().split()
        bm25_scores = self.bm25.get_scores(query_tokens)
        bm25_ranked = np.argsort(bm25_scores)[::-1][:k_each]

        # ── Vector retrieval ────────────────────────
        query_vec = embed_texts([query])
        _, vector_ranked = self.faiss_index.search(query_vec, k_each)
        vector_ranked = vector_ranked[0]

        # ── RRF Fusion ──────────────────────────────
        rrf_scores: dict = {}
        K = 60  # RRF constant (standard value)

        for rank, idx in enumerate(bm25_ranked):
            rrf_scores[int(idx)] = rrf_scores.get(int(idx), 0) + 1.0 / (K + rank + 1)

        for rank, idx in enumerate(vector_ranked):
            rrf_scores[int(idx)] = rrf_scores.get(int(idx), 0) + 1.0 / (K + rank + 1)

        # Sort by fused score, take top_k
        sorted_indices = sorted(rrf_scores.keys(), key=lambda x: rrf_scores[x], reverse=True)[:top_k]

        docs = []
        for idx in sorted_indices:
            # Determine which method found this doc
            in_bm25 = idx in set(bm25_ranked[:top_k * 2])
            in_vec = idx in set(vector_ranked[:top_k * 2])

            if in_bm25 and in_vec:
                method = "hybrid (both)"
            elif in_bm25:
                method = "keyword (BM25)"
            else:
                method = "semantic (vector)"

            docs.append(Document(
                content=self.chunks[idx],
                score=round(rrf_scores[idx], 4),
                source=self.sources[idx],
                chunk_index=idx,
                retrieval_method=method,
            ))

        return docs

    def ask(self, query: str, top_k: int = 3, use_ollama: bool = False) -> RAGResult:
        """Full pipeline: retrieve (BM25 + Vector) → fuse → generate."""
        steps = []

        t0 = time.time()
        steps.append({"step": "BM25 Search", "detail": f"Searching for keywords: {query[:40]}..."})
        steps.append({"step": "Vector Search", "detail": "Searching for semantic meaning..."})

        docs = self.retrieve(query, top_k)
        retrieval_ms = (time.time() - t0) * 1000

        steps.append({
            "step": "RRF Fusion",
            "detail": f"Merged keyword + semantic results. Top match: '{docs[0].content[:60]}...'" if docs else "No results"
        })

        t0 = time.time()
        if use_ollama:
            answer, _ = try_ollama_generate(query, docs)
        else:
            answer = demo_generate(query, docs)
        generation_ms = (time.time() - t0) * 1000

        steps.append({"step": "Generate Answer", "detail": "Combined context → answer"})

        return RAGResult(
            query=query,
            answer=answer,
            retrieved_docs=docs,
            retrieval_ms=round(retrieval_ms, 1),
            generation_ms=round(generation_ms, 1),
            rag_type=self.name,
            total_chunks_searched=len(self.chunks),
            steps=steps,
        )
