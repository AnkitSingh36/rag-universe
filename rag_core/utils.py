"""
rag_core/utils.py

Shared tools used by every RAG type:
  - chunk_text()      → split a long document into small pieces
  - get_embedder()    → load the embedding model (cached, loads once)
  - demo_generate()   → create an answer WITHOUT a real LLM (works offline!)
  - try_ollama()      → use Ollama if it's installed (optional upgrade)
"""

import re
import time
import requests
from typing import List, Tuple, Optional

import numpy as np

# Lazy import — only loaded once the first time
_embedder = None


# ─────────────────────────────────────────────
# STEP 1: Chunking
# Split long text into smaller pieces so retrieval is precise
# ─────────────────────────────────────────────
def chunk_text(text: str, chunk_size: int = 200, overlap: int = 40) -> List[str]:
    """
    Split text into overlapping chunks.

    Why overlap? So sentences that span a chunk boundary aren't lost.

    Example:
        chunk_size = 200 chars
        overlap    = 40 chars
        text       = "AAAA...BBBB...CCCC..."
        chunks     = ["AAAA...first 200", "...last40+next200", ...]

    Args:
        text:       The document to chunk
        chunk_size: How many characters per chunk (≈50 words)
        overlap:    How many characters to share between chunks

    Returns:
        List of text chunks
    """
    text = text.strip()
    if not text:
        return []

    # Try to split on sentences first (more natural)
    sentences = re.split(r'(?<=[.!?])\s+', text)

    chunks = []
    current = ""

    for sentence in sentences:
        # If adding this sentence fits, add it
        if len(current) + len(sentence) <= chunk_size:
            current += " " + sentence if current else sentence
        else:
            # Save current chunk
            if current:
                chunks.append(current.strip())
            # Start new chunk (with overlap from previous)
            overlap_text = current[-overlap:] if len(current) > overlap else current
            current = overlap_text + " " + sentence if overlap_text else sentence

    if current.strip():
        chunks.append(current.strip())

    return [c for c in chunks if len(c) > 10]  # remove tiny fragments


# ─────────────────────────────────────────────
# STEP 2: Embedding Model
# Converts text into numbers (vectors) that capture meaning
# ─────────────────────────────────────────────
def get_embedder():
    """
    Load the sentence embedding model. Cached globally (loads only once).

    This model turns text into a list of numbers.
    Similar text → similar numbers → nearby in vector space.

    Model: all-MiniLM-L6-v2
      - Size: 22MB (small!)
      - Speed: ~1000 sentences/second
      - Quality: Good enough for learning and many production apps
    """
    global _embedder
    if _embedder is None:
        from sentence_transformers import SentenceTransformer
        _embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return _embedder


def embed_texts(texts: List[str]) -> np.ndarray:
    """
    Convert a list of text strings into embedding vectors.

    Returns:
        numpy array of shape (N, 384) — one 384-dimensional vector per text
    """
    embedder = get_embedder()
    return embedder.encode(texts, convert_to_numpy=True, show_progress_bar=False).astype("float32")


# ─────────────────────────────────────────────
# STEP 3: Generation (Answer Creation)
# Two options:
#   A. Demo mode  → works offline, no LLM needed
#   B. Ollama     → real LLM, optional
# ─────────────────────────────────────────────
def demo_generate(query: str, docs: List["Document"]) -> str:  # type: ignore
    """
    Create an answer WITHOUT a real LLM.

    How it works:
      1. Look at the retrieved chunks
      2. Find the sentence most relevant to the query
      3. Format it as a human-friendly answer

    This is 'extractive QA' — we extract the answer from the docs
    instead of generating new text. Good for demos and learning!

    Returns:
        A formatted answer string
    """
    if not docs:
        return "❌ I couldn't find any relevant information in the documents for your question."

    # Score each sentence against the query (word overlap heuristic)
    query_words = set(re.sub(r'[^a-z0-9 ]', '', query.lower()).split())

    best_sentences = []

    for doc in docs[:3]:  # only look at top 3 retrieved chunks
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', doc.content) if len(s.strip()) > 15]
        for sent in sentences:
            sent_words = set(re.sub(r'[^a-z0-9 ]', '', sent.lower()).split())
            overlap = len(query_words & sent_words)
            if overlap > 0:
                best_sentences.append((overlap, sent))

    best_sentences.sort(key=lambda x: x[0], reverse=True)

    if best_sentences:
        # Take best 1-2 sentences
        answer_parts = [s for _, s in best_sentences[:2]]
        answer = " ".join(answer_parts)
        return (
            f"**Based on the retrieved documents:**\n\n{answer}\n\n"
            f"*💡 Demo mode — connect Ollama for richer AI-generated answers*"
        )
    else:
        # Just return the top retrieved chunk summary
        top_content = docs[0].content[:200]
        return (
            f"**Based on the retrieved documents:**\n\n{top_content}...\n\n"
            f"*💡 Demo mode — connect Ollama for richer AI-generated answers*"
        )


def try_ollama_generate(query: str, docs: List["Document"], model: str = "mistral") -> Tuple[str, bool]:  # type: ignore
    """
    Try to generate an answer using a local Ollama LLM.

    Returns:
        (answer_text, success_bool)
        If Ollama is not running, falls back to demo_generate().
    """
    context = "\n\n".join([f"[{i+1}] {doc.content}" for i, doc in enumerate(docs)])

    prompt = f"""You are a helpful assistant. Answer the question based ONLY on the context provided.
If the context doesn't contain the answer, say "I don't have that information."

Context:
{context}

Question: {query}

Answer:"""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=30,
        )
        if response.status_code == 200:
            return response.json().get("response", ""), True
    except Exception:
        pass

    # Fallback to demo mode
    return demo_generate(query, docs), False


def check_ollama_running() -> bool:
    """Check if Ollama is available."""
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=2)
        return r.status_code == 200
    except Exception:
        return False
