"""
pages/6_Build_Your_Own.py
Complete guide to adding your own RAG type to this project.
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from ui_styles import apply_global_styles, sidebar_nav

st.set_page_config(page_title="Build Your Own RAG", page_icon="🛠️", layout="wide")
apply_global_styles()

# ── PAGE HEADER ───────────────────────────────────────────────
st.markdown("""
<div style="padding:1.5rem 0 0.5rem">
  <div class="sec-label">Page 6 of 6</div>
  <h1 style="font-size:2rem;font-weight:800;color:#F0F4FF;margin:0.3rem 0;letter-spacing:-0.02em">
    🛠️ Build Your Own RAG
  </h1>
  <p style="color:#8892A4;font-size:0.95rem;margin:0">
    Add any new RAG architecture to this project in under 30 minutes.
  </p>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="fancy-div"></div>', unsafe_allow_html=True)

tabs = st.tabs([
    "📐 Template",
    "🔌 Integration Steps",
    "💡 5 RAG Ideas",
    "🧪 Testing Guide",
    "📚 Real Examples",
])

# ── TAB 1: TEMPLATE ───────────────────────────────────────────
with tabs[0]:
    st.markdown("""
<div class="sec-head" style="margin-top:0">
  <div class="sec-label">Starter Template</div>
  <div class="sec-title">📐 Copy This Template — Fill in Your Logic</div>
</div>
<p style="color:#94a3b8;font-size:0.9rem;margin-bottom:1rem">
  Every RAG type follows the same 3-method interface. Copy and customize.
</p>
""", unsafe_allow_html=True)

    st.code('''"""
rag_core/my_custom_rag.py  ── "Your RAG Name" ──

HOW MY CUSTOM RAG WORKS:
─────────────────────────────────────────────
  Explain it simply: What problem does it solve?
  How is it different from Naive RAG?

  Strengths:  ✅ (list 3-4)
  Weaknesses: ❌ (list 2-3)
─────────────────────────────────────────────
"""

import time
from typing import List
import numpy as np
import faiss

from .base import BaseRAG, Document, RAGResult
from .utils import chunk_text, embed_texts, demo_generate, try_ollama_generate


class MyCustomRAG(BaseRAG):
    # REQUIRED: Set these 4 class attributes
    name = "My Custom RAG"
    description = "What it does"
    emoji = "🆕"
    color = "#FF6B6B"

    def __init__(self, chunk_size: int = 300, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.chunks: List[str] = []
        self.sources: List[str] = []
        self.index = None

    def add_documents(self, texts: List[str], source: str = "document") -> int:
        """REQUIRED: Store documents and build search index."""
        self.chunks = []
        self.sources = []

        for text in texts:
            new_chunks = chunk_text(text, self.chunk_size, self.overlap)
            self.chunks.extend(new_chunks)
            self.sources.extend([source] * len(new_chunks))

        if not self.chunks:
            return 0

        embeddings = embed_texts(self.chunks).astype("float32")
        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(embeddings)

        # YOUR CUSTOM PROCESSING (if any)
        # self._build_custom_index(self.chunks)

        return len(self.chunks)

    def retrieve(self, query: str, top_k: int = 3) -> List[Document]:
        """REQUIRED: Find relevant chunks for a query."""
        if self.index is None or not self.chunks:
            return []

        query_vec = embed_texts([query]).astype("float32")
        actual_k = min(top_k, len(self.chunks))
        distances, indices = self.index.search(query_vec, actual_k)

        # YOUR CUSTOM LOGIC GOES HERE
        # Examples: custom reranking, source filters, validation...

        results = []
        for idx, dist in zip(indices[0], distances[0]):
            score = float(1 / (1 + dist))
            results.append(Document(
                content=self.chunks[idx],
                score=round(score, 3),
                source=self.sources[idx],
                chunk_index=int(idx),
                retrieval_method="my_custom_method",
            ))

        return results

    def ask(self, query: str, top_k: int = 3, use_ollama: bool = False) -> RAGResult:
        """REQUIRED: Full pipeline — retrieve + generate."""
        steps = []
        t0 = time.time()

        steps.append({"step": "My Step 1", "detail": "Describe what\'s happening…"})

        docs = self.retrieve(query, top_k)
        retrieval_ms = (time.time() - t0) * 1000

        steps.append({"step": "Retrieved", "detail": f"Found {len(docs)} relevant chunks"})

        t0 = time.time()
        if use_ollama:
            answer, _ = try_ollama_generate(query, docs)
        else:
            answer = demo_generate(query, docs)
        generation_ms = (time.time() - t0) * 1000

        steps.append({"step": "Generated", "detail": "Answer created from context"})

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

    st.info("💡 **Tip:** The `steps` list is shown in the pipeline log in the UI. Add a step for every meaningful action — great for debugging and teaching!")

# ── TAB 2: INTEGRATION ────────────────────────────────────────
with tabs[1]:
    st.markdown("""
<div class="sec-head" style="margin-top:0">
  <div class="sec-label">Step-by-Step</div>
  <div class="sec-title">🔌 Add to App in 5 Steps</div>
</div>
""", unsafe_allow_html=True)

    steps_data = [
        ("1", "Create your RAG file", "rag_core/",
         "Save your RAG class as `rag_core/my_rag.py`. Follow the template — same 3 methods.",
         "touch rag_core/my_rag.py"),
        ("2", "Export from __init__.py", "rag_core/__init__.py",
         "Add your class to the package so the UI can find it.",
         '''# Add to rag_core/__init__.py:
from .my_rag import MyCustomRAG

ALL_RAG_TYPES["🆕 My Custom RAG"] = MyCustomRAG

RAG_META["🆕 My Custom RAG"] = {
    "color": "#FF6B6B",
    "complexity": "⭐⭐ Medium",
    "speed": "⚡⚡",
}'''),
        ("3", "Add pipeline diagram", "rag_diagrams/pipeline.py",
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

DIAGRAM_MAP["My Custom RAG"] = diagram_my_rag'''),
        ("4", "Add to Encyclopedia", "pages/5_RAG_Encyclopedia.py",
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
        ("5", "Test your RAG", "Terminal",
         "Run the test script to verify everything works correctly.",
         '''python3 -c "
from rag_core import MyCustomRAG

rag = MyCustomRAG()
n = rag.add_documents([\'Your test document here...\'])
print(f\'Indexed {n} chunks\')

result = rag.ask(\'Test question?\')
print(f\'Answer: {result.answer}\')
print(f\'Docs: {len(result.retrieved_docs)}\')
print(f\'Time: {result.retrieval_ms:.1f}ms\')
"'''),
    ]

    for step_num, step_name, location, description, code in steps_data:
        with st.expander(f"Step {step_num}: {step_name}   `{location}`"):
            col_desc, col_code = st.columns([1, 1], gap="medium")
            with col_desc:
                st.markdown(f"""
<div class="g-card" style="height:100%">
  <div style="font-size:0.75rem;font-weight:700;color:#6366f1;text-transform:uppercase;
       letter-spacing:0.08em;margin-bottom:0.5rem">What to do</div>
  <p style="color:#c7d2fe;font-size:0.9rem;line-height:1.6">{description}</p>
</div>
""", unsafe_allow_html=True)
            with col_code:
                st.code(code, language="python" if "python" not in code.lower() and "from" in code else "python")
            st.success(f"✅ After this step: **{step_name}** is complete")

