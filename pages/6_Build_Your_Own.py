"""
pages/6_Build_Your_Own.py

Complete guide to adding your own RAG type to this project.
Includes: template class, integration steps, testing checklist, real examples.
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st

st.set_page_config(page_title="Build Your Own RAG", page_icon="🛠️", layout="wide")

st.title("🛠️ Build Your Own RAG")
st.markdown("*Add any new RAG architecture to this project in under 30 minutes.*")
st.divider()

tabs = st.tabs(["📐 Template", "🔌 Integration Steps", "💡 5 RAG Ideas to Build", "🧪 Testing Guide", "📚 Real Examples"])

# ── TAB 1: TEMPLATE ────────────────────────────────────────
with tabs[0]:
    st.subheader("📐 RAG Template — Copy and Customize")
    st.markdown("Every RAG type in this project follows the same 3-method interface. Copy this and fill in your logic.")

    st.code('''"""
rag_core/my_custom_rag.py  ── "Your RAG Name" ──

HOW MY CUSTOM RAG WORKS (describe it simply):
─────────────────────────────────────────────
  Explain it to a 14-year-old in 3-5 sentences.
  What problem does it solve?
  How is it different from Naive RAG?

  What it\'s GOOD at:
    ✅ (list 3-4 strengths)

  What it\'s BAD at:
    ❌ (list 2-3 weaknesses)
