"""
rag_core/naive_rag.py  ── "The Simple RAG" ──

HOW NAIVE RAG WORKS (explain like you're 14 years old):
─────────────────────────────────────────────────────────
  Imagine you have a big box of index cards, each with a fact written on it.

  When someone asks you a question:
    1. You turn the question into a "meaning fingerprint" (embedding)
    2. You compare that fingerprint to every index card's fingerprint
    3. You grab the 3 cards most similar in meaning
    4. You read those 3 cards and answer the question

  That's Naive RAG! ✅

  What it's GOOD at:
    ✅ Simple questions about any topic
    ✅ Finding text that MEANS the same thing as your question
    ✅ Fast (milliseconds)
    ✅ Easy to understand

  What it's BAD at:
    ❌ Finding EXACT keyword matches (searching "NASA" might miss "ISRO")
    ❌ Multi-step questions ("who is the CEO of the company that made X?")
    ❌ Remembering what you asked before
─────────────────────────────────────────────────────────
"""

import time
from typing import List

import numpy as np
import faiss

from .base import BaseRAG, Document, RAGResult
from .utils import chunk_text, embed_texts, demo_generate, try_ollama_generate


class NaiveRAG(BaseRAG):
    """
    Naive RAG: embed everything → vector search → answer.

    The SIMPLEST form of RAG. Perfect starting point for learning.
    """

    name = "Naive RAG"
    description = "Pure semantic search. Converts everything to meaning-vectors and finds what's most similar."
    emoji = "🔵"
    color = "#3B82F6"

    def __init__(self, chunk_size: int = 300, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.chunks: List[str] = []
        self.sources: List[str] = []
        self.index = None          # FAISS vector index
        self.embeddings = None     # stored embeddings

    def add_documents(self, texts: List[str], source: str = "document") -> int:
        """
        Store documents in the vector index.

        What happens here:
          1. Split each document into chunks (e.g., 300 chars each)
          2. Turn each chunk into a vector (384 numbers)
          3. Store all vectors in FAISS for fast searching
        """
        self.chunks = []
        self.sources = []

        # Step 1: Chunk all documents
        for text in texts:
            new_chunks = chunk_text(text, self.chunk_size, self.overlap)
            self.chunks.extend(new_chunks)
            self.sources.extend([source] * len(new_chunks))

        if not self.chunks:
            return 0

        # Step 2: Embed all chunks → shape (N, 384)
        self.embeddings = embed_texts(self.chunks)

        # Step 3: Build FAISS index for fast vector search
        dim = self.embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dim)   # L2 distance (Euclidean)
        self.index.add(self.embeddings)

        return len(self.chunks)

    def retrieve(self, query: str, top_k: int = 3) -> List[Document]:
        """
        Find the most relevant chunks for the query.

        What happens here:
          1. Embed the query into a vector (same 384 numbers)
          2. FAISS searches all stored vectors for closest ones
          3. Return the matching text chunks with scores
        """
        if self.index is None or not self.chunks:
            return []

        # Embed the query
        query_vec = embed_texts([query])

        # Search FAISS (returns distances and indices)
        actual_k = min(top_k, len(self.chunks))
        distances, indices = self.index.search(query_vec, actual_k)

        # Convert L2 distances → similarity scores (0 to 1, higher is better)
        docs = []
        for rank, (idx, dist) in enumerate(zip(indices[0], distances[0])):
            similarity = float(1 / (1 + dist))  # convert distance to similarity
            docs.append(Document(
                content=self.chunks[idx],
                score=round(similarity, 3),
                source=self.sources[idx],
                chunk_index=int(idx),
                retrieval_method="vector_search",
            ))

        return docs

    def ask(self, query: str, top_k: int = 3, use_ollama: bool = False) -> RAGResult:
        """
        Full pipeline: retrieve relevant chunks → generate an answer.
        """
        steps = []

        # ── STEP 1: Retrieval ──────────────────────
        t0 = time.time()
        steps.append({"step": "Embed Query", "detail": f"Converting '{query[:50]}...' into a 384-dim vector"})

        docs = self.retrieve(query, top_k)
        retrieval_ms = (time.time() - t0) * 1000

        steps.append({
            "step": "Vector Search",
            "detail": f"Searched {len(self.chunks)} chunks, found top {len(docs)} matches"
        })
        steps.append({
            "step": "Retrieved Chunks",
            "detail": f"Top match score: {docs[0].score:.2f}" if docs else "No matches found"
        })

        # ── STEP 2: Generation ─────────────────────
        t0 = time.time()
        if use_ollama:
            answer, used_ollama = try_ollama_generate(query, docs)
        else:
            answer = demo_generate(query, docs)
            used_ollama = False

        generation_ms = (time.time() - t0) * 1000
        steps.append({"step": "Generate Answer", "detail": f"Used {'Ollama LLM' if used_ollama else 'Demo Mode'}"})

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