# ── TAB 3: IDEAS ──────────────────────────────────────────────
with tabs[2]:
    st.markdown("""
<div class="sec-head" style="margin-top:0">
  <div class="sec-label">Inspiration</div>
  <div class="sec-title">💡 5 RAG Types You Can Build Next</div>
</div>
""", unsafe_allow_html=True)

    ideas = [
        {
            "title": "📊 Time-Aware RAG", "difficulty": "⭐⭐ Medium",
            "idea": "Prioritize recent documents. Score = `relevance × recency_weight`. Perfect for news, stock data, documentation updates.",
            "starter": '''class TimeAwareRAG(BaseRAG):
    name = "Time-Aware RAG"

    def add_documents(self, texts, source="doc", timestamps=None):
        self.timestamps = timestamps or [time.time()] * len(texts)
        # ... normal add_documents logic ...

    def _recency_score(self, chunk_idx: int) -> float:
        age_days = (time.time() - self.timestamps[chunk_idx]) / 86400
        return 1.0 / (1.0 + age_days / 30)  # decays over 30 days

    def retrieve(self, query, top_k=3):
        docs = super().retrieve(query, top_k * 3)  # over-retrieve
        for doc in docs:
            recency = self._recency_score(doc.chunk_index)
            doc.score = 0.7 * doc.score + 0.3 * recency
        docs.sort(key=lambda d: d.score, reverse=True)
        return docs[:top_k]''',
        },
        {
            "title": "📁 Source-Filtered RAG", "difficulty": "⭐ Simple",
            "idea": "Add source-based filtering. Users can say 'Only search HR policy documents'. Perfect for enterprise KB with department-specific access.",
            "starter": '''class FilteredRAG(NaiveRAG):
    name = "Source-Filtered RAG"

    def retrieve(self, query, top_k=3, allowed_sources=None):
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
            "title": "🌐 Web-Augmented RAG", "difficulty": "⭐⭐⭐ Hard",
            "idea": "When local docs don't have the answer, fall back to web search. Combines local retrieval + live internet.",
            "starter": '''import requests

class WebAugmentedRAG(HybridRAG):
    name = "Web-Augmented RAG"

    def _web_search(self, query: str, n: int = 3) -> List[Document]:
        try:
            resp = requests.get(
                "https://api.duckduckgo.com/",
                params={"q": query, "format": "json", "no_html": 1},
                timeout=5
            )
            results = []
            for r in resp.json().get("RelatedTopics", [])[:n]:
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
        if not local_docs or local_docs[0].score < 0.4:
            web_docs = self._web_search(query, 2)
            return (local_docs + web_docs)[:top_k]
        return local_docs''',
        },
        {
            "title": "🧮 Structured Data RAG", "difficulty": "⭐⭐ Medium",
            "idea": "Query CSV/Excel/SQL databases with natural language. Convert NL → SQL → execute → return as context.",
            "starter": '''import sqlite3, pandas as pd

class StructuredRAG(BaseRAG):
    name = "Structured Data RAG"

    def add_documents(self, csv_paths, source="table"):
        self.conn = sqlite3.connect(":memory:")
        for path in csv_paths:
            df = pd.read_csv(path)
            table_name = os.path.basename(path).replace(".csv", "")
            df.to_sql(table_name, self.conn)

    def _nl_to_sql(self, query: str) -> str:
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
            "title": "🖼️ Multimodal RAG", "difficulty": "⭐⭐⭐ Hard",
            "idea": "Index and retrieve both text AND images using CLIP embeddings (shared vector space). Query with text → find relevant images.",
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

    def add_images(self, image_paths: list):
        for path in image_paths:
            image = Image.open(path)
            inputs = self.processor(images=image, return_tensors="pt")
            img_emb = self.clip.get_image_features(**inputs).detach().numpy()
            self.image_chunks.append({"path": path, "type": "image"})
            # Add to FAISS index alongside text embeddings

    def retrieve(self, query, top_k=3):
        inputs = self.processor(text=[query], return_tensors="pt", padding=True)
        q_emb = self.clip.get_text_features(**inputs).detach().numpy()
        # Search across both text AND image embeddings...''',
        },
    ]

    idea_cols1, idea_cols2 = st.columns(2, gap="medium")

    for i, idea in enumerate(ideas):
        col = idea_cols1 if i % 2 == 0 else idea_cols2
        with col:
            with st.expander(f"{idea['title']}   `{idea['difficulty']}`"):
                st.markdown(f'<p style="color:#94a3b8;font-size:0.88rem;line-height:1.6">{idea["idea"]}</p>', unsafe_allow_html=True)
                st.code(idea["starter"], language="python")
                st.info("💡 Copy this starter code into `rag_core/`, then follow the 5 integration steps!")

