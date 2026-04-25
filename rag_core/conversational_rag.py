"""
rag_core/conversational_rag.py  ── "The Memory RAG" ──

HOW CONVERSATIONAL RAG WORKS (explain like you're 14 years old):
─────────────────────────────────────────────────────────
  Normal RAG forgets every question you asked.
  Conversational RAG REMEMBERS the whole conversation!

  Imagine texting a very smart friend:
    You:   "Tell me about Einstein"
    Friend: "Einstein was a physicist who..."

    You:   "When was he born?"        ← "he" refers to Einstein!
    Friend: (without memory) "Who is 'he'? 🤷"
    Friend: (WITH memory) "Einstein was born in 1879!" ✅

  How it remembers:
    - Every question + answer gets stored in 'chat history'
    - When you ask something new, it searches BOTH:
        • The documents (for facts)
        • The chat history (for context)
    - Combines everything to answer

  What it's GOOD at:
    ✅ Multi-turn conversations ("What about his wife?")
    ✅ Follow-up questions
    ✅ Customer support chatbots
    ✅ Research assistants

  What it's BAD at:
    ❌ Context window fills up (too many messages = confusion)
    ❌ More complex state to manage
    ❌ Each question is slower (more to search)
─────────────────────────────────────────────────────────
"""

import time
from typing import List, Dict

import numpy as np
import faiss

from .base import BaseRAG, Document, RAGResult
from .utils import chunk_text, embed_texts, demo_generate, try_ollama_generate


class ConversationalRAG(BaseRAG):
    """
    Conversational RAG: remembers conversation history and uses it as context.

    Storage:
      - self.chunks         → document chunks (your knowledge base)
      - self.history        → past Q&A turns (conversation memory)
      - self.doc_index      → FAISS index for documents
      - self.history_index  → FAISS index for past messages
    """

    name = "Conversational RAG"
    description = "Remembers the whole conversation. Great for follow-up questions and multi-turn chat."
    emoji = "🟢"
    color = "#10B981"

    def __init__(self, chunk_size: int = 300, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.chunks: List[str] = []
        self.sources: List[str] = []
        self.history: List[Dict[str, str]] = []  # [{"q": "...", "a": "..."}]
        self.doc_index = None
        self.history_index = None
        self._history_embeddings: List[np.ndarray] = []

    def add_documents(self, texts: List[str], source: str = "document") -> int:
        """Store documents and reset conversation history."""
        self.chunks = []
        self.sources = []
        self.history = []
        self._history_embeddings = []
        self.history_index = None

        for text in texts:
            new_chunks = chunk_text(text, self.chunk_size, self.overlap)
            self.chunks.extend(new_chunks)
            self.sources.extend([source] * len(new_chunks))

        if not self.chunks:
            return 0

        embeddings = embed_texts(self.chunks).astype("float32")
        dim = embeddings.shape[1]
        self.doc_index = faiss.IndexFlatL2(dim)
        self.doc_index.add(embeddings)

        return len(self.chunks)

    def retrieve(self, query: str, top_k: int = 3) -> List[Document]:
        """
        Retrieve from BOTH documents AND conversation history.
        Returns up to top_k doc chunks + up to 2 relevant history turns.
        """
        if self.doc_index is None:
            return []

        query_vec = embed_texts([query])
        results: List[Document] = []

        # ── Search documents ─────────────────────────
        k_docs = min(top_k, len(self.chunks))
        distances, indices = self.doc_index.search(query_vec, k_docs)

        for idx, dist in zip(indices[0], distances[0]):
            results.append(Document(
                content=self.chunks[idx],
                score=round(float(1 / (1 + dist)), 3),
                source=self.sources[idx],
                chunk_index=int(idx),
                retrieval_method="document",
            ))

        # ── Search conversation history ──────────────
        if self.history_index is not None and len(self.history) > 0:
            k_hist = min(2, len(self.history))
            h_distances, h_indices = self.history_index.search(query_vec, k_hist)

            for idx, dist in zip(h_indices[0], h_distances[0]):
                turn = self.history[idx]
                results.append(Document(
                    content=f"[Previous conversation]\nQ: {turn['q']}\nA: {turn['a']}",
                    score=round(float(1 / (1 + dist)), 3),
                    source="chat_history",
                    chunk_index=idx,
                    retrieval_method="history",
                ))

        # Sort by score
        results.sort(key=lambda d: d.score, reverse=True)
        return results

    def _store_turn(self, query: str, answer: str):
        """Store this Q&A turn in history and update the history index."""
        self.history.append({"q": query, "a": answer})

        # Embed the question for history retrieval
        q_vec = embed_texts([query]).astype("float32")
        self._history_embeddings.append(q_vec)

        # Rebuild the history FAISS index
        all_history = np.vstack(self._history_embeddings)
        dim = all_history.shape[1]
        self.history_index = faiss.IndexFlatL2(dim)
        self.history_index.add(all_history)

    def ask(self, query: str, top_k: int = 3, use_ollama: bool = False) -> RAGResult:
        """Full pipeline: retrieve (docs + history) → generate → store turn."""
        steps = []
        steps.append({
            "step": "Check History",
            "detail": f"Conversation has {len(self.history)} previous turns"
        })

        t0 = time.time()
        docs = self.retrieve(query, top_k)
        retrieval_ms = (time.time() - t0) * 1000

        history_docs = [d for d in docs if d.retrieval_method == "history"]
        doc_docs = [d for d in docs if d.retrieval_method == "document"]

        steps.append({
            "step": "Retrieve",
            "detail": f"Found {len(doc_docs)} document chunks + {len(history_docs)} history turns"
        })

        t0 = time.time()
        if use_ollama:
            answer, _ = try_ollama_generate(query, docs)
        else:
            answer = demo_generate(query, docs)
        generation_ms = (time.time() - t0) * 1000

        steps.append({"step": "Generate Answer", "detail": "Combined docs + history → answer"})

        # Store this turn for future questions
        self._store_turn(query, answer)
        steps.append({"step": "Save to Memory", "detail": f"Stored turn #{len(self.history)} in conversation memory"})

        return RAGResult(
            query=query,
            answer=answer,
            retrieved_docs=docs,
            retrieval_ms=round(retrieval_ms, 1),
            generation_ms=round(generation_ms, 1),
            rag_type=self.name,
            total_chunks_searched=len(self.chunks) + len(self.history),
            steps=steps,
            conversation_history=list(self.history),
        )

    def clear_history(self):
        """Reset the conversation (keep documents)."""
        self.history = []
        self._history_embeddings = []
        self.history_index = None
