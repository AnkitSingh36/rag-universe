"""
rag_core/adaptive_rag.py  ── "The Smart Router RAG" ──

HOW ADAPTIVE RAG WORKS:
─────────────────────────────────────────────────────────
  Not all questions need the same RAG approach!

  "What year?" → Simple question → Naive RAG (fast)
  "TSLA earnings vs Apple revenue?" → Keyword + semantic → Hybrid RAG
  "Explain how Einstein's work influenced modern physics?" → Complex → Rerank RAG

  Adaptive RAG classifies the query, then routes to the RIGHT RAG type.
  Think of it as a smart traffic controller.

  Why this matters:
    - Don't use a slow, expensive Rerank RAG for a simple question
    - Don't use Naive RAG for a complex multi-concept question
    - Match complexity of retrieval to complexity of question

  Classification criteria:
    SIMPLE:  Short query, 1-2 concepts, factual lookup
    KEYWORD: Contains names, codes, numbers → use Hybrid
    COMPLEX: Long query, multiple concepts, comparisons → use Rerank

  What it's GOOD at:
    ✅ Best answer quality for each query type
    ✅ Cost optimization (simple queries → cheap RAG)
    ✅ Production systems with mixed query types

  What it's BAD at:
    ❌ Classification can be wrong
    ❌ More moving parts to maintain
─────────────────────────────────────────────────────────
"""

import re
import time
from typing import List, Tuple
import numpy as np

from .base import BaseRAG, Document, RAGResult
from .naive_rag import NaiveRAG
from .hybrid_rag import HybridRAG
from .rerank_rag import RerankRAG
from .utils import chunk_text


class AdaptiveRAG(BaseRAG):
    """
    Adaptive RAG: routes each query to the best RAG type automatically.
    """

    name = "Adaptive RAG"
    description = "Classifies each query (simple/keyword/complex) and routes to the best RAG type automatically."
    emoji = "🔀"
    color = "#EC4899"

    def __init__(self, chunk_size: int = 300, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap
        # Initialize all sub-RAGs (they share the same documents)
        self.naive = NaiveRAG(chunk_size, overlap)
        self.hybrid = HybridRAG(chunk_size, overlap)
        self.rerank = RerankRAG(chunk_size, overlap)
        self._last_route = None
        self._last_reason = ""

    def add_documents(self, texts: List[str], source: str = "document") -> int:
        """Load documents into all three underlying RAG types."""
        n = self.naive.add_documents(texts, source)
        self.hybrid.add_documents(texts, source)
        self.rerank.add_documents(texts, source)
        return n

    def _classify_query(self, query: str) -> Tuple[str, str]:
        """
        Classify the query into: SIMPLE / KEYWORD / COMPLEX

        Returns: (route_to, reason)
        """
        query_stripped = query.strip()
        words = query_stripped.split()
        word_count = len(words)

        # --- Rule 1: Detect keywords (names, codes, numbers, uppercase acronyms)
        has_uppercase_word = bool(re.search(r'\b[A-Z]{2,6}\b', query_stripped))
        has_number = bool(re.search(r'\b\d+\b', query_stripped))
        has_name = bool(re.search(r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b', query_stripped))  # "Neil Armstrong"

        if has_uppercase_word or has_number or has_name:
            return "HYBRID", f"Query contains keywords/codes/names ({query_stripped[:30]}...)"

        # --- Rule 2: Complex = long query with multiple concepts
        complex_keywords = {'compare', 'contrast', 'difference', 'relationship', 'impact', 'influence',
                            'explain how', 'why did', 'what caused', 'analyze', 'both', 'and', 'versus', 'vs'}
        query_lower = query.lower()
        has_complex_keyword = any(kw in query_lower for kw in complex_keywords)

        if word_count > 10 or has_complex_keyword:
            return "RERANK", f"Complex query ({word_count} words, complex patterns detected)"

        # --- Rule 3: Simple = short factual question
        if word_count <= 6:
            return "NAIVE", f"Simple query ({word_count} words, factual lookup)"

        # Default: hybrid (safe middle ground)
        return "HYBRID", f"Medium complexity ({word_count} words) → defaulting to Hybrid"

    def retrieve(self, query: str, top_k: int = 3) -> List[Document]:
        route, reason = self._classify_query(query)
        self._last_route = route
        self._last_reason = reason

        if route == "NAIVE":
            return self.naive.retrieve(query, top_k)
        elif route == "HYBRID":
            return self.hybrid.retrieve(query, top_k)
        else:  # RERANK
            return self.rerank.retrieve(query, top_k)

    def ask(self, query: str, top_k: int = 3, use_ollama: bool = False) -> RAGResult:
        route, reason = self._classify_query(query)

        steps = [
            {"step": "Classify Query", "detail": f"Route: {route} — {reason}"},
            {"step": f"Route → {route} RAG", "detail": f"Using {route} RAG for this query type"},
        ]

        t0 = time.time()

        if route == "NAIVE":
            result = self.naive.ask(query, top_k, use_ollama)
            used_rag = "Naive RAG"
        elif route == "HYBRID":
            result = self.hybrid.ask(query, top_k, use_ollama)
            used_rag = "Hybrid RAG"
        else:
            result = self.rerank.ask(query, top_k, use_ollama)
            used_rag = "Rerank RAG"

        total_ms = (time.time() - t0) * 1000
        steps.extend(result.steps)
        steps.append({"step": "Done", "detail": f"Answered using {used_rag} (classified as {route})"})

        # Prepend routing info to answer
        answer = f"*[Adaptive routing: Used {used_rag} for this query]*\n\n{result.answer}"

        return RAGResult(
            query=query, answer=answer, retrieved_docs=result.retrieved_docs,
            retrieval_ms=round(result.retrieval_ms, 1), generation_ms=round(result.generation_ms, 1),
            rag_type=f"Adaptive RAG → {used_rag}",
            total_chunks_searched=result.total_chunks_searched,
            steps=steps,
        )