─────────────────────────────────────────────
"""

import time
from typing import List
import numpy as np
import faiss

# Always import from .base and .utils
from .base import BaseRAG, Document, RAGResult
from .utils import chunk_text, embed_texts, demo_generate, try_ollama_generate


class MyCustomRAG(BaseRAG):
    """
    One-line description of your RAG type.
    """

    # REQUIRED: Set these 4 class attributes
    name = "My Custom RAG"           # shown in dropdown
    description = "What it does"     # shown in UI
    emoji = "🆕"                      # shown next to name
    color = "#FF6B6B"                # hex color for UI styling

    def __init__(self, chunk_size: int = 300, overlap: int = 50):
        """
        Add any parameters your RAG needs.
        Always call super().__init__() if you extend BaseRAG.
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.chunks: List[str] = []
        self.sources: List[str] = []
        self.index = None
        # Add your custom state here:
        # self.my_custom_index = None
        # self.settings = ...

    def add_documents(self, texts: List[str], source: str = "document") -> int:
        """
        REQUIRED: Store documents and build search index.

        Must:
        - Split texts into chunks
        - Build searchable index (FAISS, BM25, or custom)
        - Store chunks + sources for retrieval

        Returns: number of chunks created
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

        # Step 2: Embed (use shared embed_texts function!)
        embeddings = embed_texts(self.chunks).astype("float32")

        # Step 3: Build FAISS index (or your custom index)
        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(embeddings)

        # Step 4: Your custom processing (if any)
        # self._build_custom_index(self.chunks)

        return len(self.chunks)

    def retrieve(self, query: str, top_k: int = 3) -> List[Document]:
        """
        REQUIRED: Find relevant chunks for a query.

        Must return a list of Document objects.
        Each Document has: content, score (0-1), source, chunk_index, retrieval_method
        """
        if self.index is None or not self.chunks:
            return []

        # Standard vector retrieval (customize this!)
        query_vec = embed_texts([query]).astype("float32")
        actual_k = min(top_k, len(self.chunks))
        distances, indices = self.index.search(query_vec, actual_k)

        # YOUR CUSTOM LOGIC GOES HERE
        # Examples:
        # - Add custom reranking
        # - Apply filters (by source, date, category)
        # - Combine with other search methods
        # - Verify/validate results

        results = []
        for idx, dist in zip(indices[0], distances[0]):
            # Convert L2 distance to similarity score (0 to 1)
            score = float(1 / (1 + dist))

            results.append(Document(
                content=self.chunks[idx],
                score=round(score, 3),
                source=self.sources[idx],
                chunk_index=int(idx),
                retrieval_method="my_custom_method",  # describe YOUR method
            ))

        return results

    def ask(self, query: str, top_k: int = 3, use_ollama: bool = False) -> RAGResult:
        """
        REQUIRED: Full pipeline — retrieve + generate.

        The steps[] list is shown in the UI as a step-by-step log.
        Always return a RAGResult object.
        """
        steps = []
        t0 = time.time()

        # Log step 1
        steps.append({"step": "My Step 1", "detail": "Describe what\'s happening..."})

        # Retrieve
        docs = self.retrieve(query, top_k)
        retrieval_ms = (time.time() - t0) * 1000

        # Log step 2
        steps.append({"step": "Retrieved", "detail": f"Found {len(docs)} relevant chunks"})

        # Generate
        t0 = time.time()
        if use_ollama:
            answer, _ = try_ollama_generate(query, docs)
        else:
            answer = demo_generate(query, docs)
        generation_ms = (time.time() - t0) * 1000

        steps.append({"step": "Generated", "detail": "Answer created from context"})

        # Return RAGResult (required format for UI to work)
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
''', language="python")

    st.info("💡 **Tip:** The `steps` list is what gets shown in the pipeline log in the UI. Add a step for every meaningful action your RAG takes. This is great for debugging and teaching!")

# ── TAB 2: INTEGRATION STEPS ──────────────────────────────
with tabs[1]:
    st.subheader("🔌 Integration Steps — Add to App in 5 Steps")

    steps_data = [
        ("Step 1", "Create your RAG file", "rag_core/",
         "Save your RAG class as `rag_core/my_rag.py`\nFollow the template exactly — same 3 methods.",
         "touch rag_core/my_rag.py"),
        ("Step 2", "Export from __init__.py", "rag_core/__init__.py",
         "Add your class to the package so the UI can find it.",
         '''# Add to rag_core/__init__.py:
from .my_rag import MyCustomRAG

ALL_RAG_TYPES["🆕 My Custom RAG"] = MyCustomRAG

RAG_META["🆕 My Custom RAG"] = {
    "color": "#FF6B6B",
    "complexity": "⭐⭐ Medium",
    "speed": "⚡⚡",
}'''),
        ("Step 3", "Add pipeline diagram", "rag_diagrams/pipeline.py",
         "Add a visual diagram so users can see how your RAG works.",
         '''# Add to rag_diagrams/pipeline.py:
def diagram_my_rag() -> str:
    content = _row(
        _box("Query", "❓", "#FF6B6B"),
        _arrow(),
        _box("My Step", "🔧", "#FF6B6B", "What it does"),
        _arrow(),
        _box("Answer", "💬", "#10B981"),
    )
    return _wrap(content, "🆕 My Custom RAG", "Your subtitle here")

# Register in DIAGRAM_MAP:
DIAGRAM_MAP["My Custom RAG"] = diagram_my_rag'''),
        ("Step 4", "Add to Encyclopedia", "pages/5_RAG_Encyclopedia.py",
         "Document your RAG for users to learn from.",
         '''# Add to ENCYCLOPEDIA list in 5_RAG_Encyclopedia.py:
{
    "name": "My Custom RAG",
    "emoji": "🆕",
    "tagline": "What it does",
    "complexity": "⭐⭐ Medium",
    "speed": "⚡⚡",
    "color": "#FF6B6B",
    "introduced": "Year — Author",
    "theory": "...",
    "use_when": "...",
    "avoid_when": "...",
    "code": "...",
    "interview_q": "...",
    "interview_a": "...",
}'''),
        ("Step 5", "Test your RAG", "Terminal",
         "Run the test script to verify everything works.",
         '''python3 -c "
from rag_core import MyCustomRAG

rag = MyCustomRAG()
n = rag.add_documents([\'Your test document here...\'])
print(f\'Indexed {n} chunks\')

result = rag.ask(\'Test question?\')
print(f\'Answer: {result.answer}\')
print(f\'Docs: {len(result.retrieved_docs)}\')
print(f\'Time: {result.total_ms:.1f}ms\')
"'''),
    ]

    for step_num, step_name, location, description, code in steps_data:
        with st.expander(f"**{step_num}: {step_name}** `{location}`"):
            st.markdown(description)
            st.code(code, language="python")
            st.success(f"✅ After this step: {step_name} is complete")

# ── TAB 3: RAG IDEAS ──────────────────────────────────────
with tabs[2]:
    st.subheader("💡 5 RAG Types You Can Build Next")
    st.markdown("*Each idea has a starter code snippet to get you going.*")

    ideas = [
        {
            "title": "📊 Time-Aware RAG",
            "difficulty": "⭐⭐ Medium",
            "idea": """Retrieve recent documents first. Documents have timestamps.
