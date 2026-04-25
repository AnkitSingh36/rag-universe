"""
rag_core/rerank_rag.py  ── "The Precise RAG" ──

HOW RERANK RAG WORKS:
─────────────────────────────────────────────────────────
  Problem with Naive RAG:
    It retrieves top-3 and stops. But what if chunk #4 was actually most relevant?
    The embedding model isn't perfect — it misses subtle matches.

  Solution — Two stages:
    Stage 1 (Fast but rough):   Retrieve top 20 chunks with vector search
    Stage 2 (Slow but precise): Re-score all 20 with a BETTER model, return top 3

  Analogy:
    Imagine hiring for a job:
    - Round 1: Review 100 resumes quickly → shortlist 20
    - Round 2: Interview all 20 in detail → hire top 3

    The interview (reranking) is much more accurate but takes more time.
    You wouldn't interview all 100 — too slow. Just the pre-selected 20.

  What it's GOOD at:
    ✅ Much higher accuracy than Naive RAG
    ✅ Legal, medical, financial (where wrong answer = big problem)
    ✅ Complex queries needing nuanced understanding
    ✅ When you can afford 2x-5x latency

  What it's BAD at:
    ❌ Slower (extra reranking step)
    ❌ Needs a reranking model (cross-encoder)
    ❌ Overkill for simple chatbots
─────────────────────────────────────────────────────────
"""

import time
import re
from typing import List
import numpy as np
import faiss

from .base import BaseRAG, Document, RAGResult
from .utils import chunk_text, embed_texts, demo_generate, try_ollama_generate


class RerankRAG(BaseRAG):
    """
    Two-stage RAG:
      Stage 1: Retrieve top-N with fast vector search
      Stage 2: Re-score top-N with a more accurate scorer, return top-k
    """

    name = "Rerank RAG"
    description = "Two-stage retrieval: fast vector search (top 20) → precise reranking (top 3). Higher accuracy."
    emoji = "🔶"
    color = "#F59E0B"

    def __init__(self, chunk_size: int = 300, overlap: int = 50,
                 first_stage_k: int = 20, second_stage_k: int = 3):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.first_stage_k = first_stage_k  # how many to retrieve in stage 1
        self.second_stage_k = second_stage_k  # how many to keep after reranking
        self.chunks: List[str] = []
        self.sources: List[str] = []
        self.index = None

    def add_documents(self, texts: List[str], source: str = "document") -> int:
        self.chunks = []
        self.sources = []
        for text in texts:
            nc = chunk_text(text, self.chunk_size, self.overlap)
            self.chunks.extend(nc)
            self.sources.extend([source] * len(nc))

        if not self.chunks:
            return 0

        embs = embed_texts(self.chunks).astype("float32")
        dim = embs.shape[1]
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(embs)
        self._embs = embs
        return len(self.chunks)

    def _rerank_score(self, query: str, chunk: str) -> float:
        """
        Cross-encoder style reranking score.

        In production: use a cross-encoder model (e.g., cross-encoder/ms-marco-MiniLM-L-6-v2)
        Here: use a richer embedding similarity + keyword overlap combo.
        This approximates cross-encoder behavior without needing a second model.
        """
        # Embedding similarity (from sentence-transformers)
        q_vec = embed_texts([query])[0]
        c_vec = embed_texts([chunk])[0]
        cosine = float(np.dot(q_vec, c_vec) / (np.linalg.norm(q_vec) * np.linalg.norm(c_vec) + 1e-8))

        # Keyword overlap bonus (BM25-inspired)
        query_words = set(re.sub(r'[^a-z0-9 ]', '', query.lower()).split())
        chunk_words = set(re.sub(r'[^a-z0-9 ]', '', chunk.lower()).split())
        overlap = len(query_words & chunk_words)
        keyword_bonus = min(overlap * 0.03, 0.15)

        # Proximity bonus: query words appearing close together in chunk
        proximity = 0.0
        for word in query_words:
            if len(word) > 3 and word in chunk.lower():
                proximity += 0.02

        return min(cosine + keyword_bonus + proximity, 1.0)

    def retrieve(self, query: str, top_k: int = 3) -> List[Document]:
        if self.index is None or not self.chunks:
            return []

        # ── STAGE 1: Fast vector search (top N) ─────────
        k1 = min(self.first_stage_k, len(self.chunks))
        q_vec = embed_texts([query]).astype("float32")
        distances, indices = self.index.search(q_vec, k1)

        stage1_candidates = [
            (int(idx), float(dist))
            for idx, dist in zip(indices[0], distances[0])
        ]

        # ── STAGE 2: Precise reranking ───────────────────
        reranked = []
        for idx, _ in stage1_candidates:
            score = self._rerank_score(query, self.chunks[idx])
            reranked.append((idx, score))

        # Sort by rerank score, take top_k
        reranked.sort(key=lambda x: x[1], reverse=True)
        final = reranked[:top_k]

        return [
            Document(
                content=self.chunks[idx],
                score=round(score, 3),
                source=self.sources[idx],
                chunk_index=idx,
                retrieval_method=f"reranked (from top-{k1})",
            )
            for idx, score in final
        ]

    def ask(self, query: str, top_k: int = 3, use_ollama: bool = False) -> RAGResult:
        steps = []
        t0 = time.time()

        k1 = min(self.first_stage_k, len(self.chunks) if self.chunks else 1)
        steps.append({"step": "Stage 1 — Vector Retrieve", "detail": f"Fast search: retrieved top {k1} candidates"})

        docs = self.retrieve(query, top_k)
        retrieval_ms = (time.time() - t0) * 1000

        steps.append({"step": "Stage 2 — Rerank", "detail": f"Precisely re-scored {k1} candidates → kept top {len(docs)}"})
        steps.append({"step": "Top Match", "detail": f"Best score after reranking: {docs[0].score:.3f}" if docs else "No results"})

        t0 = time.time()
        answer = try_ollama_generate(query, docs)[0] if use_ollama else demo_generate(query, docs)
        generation_ms = (time.time() - t0) * 1000
        steps.append({"step": "Generate", "detail": "Answered from reranked context"})

        return RAGResult(
            query=query, answer=answer, retrieved_docs=docs,
            retrieval_ms=round(retrieval_ms, 1), generation_ms=round(generation_ms, 1),
            rag_type=self.name, total_chunks_searched=len(self.chunks), steps=steps,
        )
