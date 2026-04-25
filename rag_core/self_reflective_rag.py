"""
rag_core/self_reflective_rag.py  ── "The Self-Aware RAG" ──

HOW SELF-REFLECTIVE RAG (SELF-RAG) WORKS:
─────────────────────────────────────────────────────────
  Naive RAG always retrieves and always answers. It never thinks:
  "Is what I retrieved actually relevant? Is my answer good?"

  Self-Reflective RAG adds introspection:
    Step 1: Decide — "Do I even NEED to retrieve? Maybe I know this already"
    Step 2: Retrieve docs
    Step 3: Reflect — "Are these docs relevant to my question?"
    Step 4: If NOT relevant: re-retrieve with different query
    Step 5: Answer
    Step 6: Grade answer — "Is my answer supported by the docs? Am I hallucinating?"

  Paper: "SELF-RAG: Learning to Retrieve, Generate, and Critique through
  Self-Reflection" (Asai et al., 2023)

  What it's GOOD at:
    ✅ High reliability (self-checks before answering)
    ✅ Knows when NOT to use retrieval (saves tokens)
    ✅ Detects and reduces hallucinations
    ✅ Medical, legal, financial use cases

  What it's BAD at:
    ❌ Slower (extra reflection steps)
    ❌ More complex to implement
    ❌ In real SELF-RAG: needs fine-tuned LLM with special tokens
─────────────────────────────────────────────────────────
"""

import re
import time
from typing import List, Tuple
import numpy as np
import faiss

from .base import BaseRAG, Document, RAGResult
from .utils import chunk_text, embed_texts, demo_generate, try_ollama_generate


class SelfReflectiveRAG(BaseRAG):
    """
    Self-Reflective RAG: retrieve → reflect on quality → re-retrieve if needed → answer → grade.
    """

    name = "Self-Reflective RAG"
    description = "Reflects on retrieval quality. Re-retrieves if docs are irrelevant. Grades its own answer."
    emoji = "🔮"
    color = "#6366F1"

    def __init__(self, chunk_size: int = 300, overlap: int = 50,
                 relevance_threshold: float = 0.45, max_retries: int = 2):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.relevance_threshold = relevance_threshold
        self.max_retries = max_retries
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

    def _vector_retrieve(self, query: str, top_k: int = 3) -> List[Document]:
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
                retrieval_method="self_reflective",
            )
            for idx, dist in zip(indices[0], distances[0])
        ]

    def _reflect_on_relevance(self, query: str, docs: List[Document]) -> Tuple[bool, float, str]:
        """
        Reflection step 1: Are these docs actually relevant?

        Returns: (is_relevant, avg_score, feedback_message)
        """
        if not docs:
            return False, 0.0, "No documents retrieved"

        avg_score = sum(d.score for d in docs) / len(docs)
        top_score = docs[0].score if docs else 0.0

        if top_score >= self.relevance_threshold:
            return True, avg_score, f"✅ Docs are relevant (top score: {top_score:.2f} ≥ {self.relevance_threshold})"
        else:
            return False, avg_score, f"⚠️ Docs may be irrelevant (top score: {top_score:.2f} < {self.relevance_threshold})"

    def _expand_query(self, query: str, attempt: int) -> str:
        """Generate an alternative query for re-retrieval."""
        query_words = query.strip().split()

        strategies = [
            # Strategy 1: Remove question words, focus on nouns
            " ".join([w for w in query_words if w.lower() not in
                      {'who', 'what', 'when', 'where', 'how', 'why', 'is', 'are', 'was', 'were', 'does', 'did'}]),
            # Strategy 2: Just the last N significant words
            " ".join(query_words[-3:]) if len(query_words) > 3 else query,
        ]

        idx = min(attempt - 1, len(strategies) - 1)
        expanded = strategies[idx]
        return expanded if expanded.strip() else query

    def _grade_answer(self, answer: str, docs: List[Document]) -> Tuple[float, str]:
        """
        Reflection step 2: Is the answer grounded in the docs?
        Returns: (confidence_score, grade_message)
        """
        if not docs or not answer:
            return 0.0, "Cannot grade: no docs or answer"

        all_doc_text = " ".join(d.content for d in docs).lower()
        answer_words = set(re.sub(r'[^a-z0-9 ]', '', answer.lower()).split())
        doc_words = set(re.sub(r'[^a-z0-9 ]', '', all_doc_text).split())

        # What fraction of answer words appear in docs?
        significant_words = {w for w in answer_words if len(w) > 4}
        if not significant_words:
            return 0.5, "⚠️ Answer too short to grade"

        overlap = len(significant_words & doc_words)
        grounding = overlap / len(significant_words)

        if grounding > 0.6:
            return grounding, f"✅ Well-grounded ({grounding:.0%} of answer terms found in docs)"
        elif grounding > 0.3:
            return grounding, f"⚠️ Partially grounded ({grounding:.0%} — may have some hallucination)"
        else:
            return grounding, f"❌ Poorly grounded ({grounding:.0%} — high hallucination risk)"

    def retrieve(self, query: str, top_k: int = 3) -> List[Document]:
        """Retrieve with reflection and retry logic."""
        current_query = query
        best_docs = []
        best_score = 0.0

        for attempt in range(self.max_retries + 1):
            docs = self._vector_retrieve(current_query, top_k)
            is_relevant, avg_score, _ = self._reflect_on_relevance(query, docs)

            if avg_score > best_score:
                best_score = avg_score
                best_docs = docs

            if is_relevant or attempt == self.max_retries:
                break

            # Expand query for next attempt
            current_query = self._expand_query(query, attempt + 1)

        return best_docs

    def ask(self, query: str, top_k: int = 3, use_ollama: bool = False) -> RAGResult:
        steps = []
        t0 = time.time()

        steps.append({"step": "Decide", "detail": "Should I retrieve? → Yes, query needs external docs"})

        current_query = query
        final_docs = []
        total_attempts = 0

        for attempt in range(self.max_retries + 1):
            total_attempts += 1
            docs = self._vector_retrieve(current_query, top_k)
            is_relevant, avg_score, feedback = self._reflect_on_relevance(query, docs)

            steps.append({
                "step": f"Retrieve (attempt {attempt + 1})",
                "detail": f"Query: '{current_query[:50]}...' | {feedback}"
            })

            if is_relevant or attempt == self.max_retries:
                final_docs = docs
                break

            new_query = self._expand_query(query, attempt + 1)
            steps.append({
                "step": "Reflect → Expand Query",
                "detail": f"Docs not relevant enough. Trying: '{new_query}'"
            })
            current_query = new_query

        retrieval_ms = (time.time() - t0) * 1000

        t0 = time.time()
        answer = try_ollama_generate(query, final_docs)[0] if use_ollama else demo_generate(query, final_docs)
        generation_ms = (time.time() - t0) * 1000

        # Grade the answer
        confidence, grade_msg = self._grade_answer(answer, final_docs)
        steps.append({"step": "Grade Answer", "detail": grade_msg})

        # Append confidence to answer
        answer = f"{answer}\n\n*Self-evaluation: {grade_msg}*"

        return RAGResult(
            query=query, answer=answer, retrieved_docs=final_docs,
            retrieval_ms=round(retrieval_ms, 1), generation_ms=round(generation_ms, 1),
            rag_type=self.name, total_chunks_searched=len(self.chunks) * total_attempts,
            steps=steps, confidence_score=confidence,
        )