Retrieval score = relevance_score * recency_weight where recency_weight decays over time.
Perfect for: News, stock data, documentation updates.""",
            "starter": '''class TimeAwareRAG(BaseRAG):
    name = "Time-Aware RAG"

    def add_documents(self, texts, source="doc", timestamps=None):
        """Store with timestamps for recency weighting."""
        self.timestamps = timestamps or [time.time()] * len(texts)
        # ... normal add_documents logic ...

    def _recency_score(self, chunk_idx: int) -> float:
        """More recent = higher score. Decays over time."""
        age_days = (time.time() - self.timestamps[chunk_idx]) / 86400
        return 1.0 / (1.0 + age_days / 30)  # decay over 30 days

    def retrieve(self, query, top_k=3):
        docs = super().retrieve(query, top_k * 3)  # over-retrieve
        # Combine vector score + recency score
        for doc in docs:
            recency = self._recency_score(doc.chunk_index)
            doc.score = 0.7 * doc.score + 0.3 * recency
        docs.sort(key=lambda d: d.score, reverse=True)
        return docs[:top_k]''',
        },
        {
            "title": "📁 Source-Filtered RAG",
            "difficulty": "⭐ Simple",
            "idea": """Add source-based filtering to any RAG type.
Users can say "Only search the HR policy documents" or "Only search PDFs from 2024".
Perfect for: Enterprise KB where users have department-specific access.""",
            "starter": '''class FilteredRAG(NaiveRAG):
    name = "Source-Filtered RAG"

    def retrieve(self, query, top_k=3, allowed_sources=None):
        """Filter by source before returning results."""
        # Get more than needed (some will be filtered)
        docs = super().retrieve(query, top_k * 5)

        if allowed_sources:
            docs = [d for d in docs if d.source in allowed_sources]

        return docs[:top_k]

# Usage:
rag.add_documents(hr_docs, source="HR")
rag.add_documents(it_docs, source="IT")

# Only search IT docs:
result = rag.retrieve("VPN setup", allowed_sources=["IT"])''',
        },
        {
            "title": "🌐 Web-Augmented RAG",
            "difficulty": "⭐⭐⭐ Hard",
            "idea": """When local docs don't have the answer, fall back to web search.
Combines local retrieval + live internet search.
Perfect for: News, real-time data, topics not in your KB.""",
            "starter": '''import requests

class WebAugmentedRAG(HybridRAG):
    name = "Web-Augmented RAG"

    def _web_search(self, query: str, n: int = 3) -> List[Document]:
        """Call a free search API (e.g. DuckDuckGo instant answers)."""
        try:
            resp = requests.get(
                "https://api.duckduckgo.com/",
                params={"q": query, "format": "json", "no_html": 1},
                timeout=5
            )
            data = resp.json()
            results = []
            for r in data.get("RelatedTopics", [])[:n]:
                if "Text" in r:
                    results.append(Document(
                        content=r["Text"],
                        score=0.6,
                        source="web",
                        retrieval_method="web_search"
                    ))
            return results
        except Exception:
            return []

    def retrieve(self, query, top_k=3):
        local_docs = super().retrieve(query, top_k)
        top_local_score = local_docs[0].score if local_docs else 0

        if top_local_score < 0.4:  # local docs not relevant enough
            web_docs = self._web_search(query, 2)
            return (local_docs + web_docs)[:top_k]
        return local_docs''',
        },
        {
            "title": "🧮 Structured Data RAG",
            "difficulty": "⭐⭐ Medium",
            "idea": """Query CSV/Excel/SQL databases with natural language.
Convert NL query → SQL → execute → return as context.
Perfect for: Business analytics, financial data, product catalogs.""",
            "starter": '''import sqlite3, pandas as pd

class StructuredRAG(BaseRAG):
    name = "Structured Data RAG"

    def add_documents(self, csv_paths, source="table"):
        """Load CSVs into SQLite for querying."""
        self.conn = sqlite3.connect(":memory:")
        for path in csv_paths:
            df = pd.read_csv(path)
            table_name = os.path.basename(path).replace(".csv", "")
            df.to_sql(table_name, self.conn)
        # Also create text chunks for semantic search
        # ...

    def _nl_to_sql(self, query: str) -> str:
        """Simple heuristic NL → SQL (use LLM in production)."""
        # Pattern matching for common queries
        if "total" in query.lower() or "sum" in query.lower():
            return "SELECT SUM(revenue) FROM sales"
        elif "count" in query.lower():
            return "SELECT COUNT(*) FROM products"
        return "SELECT * FROM data LIMIT 5"

    def retrieve(self, query, top_k=3):
        sql = self._nl_to_sql(query)
        df = pd.read_sql(sql, self.conn)
        result_text = df.to_string()
        return [Document(content=result_text, score=0.9,
                         source="structured_db", retrieval_method="sql")]''',
        },
        {
            "title": "🖼️ Multimodal RAG",
            "difficulty": "⭐⭐⭐ Hard",
            "idea": """Index and retrieve both text AND images.
