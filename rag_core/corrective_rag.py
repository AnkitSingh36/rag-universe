"""
rag_core/corrective_rag.py  ── "The Fact-Checker RAG" ──

CORRECTIVE RAG (CRAG):
─────────────────────────────────────────────────────────
  CRAG adds a correction step: after generating an answer,
  it checks if the answer is actually supported by retrieved docs.
  If not → it corrects the answer or flags uncertainty.

  Paper: "Corrective Retrieval Augmented Generation" (Yan et al., 2024)

  Pipeline:
    Retrieve → Generate → Evaluate docs relevance:
      - CORRECT (relevant): Use docs → confident answer
      - INCORRECT (irrelevant): Fall back, add uncertainty flag
      - AMBIGUOUS (partial): Use partial docs + flag uncertainty
─────────────────────────────────────────────────────────
"""

import re
import time
from typing import List, Tuple
import numpy as np
import faiss

from .base import BaseRAG, Document, RAGResult
from .utils import chunk_text, embed_texts, demo_generate, try_ollama_generate


class CorrectiveRAG(BaseRAG):
    name = "Corrective RAG"
    description = "Evaluates if retrieved docs actually answer the question. Flags low-confidence answers. Reduces hallucination."
    emoji = "✅"
    color = "#10B981"

    def __init__(self, chunk_size: int = 300, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap
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
        self.index = faiss.IndexFlatL2(embs.shape[1])
        self.index.add(embs)
        return len(self.chunks)

    def _evaluate_retrieval(self, query: str, docs: List[Document]) -> Tuple[str, float]:
        """
        Classify retrieval quality as: CORRECT / AMBIGUOUS / INCORRECT

        Returns: (classification, confidence)
        """
        if not docs:
            return "INCORRECT", 0.0

        top_score = docs[0].score
        avg_score = sum(d.score for d in docs) / len(docs)

        # Check if query keywords appear in docs
        query_words = set(re.sub(r'[^a-z0-9 ]', '', query.lower()).split())
        query_words = {w for w in query_words if len(w) > 3}
        all_doc_text = " ".join(d.content for d in docs).lower()
        kw_matches = sum(1 for w in query_words if w in all_doc_text)
        kw_ratio = kw_matches / max(len(query_words), 1)

        # Combined score
        combined = (top_score * 0.6) + (kw_ratio * 0.4)

        if combined > 0.55:
            return "CORRECT", combined
        elif combined > 0.30:
            return "AMBIGUOUS", combined
        else:
            return "INCORRECT", combined

    def retrieve(self, query: str, top_k: int = 3) -> List[Document]:
        if self.index is None:
            return []
        q_vec = embed_texts([query]).astype("float32")
        actual_k = min(top_k, len(self.chunks))
        distances, indices = self.index.search(q_vec, actual_k)
        return [
            Document(
                content=self.chunks[idx],
                score=round(float(1 / (1 + dist)), 3),
                source=self.sources[idx],
                chunk_index=int(idx),
                retrieval_method="corrective",
            )
            for idx, dist in zip(indices[0], distances[0])
        ]

    def ask(self, query: str, top_k: int = 3, use_ollama: bool = False) -> RAGResult:
        steps = []
        t0 = time.time()
        docs = self.retrieve(query, top_k)
        retrieval_ms = (time.time() - t0) * 1000

        # Evaluate
        classification, confidence = self._evaluate_retrieval(query, docs)
        steps.append({"step": "Retrieve", "detail": f"Got {len(docs)} chunks from docs"})
        steps.append({"step": "Evaluate", "detail": f"Retrieval quality: {classification} (score: {confidence:.2f})"})

        t0 = time.time()
        raw_answer = try_ollama_generate(query, docs)[0] if use_ollama else demo_generate(query, docs)
        generation_ms = (time.time() - t0) * 1000

        # Correct based on evaluation
        if classification == "CORRECT":
            answer = raw_answer
            steps.append({"step": "Correct", "detail": "✅ Docs are relevant — using answer confidently"})
        elif classification == "AMBIGUOUS":
            answer = f"{raw_answer}\n\n⚠️ *Note: Retrieved documents partially match your question. Answer may be incomplete.*"
            steps.append({"step": "Correct", "detail": "⚠️ Partial match — flagged uncertainty in answer"})
        else:
            answer = (
                "⚠️ The documents I have may not contain the answer to this specific question.\n\n"
                f"Best available information:\n{raw_answer}\n\n"
                "*Low confidence — consider checking another source.*"
            )
            steps.append({"step": "Correct", "detail": "❌ Docs likely irrelevant — answer flagged as low confidence"})

        return RAGResult(
            query=query, answer=answer, retrieved_docs=docs,
            retrieval_ms=round(retrieval_ms, 1), generation_ms=round(generation_ms, 1),
            rag_type=self.name, total_chunks_searched=len(self.chunks),
            steps=steps, confidence_score=confidence,
        )