# ── TAB 4: TESTING ────────────────────────────────────────────
with tabs[3]:
    st.markdown("""
<div class="sec-head" style="margin-top:0">
  <div class="sec-label">Quality Assurance</div>
  <div class="sec-title">🧪 Testing Checklist for Your RAG</div>
</div>
<p style="color:#94a3b8;font-size:0.9rem;margin-bottom:1rem">
  Before adding your RAG to the app, verify these items.
</p>
""", unsafe_allow_html=True)

    tc1, tc2 = st.columns(2, gap="large")
    with tc1:
        st.markdown("""
<div class="g-card">
  <div style="font-size:0.75rem;font-weight:700;color:#6366f1;text-transform:uppercase;
       letter-spacing:0.08em;margin-bottom:0.8rem">Basic Functionality</div>
  <ul style="color:#94a3b8;font-size:0.87rem;line-height:2;padding-left:1.2rem;margin:0">
    <li><code>add_documents()</code> runs without errors</li>
    <li>Returns correct number of chunks</li>
    <li><code>retrieve()</code> returns Document objects with valid scores</li>
    <li>All scores are between 0 and 1</li>
    <li><code>ask()</code> returns a RAGResult with answer</li>
  </ul>

  <div style="height:1px;background:rgba(255,255,255,0.06);margin:1rem 0"></div>

  <div style="font-size:0.75rem;font-weight:700;color:#f59e0b;text-transform:uppercase;
       letter-spacing:0.08em;margin-bottom:0.8rem">Edge Cases</div>
  <ul style="color:#94a3b8;font-size:0.87rem;line-height:2;padding-left:1.2rem;margin:0">
    <li>Empty document list → handles gracefully</li>
    <li>Empty query → handles gracefully</li>
    <li>Very long document (10KB+) → doesn't crash</li>
    <li>Unicode characters → handled correctly</li>
  </ul>
</div>
""", unsafe_allow_html=True)

    with tc2:
        st.markdown("""
<div class="g-card">
  <div style="font-size:0.75rem;font-weight:700;color:#10b981;text-transform:uppercase;
       letter-spacing:0.08em;margin-bottom:0.8rem">Quality Checks</div>
  <ul style="color:#94a3b8;font-size:0.87rem;line-height:2;padding-left:1.2rem;margin:0">
    <li>Relevant query → top doc score > 0.5</li>
    <li>Irrelevant query → top doc score < 0.3</li>
    <li>Steps list is populated (for UI log)</li>
    <li>RAGResult.rag_type equals your class's <code>name</code></li>
    <li>Pipeline log has 3+ meaningful steps</li>
  </ul>

  <div style="height:1px;background:rgba(255,255,255,0.06);margin:1rem 0"></div>

  <div style="font-size:0.75rem;font-weight:700;color:#818cf8;text-transform:uppercase;
       letter-spacing:0.08em;margin-bottom:0.8rem">Performance</div>
  <ul style="color:#94a3b8;font-size:0.87rem;line-height:2;padding-left:1.2rem;margin:0">
    <li><code>add_documents()</code> for 10 docs < 10 seconds</li>
    <li><code>ask()</code> for simple query < 5 seconds</li>
    <li>No memory leaks on repeated calls</li>
  </ul>
</div>
""", unsafe_allow_html=True)

    st.markdown("#### 🤖 Automated Test Script")
    st.code("""# Save as tests/test_my_rag.py

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
    assert docs[0].score > 0.3

def test_ask_returns_ragresult(rag):
    result = rag.ask("Who was Einstein?")
    assert result.answer
    assert result.retrieved_docs
    assert result.rag_type == MyCustomRAG.name
    assert len(result.steps) >= 2

# Run: pytest tests/test_my_rag.py -v
""", language="python")

