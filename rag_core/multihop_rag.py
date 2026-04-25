"""
rag_core/multihop_rag.py  ── "The Chain-of-Thought RAG" ──

HOW MULTI-HOP RAG WORKS:
─────────────────────────────────────────────────────────
  Some questions need multiple steps to answer:

  "Who invented the telescope and what did they discover with it?"
    Hop 1: Find "who invented telescope" → Galileo
    Hop 2: Find "what did Galileo discover" → moons of Jupiter
    Synthesis: Combine both answers

  This is like a detective connecting clues:
    Clue 1 → leads to → Clue 2 → leads to → Answer

  Why not just ask everything at once?
    Because a single query can't express "first find X, then use X to find Y"
    Multi-hop makes these implicit dependencies explicit.

  What it's GOOD at:
    ✅ "Who is the CEO of the company that makes X?"
    ✅ "What happened after event A that caused event B?"
    ✅ Research questions requiring multiple fact lookups
    ✅ Knowledge graph-style reasoning

  What it's BAD at:
    ❌ Much slower (multiple retrieval rounds)
    ❌ Error propagation (mistake in hop 1 → wrong hop 2)
    ❌ Simple questions (overkill)
─────────────────────────────────────────────────────────
"""

import re
import time
from typing import List, Tuple
import numpy as np
import faiss

from .base import BaseRAG, Document, RAGResult
from .utils import chunk_text, embed_texts, demo_generate, try_ollama_generate


class MultiHopRAG(BaseRAG):
    name = "Multi-Hop RAG"
    description = "Chains multiple retrievals. Finds Entity 1 → uses Entity 1 to find Entity 2 → synthesizes answer."
    emoji = "🔗"
    color = "#F97316"

    def __init__(self, chunk_size: int = 300, overlap: int = 50, max_hops: int = 2):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.max_hops = max_hops
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

    def _basic_retrieve(self, query: str, top_k: int = 2) -> List[Document]:
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
                retrieval_method="multi_hop",
            )
            for idx, dist in zip(indices[0], distances[0])
        ]

    def _extract_entities(self, text: str) -> List[str]:
        """
        Extract key entities (nouns, names) from text for the next hop.
        Simple heuristic: find capitalized words and common noun phrases.
        """
        # Find proper nouns (capitalized words not at sentence start)
        entities = re.findall(r'(?<=[a-z] )[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*', text)

        # Find years and numbers (often useful for next hop)
        years = re.findall(r'\b(1[0-9]{3}|20[0-9]{2})\b', text)
        entities.extend(years)

        # Deduplicate, keep max 3
        seen = set()
        unique = []
        for e in entities:
            if e not in seen and len(e) > 2:
                seen.add(e)
                unique.append(e)

        return unique[:3]

    def _decompose_query(self, query: str) -> List[str]:
        """
        Decompose a multi-part question into sub-queries.

        Simple heuristic: split on 'and', 'also', 'additionally', common conjunctions.
        """
        # Check for multi-part questions
        connectors = [r'\band\b', r'\balso\b', r'\badditionally\b', r'\bwhat about\b']
        for conn in connectors:
            parts = re.split(conn, query, flags=re.IGNORECASE, maxsplit=1)
            if len(parts) == 2:
                p1 = parts[0].strip()
                p2 = parts[1].strip()
                if len(p1) > 5 and len(p2) > 5:
                    return [p1, p2]

        # If can't split: just return the original as single query
        return [query]

    def retrieve(self, query: str, top_k: int = 3) -> List[Document]:
        """Multi-hop retrieval: hop 1 → extract → hop 2 → merge."""
        all_docs = []

        # Hop 1: retrieve for original query
        hop1_docs = self._basic_retrieve(query, 2)
        all_docs.extend(hop1_docs)

        if hop1_docs and self.max_hops > 1:
            # Extract entities from hop 1 results
            hop1_text = " ".join(d.content for d in hop1_docs)
            entities = self._extract_entities(hop1_text)

            if entities:
                # Hop 2: retrieve for extracted entity + original query
                hop2_query = f"{query} {entities[0]}"
                hop2_docs = self._basic_retrieve(hop2_query, 2)

                # Add hop 2 docs if not already in results
                existing_indices = {d.chunk_index for d in all_docs}
                for doc in hop2_docs:
                    if doc.chunk_index not in existing_indices:
                        doc.retrieval_method = f"hop_2 (via '{entities[0]}')"
                        all_docs.append(doc)

        # Sort by score, return top_k
        all_docs.sort(key=lambda d: d.score, reverse=True)
        return all_docs[:top_k]

    def ask(self, query: str, top_k: int = 3, use_ollama: bool = False) -> RAGResult:
        steps = []
        t0 = time.time()

        # Decompose
        sub_queries = self._decompose_query(query)
        if len(sub_queries) > 1:
            steps.append({"step": "Decompose", "detail": f"Multi-part query → {len(sub_queries)} sub-queries"})
        else:
            steps.append({"step": "Decompose", "detail": "Single query (no decomposition needed)"})

        # Hop 1
        hop1_docs = self._basic_retrieve(sub_queries[0], 2)
        steps.append({"step": "Hop 1 Retrieve", "detail": f"Retrieved {len(hop1_docs)} docs for: '{sub_queries[0][:40]}...'"})

        # Extract and Hop 2
        all_docs = list(hop1_docs)
        if hop1_docs and self.max_hops > 1:
            hop1_text = " ".join(d.content for d in hop1_docs)
            entities = self._extract_entities(hop1_text)
            if entities:
                hop2_query = f"{query} {entities[0]}"
                hop2_docs = self._basic_retrieve(hop2_query, 2)
                existing_indices = {d.chunk_index for d in all_docs}
                new_hop2 = [d for d in hop2_docs if d.chunk_index not in existing_indices]
                for doc in new_hop2:
                    doc.retrieval_method = f"hop_2 (via '{entities[0]}')"
                all_docs.extend(new_hop2)
                steps.append({"step": "Hop 2 Retrieve", "detail": f"Used entity '{entities[0]}' for 2nd hop → {len(new_hop2)} new docs"})

        all_docs.sort(key=lambda d: d.score, reverse=True)
        final_docs = all_docs[:top_k]
        retrieval_ms = (time.time() - t0) * 1000

        t0 = time.time()
        answer = try_ollama_generate(query, final_docs)[0] if use_ollama else demo_generate(query, final_docs)
        generation_ms = (time.time() - t0) * 1000
        steps.append({"step": "Synthesize", "detail": f"Combined {len(final_docs)} docs from {self.max_hops} hops"})

        return RAGResult(
            query=query, answer=answer, retrieved_docs=final_docs,
            retrieval_ms=round(retrieval_ms, 1), generation_ms=round(generation_ms, 1),
            rag_type=self.name, total_chunks_searched=len(self.chunks) * self.max_hops,
            steps=steps,
        )