Use CLIP embeddings (text+image shared vector space) for cross-modal retrieval.
Query with text → find relevant images. Query with image → find relevant text.
Perfect for: Product catalog, medical imaging, document search.""",
            "starter": '''# Requires: pip install transformers pillow
from transformers import CLIPProcessor, CLIPModel
from PIL import Image

class MultimodalRAG(NaiveRAG):
    name = "Multimodal RAG"

    def __init__(self):
        super().__init__()
        self.clip = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        self.image_chunks = []
        self.image_embeddings = []

    def add_images(self, image_paths: list):
        """Embed images and add to index."""
        for path in image_paths:
            image = Image.open(path)
            inputs = self.processor(images=image, return_tensors="pt")
            img_emb = self.clip.get_image_features(**inputs).detach().numpy()
            self.image_chunks.append({"path": path, "type": "image"})
            self.image_embeddings.append(img_emb)
            # Add to FAISS index alongside text embeddings

    def retrieve(self, query, top_k=3):
        # Get text query embedding via CLIP
        inputs = self.processor(text=[query], return_tensors="pt", padding=True)
        q_emb = self.clip.get_text_features(**inputs).detach().numpy()
        # Search across both text AND image embeddings
        # Return mixed results...''',
        },
    ]

    for idea in ideas:
        with st.expander(f"{idea['title']}  `{idea['difficulty']}`"):
            st.markdown(idea['idea'])
            st.code(idea['starter'], language="python")
            st.info("💡 Copy this starter code into `rag_core/`, then follow the 5 integration steps on the previous tab!")

# ── TAB 4: TESTING GUIDE ──────────────────────────────────
with tabs[3]:
    st.subheader("🧪 Testing Checklist for Your RAG")

    st.markdown("Before adding your RAG to the app, run through this checklist:")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
**Basic functionality:**
- [ ] `add_documents()` runs without errors
- [ ] Returns correct number of chunks
- [ ] `retrieve()` returns Document objects with valid scores
- [ ] Scores are between 0 and 1
- [ ] `ask()` returns a RAGResult with answer

**Edge cases:**
- [ ] Empty document list → handles gracefully
- [ ] Empty query → handles gracefully
- [ ] Query with no relevant docs → returns answer with low scores
- [ ] Very long document (10KB+) → doesn't crash
- [ ] Unicode characters → handled correctly
        """)
    with col2:
        st.markdown("""
**Quality checks:**
- [ ] Relevant query → top doc score > 0.5
- [ ] Irrelevant query → top doc score < 0.3
- [ ] Steps list is populated (for UI log)
- [ ] RAGResult.rag_type equals your class's `name`
- [ ] Pipeline log has 3+ meaningful steps

**Performance:**
- [ ] `add_documents()` for 10 docs < 10 seconds
- [ ] `ask()` for simple query < 5 seconds
- [ ] Memory usage reasonable (no leaks on repeated calls)
        """)

    st.code("""
# Automated test script — save as tests/test_my_rag.py

import pytest
from rag_core.my_rag import MyCustomRAG

SAMPLE_DOCS = [
    "Einstein was born in 1879 in Germany.",
    "Tesla was an inventor famous for AC electricity.",
    "Newton discovered gravity by watching an apple fall.",
]

@pytest.fixture
def rag():
    rag = MyCustomRAG()
    n = rag.add_documents(SAMPLE_DOCS)
    assert n > 0, "Should create at least 1 chunk"
    return rag

def test_retrieve_returns_documents(rag):
    docs = rag.retrieve("When was Einstein born?")
    assert len(docs) > 0
    assert all(0 <= d.score <= 1 for d in docs)

def test_relevant_query_high_score(rag):
    docs = rag.retrieve("Einstein born year Germany")
    assert docs[0].score > 0.3, "Relevant query should get score > 0.3"

def test_ask_returns_ragresult(rag):
    result = rag.ask("Who was Einstein?")
    assert result.answer
    assert result.retrieved_docs
    assert result.rag_type == MyCustomRAG.name
    assert result.retrieval_ms >= 0
    assert len(result.steps) >= 2

def test_empty_docs_handled():
    rag = MyCustomRAG()
    rag.add_documents([])
    result = rag.ask("Any question")
    assert result  # should not crash

# Run: pytest tests/test_my_rag.py -v
""", language="python")

