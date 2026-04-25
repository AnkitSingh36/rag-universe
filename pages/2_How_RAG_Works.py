"""
pages/2_How_RAG_Works.py

Visual step-by-step explainer of the RAG pipeline.
Shows EXACTLY what happens when you ask RAG a question.
"""

import streamlit as st
import time

st.set_page_config(page_title="How RAG Works", page_icon="2️⃣", layout="wide")

st.title("2️⃣ How RAG Works — Step by Step")
st.markdown("*Let's trace exactly what happens when you ask RAG a question.*")
st.divider()

# ── THE BIG PICTURE ───────────────────────────────────────
st.subheader("🗺️ The Big Picture")

st.markdown("""
RAG has two phases:

**Phase 1: Storing Knowledge** *(happens once, when you load your documents)*
```
Your Documents → Chunker → Embedder → Vector Database
```

**Phase 2: Answering Questions** *(happens every time someone asks)*
```
Your Question → Embedder → Vector Search → Retrieved Chunks → LLM → Answer
```
""")

# Visual pipeline
st.markdown("""
<style>
.pipeline {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0;
    flex-wrap: wrap;
    margin: 1.5rem 0;
}
.pipe-step {
    background: linear-gradient(135deg, #1e293b, #0f172a);
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    text-align: center;
    min-width: 110px;
}
.pipe-step .icon { font-size: 1.8rem; margin-bottom: 4px; }
.pipe-step .label { font-size: 0.75rem; color: #94a3b8; font-weight: 600; }
.pipe-step .name { font-size: 0.9rem; color: #e2e8f0; font-weight: 700; }
.arrow { font-size: 1.8rem; color: #6366f1; padding: 0 0.3rem; }
.pipe-query { border-color: #6366f1; }
.pipe-embed { border-color: #8b5cf6; }
.pipe-search { border-color: #a855f7; }
.pipe-docs { border-color: #ec4899; }
.pipe-llm { border-color: #f59e0b; }
.pipe-answer { border-color: #10b981; }
</style>

<div style="text-align:center; margin-bottom:0.5rem; color:#94a3b8; font-size:0.85rem">PHASE 2: Answering Questions (what happens every time)</div>

<div class="pipeline">
  <div class="pipe-step pipe-query">
    <div class="icon">❓</div>
    <div class="label">INPUT</div>
    <div class="name">Your Question</div>
  </div>
  <div class="arrow">→</div>
  <div class="pipe-step pipe-embed">
    <div class="icon">🔢</div>
    <div class="label">EMBEDDING</div>
    <div class="name">Meaning Vector</div>
  </div>
  <div class="arrow">→</div>
  <div class="pipe-step pipe-search">
    <div class="icon">🔍</div>
    <div class="label">SEARCH</div>
    <div class="name">Vector DB</div>
  </div>
  <div class="arrow">→</div>
  <div class="pipe-step pipe-docs">
    <div class="icon">📄</div>
    <div class="label">RETRIEVED</div>
    <div class="name">Top Chunks</div>
  </div>
  <div class="arrow">→</div>
  <div class="pipe-step pipe-llm">
    <div class="icon">🤖</div>
    <div class="label">LLM</div>
    <div class="name">Generate</div>
  </div>
  <div class="arrow">→</div>
  <div class="pipe-step pipe-answer">
    <div class="icon">💬</div>
    <div class="label">OUTPUT</div>
    <div class="name">Answer</div>
  </div>
</div>
""", unsafe_allow_html=True)

st.divider()

# ── STEP-BY-STEP TABS ─────────────────────────────────────
st.subheader("🔬 Each Step Explained")

tabs = st.tabs([
    "Step 1: Chunking",
    "Step 2: Embedding",
    "Step 3: Vector Search",
    "Step 4: Retrieval",
    "Step 5: Generation",
])