# ── TAB 5: REAL EXAMPLES ──────────────────────────────────────
with tabs[4]:
    st.markdown("""
<div class="sec-head" style="margin-top:0">
  <div class="sec-label">Learn by Example</div>
  <div class="sec-title">📚 Patterns from Existing Implementations</div>
</div>
""", unsafe_allow_html=True)

    examples = {
        "Pattern 1: Two-index fusion (Hybrid RAG)": """# From hybrid_rag.py — BM25 + FAISS + RRF fusion
class HybridRAG(BaseRAG):
    def add_documents(self, texts, source="doc"):
        tokenized = [chunk.lower().split() for chunk in all_chunks]
        self.bm25 = BM25Okapi(tokenized)

        embeddings = embed_texts(all_chunks).astype("float32")
        self.faiss_index = faiss.IndexFlatL2(dim)
        self.faiss_index.add(embeddings)

    def retrieve(self, query, top_k=3):
        bm25_scores = self.bm25.get_scores(query.lower().split())
        bm25_ranked = np.argsort(bm25_scores)[::-1][:k]

        query_vec = embed_texts([query]).astype("float32")
        _, vector_ranked = self.faiss_index.search(query_vec, k)

        # RRF Fusion
        rrf_scores = {}
        for rank, idx in enumerate(bm25_ranked):
            rrf_scores[idx] = rrf_scores.get(idx, 0) + 1.0/(60 + rank)
        for rank, idx in enumerate(vector_ranked[0]):
            rrf_scores[idx] = rrf_scores.get(idx, 0) + 1.0/(60 + rank)""",

        "Pattern 2: Decision loop with retry (Self-Reflective RAG)": """# From self_reflective_rag.py — retry with query expansion
def ask(self, query, top_k=3):
    current_query = query
    for attempt in range(self.max_retries + 1):
        docs = self._vector_retrieve(current_query, top_k)
        is_relevant, score, msg = self._reflect_on_relevance(query, docs)

        if is_relevant or attempt == self.max_retries:
            break  # good enough or last attempt

        # Expand query for next attempt
        current_query = self._expand_query(query, attempt + 1)""",

        "Pattern 3: Multi-stage chain (Multi-hop RAG)": """# From multihop_rag.py — hop 1 → extract entity → hop 2
def retrieve(self, query, top_k=3):
    all_docs = []

    # Hop 1
    hop1_docs = self._basic_retrieve(query, 2)
    all_docs.extend(hop1_docs)

    # Extract key entities from hop 1 results
    hop1_text = " ".join(d.content for d in hop1_docs)
    entities = self._extract_entities(hop1_text)

    if entities:
        # Hop 2: use extracted entity as new query context
        hop2_query = f"{query} {entities[0]}"
        hop2_docs = self._basic_retrieve(hop2_query, 2)
        all_docs.extend(hop2_docs)

    return sorted(all_docs, key=lambda d: d.score, reverse=True)[:top_k]""",

        "Pattern 4: Post-processing chunks (Contextual RAG)": """# From contextual_rag.py — compress after retrieval
def retrieve(self, query, top_k=3):
    # First: standard retrieval
    docs = self._vector_retrieve(query, top_k)

    # Then: compress each chunk (keep only relevant sentences)
    for doc in docs:
        original = doc.content
        compressed = self._compress_chunk(query, original)
        doc.content = compressed
        doc.retrieval_method = f"compressed ({len(compressed)/len(original):.0%} kept)"

    return docs""",
    }

    for pattern_name, code in examples.items():
        with st.expander(f"**{pattern_name}**"):
            st.code(code, language="python")

    st.markdown('<div class="fancy-div"></div>', unsafe_allow_html=True)
    st.info("""
**📌 Key principles for all RAG implementations in this project:**

1. **Always use `embed_texts()`** from `utils.py` — it's cached, shared, fast
2. **Always use `chunk_text()`** from `utils.py` — consistent chunking across all types
3. **Always use `demo_generate()`** as fallback — works without any LLM
4. **Always populate `steps[]`** — this is what makes the UI educational
5. **Always set `name`, `emoji`, `color`** — required for UI rendering
6. **Return `RAGResult`** with all fields filled — required by comparison page
    """)

# ── SIDEBAR ───────────────────────────────────────────────────
sidebar_nav("6")
with st.sidebar:
    st.divider()
    st.markdown("""
<div style="background:rgba(16,185,129,0.07);border:1px solid rgba(16,185,129,0.2);
     border-radius:10px;padding:0.8rem 1rem">
  <div style="font-size:0.72rem;font-weight:700;color:#34d399;text-transform:uppercase;
       letter-spacing:0.08em;margin-bottom:0.4rem">You've Reached the End!</div>
  <div style="font-size:0.85rem;color:#a7f3d0;font-weight:600">⭐ Go Build Something</div>
  <div style="font-size:0.78rem;color:#8892A4;margin-top:0.2rem">Return to Test Any RAG to try your creation</div>
</div>
""", unsafe_allow_html=True)