# ── TAB 5: REAL EXAMPLES ──────────────────────────────────
with tabs[4]:
    st.subheader("📚 Learning from Existing Implementations")
    st.markdown("Study these patterns from the existing RAG types in this project:")

    examples = {
        "Pattern 1: Simple two-index RAG (Hybrid)": """
# From hybrid_rag.py — two indexes, RRF fusion
class HybridRAG(BaseRAG):
    def add_documents(self, texts, source="doc"):
        # Build BOTH BM25 and FAISS
        tokenized = [chunk.lower().split() for chunk in all_chunks]
        self.bm25 = BM25Okapi(tokenized)

        embeddings = embed_texts(all_chunks).astype("float32")
        self.faiss_index = faiss.IndexFlatL2(dim)
        self.faiss_index.add(embeddings)

    def retrieve(self, query, top_k=3):
        # BM25 search
        bm25_scores = self.bm25.get_scores(query.lower().split())
        bm25_ranked = np.argsort(bm25_scores)[::-1][:k]

        # Vector search
        query_vec = embed_texts([query]).astype("float32")
        _, vector_ranked = self.faiss_index.search(query_vec, k)

        # RRF Fusion
        rrf_scores = {}
        for rank, idx in enumerate(bm25_ranked):
            rrf_scores[idx] = rrf_scores.get(idx, 0) + 1.0/(60 + rank)
        for rank, idx in enumerate(vector_ranked[0]):
            rrf_scores[idx] = rrf_scores.get(idx, 0) + 1.0/(60 + rank)
""",
        "Pattern 2: Decision loop with retry (Self-Reflective)": """
# From self_reflective_rag.py — retry with query expansion
def ask(self, query, top_k=3):
    current_query = query
    for attempt in range(self.max_retries + 1):
        docs = self._vector_retrieve(current_query, top_k)
        is_relevant, score, msg = self._reflect_on_relevance(query, docs)

        if is_relevant or attempt == self.max_retries:
            break  # good enough or last attempt

        # Expand query for next attempt
        current_query = self._expand_query(query, attempt + 1)
""",
        "Pattern 3: Multi-stage with chain (Multi-hop)": """
# From multihop_rag.py — hop 1 → extract → hop 2
def retrieve(self, query, top_k=3):
    all_docs = []

    # Hop 1
    hop1_docs = self._basic_retrieve(query, 2)
    all_docs.extend(hop1_docs)

    # Extract key entities from hop 1 results
    hop1_text = " ".join(d.content for d in hop1_docs)
    entities = self._extract_entities(hop1_text)

    if entities:
        # Hop 2: use extracted entity
        hop2_query = f"{query} {entities[0]}"
        hop2_docs = self._basic_retrieve(hop2_query, 2)
        all_docs.extend(hop2_docs)  # add new unique docs

    return sorted(all_docs, key=lambda d: d.score, reverse=True)[:top_k]
""",
        "Pattern 4: Post-processing chunks (Contextual)": """
# From contextual_rag.py — compress after retrieval
def retrieve(self, query, top_k=3):
    # First: standard retrieval
    docs = self._vector_retrieve(query, top_k)

    # Then: compress each chunk (keep only relevant sentences)
    for doc in docs:
        original = doc.content
        compressed = self._compress_chunk(query, original)
        doc.content = compressed  # replace with compressed version
        doc.retrieval_method = f"compressed ({len(compressed)/len(original):.0%} kept)"

    return docs
""",
    }

    for pattern_name, code in examples.items():
        with st.expander(f"**{pattern_name}**"):
            st.code(code, language="python")

    st.divider()
    st.info("""
📌 **Key principles for all RAG implementations in this project:**

1. **Always use `embed_texts()`** from `utils.py` — it's cached, shared, fast
2. **Always use `chunk_text()`** from `utils.py` — consistent chunking across all types
3. **Always use `demo_generate()`** as fallback — works without LLM
4. **Always populate `steps[]`** — this is what makes the UI educational
5. **Always set `name`, `emoji`, `color`** — required for UI to render correctly
6. **Return `RAGResult`** with all fields filled — required by comparison page
    """)

with st.sidebar:
    st.markdown("## 🗺️ Navigation")
    st.page_link("app.py", label="🏠 Home")
    st.page_link("pages/1_When_To_Use_RAG.py", label="1️⃣ When to Use RAG")
    st.page_link("pages/2_How_RAG_Works.py", label="2️⃣ How RAG Works")
    st.page_link("pages/3_Test_Any_RAG.py", label="3️⃣ Test Any RAG ⭐")
    st.page_link("pages/4_Compare_RAGs.py", label="4️⃣ Compare RAG Types")
    st.page_link("pages/5_RAG_Encyclopedia.py", label="5️⃣ Encyclopedia 📖")
    st.page_link("pages/6_Build_Your_Own.py", label="6️⃣ Build Your Own 🛠️")