with tabs[0]:
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### 🔪 Step 1: Chunking")
        st.markdown("""
**What is it?**
Splitting a long document into small, searchable pieces.

**Why?**
If your document is 50 pages, you can't compare ALL of it to a question efficiently.
Small chunks = faster + more precise search.

**Analogy:**
Think of a textbook chapter. Instead of comparing your question to 30 pages,
you compare it to each paragraph (chunk). Much faster and more focused!

**Typical chunk size:**
- Too small (50 chars) → loses context
- Too large (1000 chars) → loses precision
- Just right (200-400 chars) → ✅

**What about overlaps?**
```
Chunk 1:  "Einstein was born in 1879. He studied physics"
Chunk 2:       "He studied physics. Later he published..."
           ↑ overlap ↑
```
Overlap prevents sentences from being cut in half.
        """)

    with col2:
        st.markdown("### 📝 Live Example")
        example_text = st.text_area(
            "Try chunking this text:",
            value="The Apollo 11 mission was launched on July 16, 1969. Neil Armstrong became the first human to walk on the Moon. He stepped on the surface on July 20, 1969. The mission returned safely on July 24.",
            height=100,
        )

        chunk_size = st.slider("Chunk size (characters)", 50, 400, 150)
        overlap = st.slider("Overlap (characters)", 0, 100, 30)

        if example_text:
            from rag_core.utils import chunk_text
            chunks = chunk_text(example_text, chunk_size, overlap)

            st.markdown(f"**Result: {len(chunks)} chunks**")
            for i, chunk in enumerate(chunks, 1):
                st.markdown(f"""
<div style="background:#1e293b; border:1px solid #334155; border-radius:8px; padding:0.8rem; margin:0.4rem 0;">
<small style="color:#6366f1">Chunk #{i}</small><br>
<span style="color:#e2e8f0; font-size:0.9rem">{chunk}</span>
</div>
""", unsafe_allow_html=True)

