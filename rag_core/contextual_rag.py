"""
rag_core/contextual_rag.py  ── "The Efficient RAG" ──

HOW CONTEXTUAL COMPRESSION RAG WORKS:
─────────────────────────────────────────────────────────
  Problem with Naive RAG:
    You retrieve chunk of 300 words. But only 1 sentence in it is relevant.
    You're sending 299 useless words to the LLM — wasting tokens & money!

  Solution:
    After retrieving chunks, COMPRESS them:
    - Remove sentences not relevant to the query
    - Keep only the useful parts
    - Send compressed, focused context to LLM

  Before compression:
    "Einstein was born in Germany. He later moved to USA.
     He married Mileva Marić in 1903. He published the
     Theory of Relativity in 1905. He played violin.
     His cat was named..." ← 60 words, lots of noise

  After compression (query: "When did Einstein publish Relativity?"):
    "He published the Theory of Relativity in 1905." ← 10 words, focused

  Token savings: ~83%! Less cost, better answers.

  What it's GOOD at:
    ✅ Long documents with sparse relevant info
    ✅ Token-budget-constrained deployments
    ✅ Cost optimization
    ✅ Focus — LLM isn't confused by noise

  What it's BAD at:
    ❌ Might discard context that seems unrelated but matters
    ❌ Extra processing step
    ❌ Short docs (not worth compressing)
─────────────────────────────────────────────────────────
"""

import re
import time
from typing import List
import numpy as np
import faiss

from .base import BaseRAG, Document, RAGResult
from .utils import chunk_text, embed_texts, demo_generate, try_ollama_generate


class ContextualRAG(BaseRAG):
    """
    Contextual Compression RAG:
      1. Retrieve chunks (same as Naive RAG)
      2. Compress each chunk — keep only relevant sentences
      3. Send compressed context to LLM
    """

    name = "Contextual RAG"
    description = "Retrieves chunks then compresses them — keeps only sentences relevant to your query. Saves tokens."
    emoji = "🟡"
    color = "#EAB308"

    def __init__(self, chunk_size: int = 400, overlap: int = 60,
                 compression_threshold: float = 0.15):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.compression_threshold = compression_threshold
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
        return len(self.chunks)

    def _compress_chunk(self, query: str, chunk: str) -> str:
        """
        Remove sentences from chunk that are NOT relevant to the query.

        Method:
        - Split chunk into sentences
        - Embed each sentence + query
        - Keep sentences with cosine similarity > threshold
        - Return the kept sentences joined

        Returns compressed chunk (might be shorter or same as original).
        """
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', chunk) if len(s.strip()) > 10]
        if len(sentences) <= 2:
            return chunk  # too short to compress

        # Embed query + all sentences
        all_texts = [query] + sentences
        all_embs = embed_texts(all_texts)

        q_vec = all_embs[0]
        s_vecs = all_embs[1:]

        # Cosine similarity of each sentence to query
        q_norm = q_vec / (np.linalg.norm(q_vec) + 1e-8)
        relevant_sentences = []
        scores = []

        for sent, svec in zip(sentences, s_vecs):
            s_norm = svec / (np.linalg.norm(svec) + 1e-8)
            sim = float(np.dot(q_norm, s_norm))
            scores.append(sim)
            if sim > self.compression_threshold:
                relevant_sentences.append(sent)

        # Always keep at least 1 sentence (the best one)
        if not relevant_sentences:
            best_idx = int(np.argmax(scores))
            relevant_sentences = [sentences[best_idx]]

        return " ".join(relevant_sentences)

    def retrieve(self, query: str, top_k: int = 3) -> List[Document]:
        if self.index is None or not self.chunks:
            return []

        # Stage 1: Vector retrieval
        q_vec = embed_texts([query]).astype("float32")
        actual_k = min(top_k, len(self.chunks))
        distances, indices = self.index.search(q_vec, actual_k)

        docs = []
        for idx, dist in zip(indices[0], distances[0]):
            original = self.chunks[idx]
            compressed = self._compress_chunk(query, original)

            compression_ratio = len(compressed) / max(len(original), 1)

            docs.append(Document(
                content=compressed,
                score=round(float(1 / (1 + dist)), 3),
                source=self.sources[idx],
                chunk_index=int(idx),
                retrieval_method=f"compressed ({compression_ratio:.0%} kept)",
            ))

        return docs

    def ask(self, query: str, top_k: int = 3, use_ollama: bool = False) -> RAGResult:
        steps = []
        t0 = time.time()

        # For step logging, also get pre-compression sizes
        if self.index is not None and self.chunks:
            q_vec = embed_texts([query]).astype("float32")
            actual_k = min(top_k, len(self.chunks))
            distances, indices = self.index.search(q_vec, actual_k)
            pre_sizes = [len(self.chunks[i]) for i in indices[0]]
        else:
            pre_sizes = []

        steps.append({"step": "Retrieve", "detail": f"Vector search: found top {top_k} chunks"})

        docs = self.retrieve(query, top_k)
        retrieval_ms = (time.time() - t0) * 1000

        post_sizes = [len(d.content) for d in docs]
        if pre_sizes and post_sizes:
            avg_before = sum(pre_sizes) / len(pre_sizes)
            avg_after = sum(post_sizes) / len(post_sizes)
            saved = int((1 - avg_after / max(avg_before, 1)) * 100)
            steps.append({
                "step": "Compress",
                "detail": f"Removed irrelevant sentences. Avg chars: {avg_before:.0f} → {avg_after:.0f} ({saved}% saved)"
            })

        t0 = time.time()
        answer = try_ollama_generate(query, docs)[0] if use_ollama else demo_generate(query, docs)
        generation_ms = (time.time() - t0) * 1000
        steps.append({"step": "Generate", "detail": "Answered from compressed, focused context"})

        return RAGResult(
            query=query, answer=answer, retrieved_docs=docs,
            retrieval_ms=round(retrieval_ms, 1), generation_ms=round(generation_ms, 1),
            rag_type=self.name, total_chunks_searched=len(self.chunks), steps=steps,
        )
