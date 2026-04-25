"""
rag_core/base.py

The building blocks that every RAG type uses.
Think of this like a recipe template — each RAG type fills in the steps differently.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import time


# ─────────────────────────────────────────────
# A Document = one piece of knowledge your RAG knows about
# ─────────────────────────────────────────────
@dataclass
class Document:
    """
    One chunk of text retrieved from your knowledge base.

    Example:
        content = "The Apollo 11 mission landed on the moon in 1969."
        score   = 0.92  (how relevant it is to the question)
        source  = "space_facts.txt"
    """
    content: str
    score: float = 0.0          # relevance score (0 = useless, 1 = perfect match)
    source: str = "unknown"     # where this text came from
    chunk_index: int = 0        # which chunk number this is
    retrieval_method: str = "vector"   # "vector", "bm25", or "hybrid"


# ─────────────────────────────────────────────
# A RAGResult = everything that happened when you asked a question
# (used for visualization in the UI)
# ─────────────────────────────────────────────
@dataclass
class RAGResult:
    """
    Everything RAG did to answer your question.
    We store all the steps so we can SHOW the user what happened.
    """
    query: str                              # the question asked
    answer: str                             # the final answer
    retrieved_docs: List[Document]          # which chunks it found
    retrieval_ms: float = 0.0              # how long retrieval took
    generation_ms: float = 0.0            # how long generation took
    rag_type: str = "Naive RAG"           # which RAG type was used
    total_chunks_searched: int = 0        # how many chunks existed
    steps: List[Dict[str, Any]] = field(default_factory=list)  # step-by-step log
    conversation_history: List[Dict] = field(default_factory=list)  # for conversational
    confidence_score: float = 0.0  # used by SelfReflectiveRAG and CorrectiveRAG

    @property
    def total_ms(self):
        return self.retrieval_ms + self.generation_ms

    @property
    def top_doc(self) -> Optional[Document]:
        return self.retrieved_docs[0] if self.retrieved_docs else None


# ─────────────────────────────────────────────
# BaseRAG = the template all RAG types follow
# ─────────────────────────────────────────────
class BaseRAG:
    """
    Every RAG type has the same 3 steps:
      1. add_documents() → store your knowledge
      2. retrieve()      → find relevant chunks
      3. ask()           → get an answer

    Subclasses override retrieve() to use different search strategies.
    """

    name: str = "Base RAG"
    description: str = "Abstract base"
    emoji: str = "📚"

    def add_documents(self, texts: List[str], source: str = "user_input") -> int:
        """Store documents. Returns how many chunks were created."""
        raise NotImplementedError

    def retrieve(self, query: str, top_k: int = 3) -> List[Document]:
        """Find the most relevant chunks for a query."""
        raise NotImplementedError

    def ask(self, query: str, top_k: int = 3) -> RAGResult:
        """Full pipeline: retrieve + generate. Returns RAGResult."""
        raise NotImplementedError