with tabs[1]:
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### 🔢 Step 2: Embedding")
        st.markdown("""
**What is it?**
Converting text into a list of numbers that represent its **meaning**.

**Why numbers?**
Computers can't compare text directly. But they can compare numbers extremely fast.

**Analogy:**
Imagine plotting countries on a map by personality:
- Italy, Spain → near each other (both Mediterranean, warm)
- Antarctica → far from both
- If someone asks "warm European country" → the map shows Italy and Spain are closest

Embeddings do the same thing but in 384 dimensions instead of 2.

**Key insight:** Words that MEAN the same thing → similar numbers
```
"car"        → [0.12, -0.45, 0.87, ...]
"automobile" → [0.11, -0.44, 0.88, ...]  ← almost same!
"pizza"      → [0.93,  0.22, -0.33, ...]  ← very different
```

**Model used here:** `all-MiniLM-L6-v2`
- Free & open-source
- 22MB (tiny!)
- Produces 384-dimensional vectors
        """)

    with col2:
        st.markdown("### 🔬 See Embeddings Live")
        words = st.text_input("Enter comma-separated words:", "cat, kitten, dog, car, automobile, pizza")

        if st.button("Embed These Words") and words:
            word_list = [w.strip() for w in words.split(",") if w.strip()]

            if word_list:
                with st.spinner("Embedding..."):
                    from rag_core.utils import embed_texts
                    import numpy as np
                    import plotly.express as px

                    vecs = embed_texts(word_list)

                    # Show truncated vectors
                    st.markdown("**First 8 dimensions of each embedding:**")
                    for word, vec in zip(word_list, vecs):
                        short_vec = ", ".join([f"{v:.2f}" for v in vec[:8]])
                        st.markdown(f"""
<div style="background:#1e293b; border:1px solid #334155; border-radius:8px; padding:0.8rem; margin:0.4rem 0">
<strong style="color:#6366f1">{word}</strong><br>
<code style="color:#94a3b8; font-size:0.8rem">[{short_vec}, ...] (384 total)</code>
</div>
""", unsafe_allow_html=True)

                    # Similarity matrix
                    if len(word_list) > 1:
                        norms = np.linalg.norm(vecs, axis=1, keepdims=True)
                        normalized = vecs / (norms + 1e-8)
                        sim_matrix = normalized @ normalized.T

                        import plotly.figure_factory as ff
                        import plotly.graph_objects as go

                        fig = go.Figure(data=go.Heatmap(
                            z=sim_matrix,
                            x=word_list,
                            y=word_list,
                            colorscale="Purples",
                            text=[[f"{v:.2f}" for v in row] for row in sim_matrix],
                            texttemplate="%{text}",
                        ))
                        fig.update_layout(
                            title="Similarity Between Words (1.0 = identical meaning)",
                            height=350,
                            paper_bgcolor="#0f172a",
                            plot_bgcolor="#0f172a",
                            font=dict(color="#e2e8f0"),
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        st.caption("Close to 1.0 = similar meaning | Close to 0.0 = different meaning")

with tabs[2]:
    st.markdown("### 🔍 Step 3: Vector Search (FAISS)")
    st.markdown("""
**What is it?**
Finding the text chunks whose vectors are CLOSEST to your query vector.

**Two approaches:**

| Approach | How | Speed | Accuracy |
|----------|-----|-------|----------|
| **Naive RAG** | Check ALL vectors (exact) | Slower for large DBs | 100% |
| **FAISS IndexFlatL2** | Compare all vectors using L2 (Euclidean) distance | Fast | 100% |
| **FAISS IVF** | Cluster vectors, search only nearby clusters | Very fast | ~95% |

**The math (don't worry if it looks scary):**

L2 Distance between two vectors A and B:
```
distance = sqrt((A₁-B₁)² + (A₂-B₂)² + ... + (A₃₈₄-B₃₈₄)²)
```
Smaller distance = more similar = more relevant!

**Visualization:**
""")

    # Plot a 2D visualization of how vector search works
    import numpy as np
    import plotly.graph_objects as go

    np.random.seed(42)
    n_docs = 20

    # Create mock 2D points for visualization
    doc_points = np.random.randn(n_docs, 2) * 2
    query_point = np.array([1.2, 0.8])

    # Find 3 nearest neighbors
    distances = np.sqrt(((doc_points - query_point) ** 2).sum(axis=1))
    top3 = np.argsort(distances)[:3]

    fig = go.Figure()

    # All document points
    not_top = [i for i in range(n_docs) if i not in top3]
    fig.add_trace(go.Scatter(
        x=doc_points[not_top, 0], y=doc_points[not_top, 1],
        mode='markers+text',
        name='Document Chunks',
        marker=dict(color='#475569', size=12),
        text=[f"Doc {i}" for i in not_top],
        textposition="top center",
        textfont=dict(size=9, color="#94a3b8"),
    ))

    # Top 3 nearest
    colors = ["#10b981", "#34d399", "#6ee7b7"]
    labels = ["Best match", "2nd match", "3rd match"]
    for rank, idx in enumerate(top3):
        fig.add_trace(go.Scatter(
            x=[doc_points[idx, 0]], y=[doc_points[idx, 1]],
            mode='markers+text',
            name=labels[rank],
            marker=dict(color=colors[rank], size=18, symbol="star"),
            text=[labels[rank]],
            textposition="top center",
            textfont=dict(size=10, color=colors[rank]),
        ))

    # Query point
    fig.add_trace(go.Scatter(
        x=[query_point[0]], y=[query_point[1]],
        mode='markers+text',
        name='Your Query',
        marker=dict(color='#f59e0b', size=22, symbol="diamond"),
        text=["❓ Your Query"],
        textposition="top center",
        textfont=dict(size=11, color="#f59e0b"),
    ))

    # Draw lines from query to top 3
    for idx in top3:
        fig.add_shape(
            type="line",
            x0=query_point[0], y0=query_point[1],
            x1=doc_points[idx, 0], y1=doc_points[idx, 1],
            line=dict(color="#6366f1", width=2, dash="dot"),
        )

    fig.update_layout(
        title="Vector Space: Finding nearest document chunks to your query",
        height=450,
        paper_bgcolor="#0f172a",
        plot_bgcolor="#1e293b",
        font=dict(color="#e2e8f0"),
        xaxis=dict(gridcolor="#334155", title="Dimension 1"),
        yaxis=dict(gridcolor="#334155", title="Dimension 2"),
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption("(Simplified 2D view. Real vectors have 384 dimensions)")

with tabs[3]:
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("### 📄 Step 4: Retrieval")
        st.markdown("""
**What is it?**
Taking the top-k closest chunks and packaging them as context.

**Top-k explained:**
- k=1 → only the single best match
- k=3 → top 3 matches (most common)
- k=10 → top 10 matches (for complex questions)

**Trade-off:**
| k value | Pros | Cons |
|---------|------|------|
| k=1 | Very focused | Might miss important context |
| k=3 | Good balance | Standard choice |
| k=10 | More context | More tokens = more expensive |

**Relevance scores:**
Each retrieved chunk gets a score (0 to 1):
- 0.9+ = Excellent match
- 0.7-0.9 = Good match
- Below 0.5 = Probably irrelevant

💡 **Tip:** If ALL your retrieved chunks score below 0.5, the question
is probably not related to your documents.
        """)
    with col2:
        st.markdown("### 📊 Score Distribution Example")
        import plotly.graph_objects as go
        chunks_example = [
            "The Apollo 11 mission landed on the Moon in 1969.",
            "Neil Armstrong was the first astronaut on the Moon.",
            "Saturn has 146 known moons.",
            "Apple stock price rose 5% today.",
            "The recipe calls for 2 cups of flour.",
        ]
        scores = [0.91, 0.83, 0.47, 0.12, 0.08]
        colors = ["#10b981" if s > 0.6 else "#f59e0b" if s > 0.3 else "#ef4444" for s in scores]

        fig = go.Figure(go.Bar(
            x=scores,
            y=[f"Chunk {i+1}: {c[:35]}..." for i, c in enumerate(chunks_example)],
            orientation='h',
            marker_color=colors,
            text=[f"{s:.2f}" for s in scores],
            textposition='outside',
        ))
        fig.update_layout(
            title="Query: 'Who first walked on the Moon?'",
            xaxis_title="Relevance Score",
            height=300,
            paper_bgcolor="#0f172a",
            plot_bgcolor="#1e293b",
            font=dict(color="#e2e8f0"),
            xaxis=dict(range=[0, 1.1], gridcolor="#334155"),
            yaxis=dict(gridcolor="#334155"),
        )
        st.plotly_chart(fig, use_container_width=True)
        st.success("✅ Top 2 are relevant (>0.7) | ❌ Bottom 3 are not relevant")

with tabs[4]:
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("### 🤖 Step 5: Generation")
        st.markdown("""
**What is it?**
The LLM reads the retrieved chunks and writes an answer.

**The prompt:**
```
You are a helpful assistant.
Answer the question based ONLY on the context below.

Context:
[Chunk 1: "Apollo 11 landed in 1969..."]
[Chunk 2: "Neil Armstrong was first..."]

Question: Who first walked on the Moon?

Answer:
```

**Two modes in this app:**
1. **Demo Mode (offline):** Extracts the most relevant sentence from retrieved chunks.
   No LLM needed! Works completely offline. ✅

2. **Ollama Mode (optional):** Connects to a real local LLM (Mistral, Llama, etc.)
   for more natural, fluent answers.

**Why does Demo Mode still work?**
It shows you EXACTLY what retrieval found — which is the heart of RAG!
The LLM just formats it better. The retrieval is the important part.

**Common issue: Hallucination**
Without RAG: "I think Armstrong landed in 1968" ← WRONG, made up
With RAG: "According to your document: 1969" ← CORRECT, from source
        """)
    with col2:
        st.markdown("### 🔑 The Prompt That Powers RAG")
        st.code("""
# This is the actual prompt structure sent to the LLM:

SYSTEM = "You are a helpful assistant."

CONTEXT = \"\"\"
[Document 1] The Apollo 11 mission was launched on
July 16, 1969. Neil Armstrong and Buzz Aldrin landed
on the Moon on July 20, 1969.

[Document 2] Neil Armstrong became the first human
to walk on the Moon, saying: "One small step for man,
one giant leap for mankind."
\"\"\"

QUESTION = "Who first walked on the Moon?"

PROMPT = f\"\"\"{SYSTEM}

Context:
{CONTEXT}

Question: {QUESTION}

Answer ONLY from the context above.
If not in context, say "I don't know."

Answer:\"\"\"
""", language="python")

        st.info("""
💡 **The most important instruction:**
`"Answer ONLY from the context above."`

This prevents the LLM from using its own (potentially wrong) knowledge.
The answer must come from YOUR documents!
""")

st.divider()

# ── PUTTING IT ALL TOGETHER ────────────────────────────────
st.subheader("🎯 Putting It All Together")

with st.expander("▶️ See the Complete RAG Pipeline with Real Code", expanded=False):
    st.code("""
from rag_core import NaiveRAG

# 1. Create RAG instance
rag = NaiveRAG()

# 2. Add your documents (chunking + embedding happens here)
rag.add_documents([
    "The Apollo 11 mission was launched on July 16, 1969...",
    "Neil Armstrong became the first human to walk on the Moon...",
])

# 3. Ask a question (retrieval + generation happens here)
result = rag.ask("Who first walked on the Moon?")

# 4. See the results
print(result.answer)
# → "Based on your documents: Neil Armstrong became the first human to walk on the Moon"

print(f"Retrieval took: {result.retrieval_ms:.1f}ms")
print(f"Top match score: {result.retrieved_docs[0].score:.2f}")
print(f"Chunks searched: {result.total_chunks_searched}")
""", language="python")

with st.sidebar:
    st.markdown("## 🗺️ Navigation")
    st.page_link("app.py", label="🏠 Home")
    st.page_link("pages/1_When_To_Use_RAG.py", label="1️⃣ When to Use RAG")
    st.page_link("pages/2_How_RAG_Works.py", label="2️⃣ How RAG Works")
    st.page_link("pages/3_Test_Any_RAG.py", label="3️⃣ Test Any RAG ⭐")
    st.page_link("pages/4_Compare_RAGs.py", label="4️⃣ Compare RAG Types")
    st.divider()
    st.markdown("**Next:** Try it yourself →")
