"""
pages/2_How_RAG_Works.py
Visual step-by-step explainer of the RAG pipeline.
"""

import streamlit as st
import time
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from ui_styles import apply_global_styles, sidebar_nav

st.set_page_config(page_title="How RAG Works", page_icon="2️⃣", layout="wide")
apply_global_styles()

# ── PAGE HEADER ───────────────────────────────────────────────
st.markdown("""
<div style="padding:1.5rem 0 0.5rem">
  <div class="sec-label">Page 2 of 6</div>
  <h1 style="font-size:2rem;font-weight:800;color:#F0F4FF;margin:0.3rem 0;letter-spacing:-0.02em">
    How RAG Works — Step by Step
  </h1>
  <p style="color:#8892A4;font-size:0.95rem;margin:0">
    Let's trace exactly what happens when you ask RAG a question.
  </p>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="fancy-div"></div>', unsafe_allow_html=True)

# ── BIG PICTURE ───────────────────────────────────────────────
st.markdown("""
<div class="sec-head">
  <div class="sec-label">Overview</div>
  <div class="sec-title">🗺️ The Big Picture — 2 Phases</div>
</div>
""", unsafe_allow_html=True)

ph1, ph2 = st.columns(2, gap="large")
with ph1:
    st.markdown("""
<div class="g-card">
  <div style="display:flex;align-items:center;gap:0.7rem;margin-bottom:1rem">
    <div style="background:rgba(99,102,241,0.15);border:1px solid rgba(99,102,241,0.3);
         border-radius:8px;padding:0.4rem 0.8rem;font-size:0.72rem;font-weight:700;
         color:#818cf8;letter-spacing:0.08em;text-transform:uppercase">Phase 1</div>
    <div style="font-size:0.95rem;font-weight:700;color:#F0F4FF">Storing Knowledge</div>
  </div>
  <div style="color:#8892A4;font-size:0.8rem;margin-bottom:0.8rem;font-style:italic">Happens once, when you load your documents</div>
  <div style="display:flex;align-items:center;gap:0.4rem;flex-wrap:wrap">
    <div style="background:rgba(17,24,39,0.9);border:1px solid rgba(255,255,255,0.08);
         border-radius:8px;padding:0.5rem 0.8rem;font-size:0.82rem;color:#c7d2fe;font-weight:600">📄 Documents</div>
    <div style="color:#6366f1;font-size:1rem">→</div>
    <div style="background:rgba(17,24,39,0.9);border:1px solid rgba(255,255,255,0.08);
         border-radius:8px;padding:0.5rem 0.8rem;font-size:0.82rem;color:#c7d2fe;font-weight:600">✂️ Chunker</div>
    <div style="color:#6366f1;font-size:1rem">→</div>
    <div style="background:rgba(17,24,39,0.9);border:1px solid rgba(255,255,255,0.08);
         border-radius:8px;padding:0.5rem 0.8rem;font-size:0.82rem;color:#c7d2fe;font-weight:600">🔢 Embedder</div>
    <div style="color:#6366f1;font-size:1rem">→</div>
    <div style="background:rgba(17,24,39,0.9);border:1px solid rgba(255,255,255,0.08);
         border-radius:8px;padding:0.5rem 0.8rem;font-size:0.82rem;color:#c7d2fe;font-weight:600">🗄️ Vector DB</div>
  </div>
</div>
""", unsafe_allow_html=True)

with ph2:
    st.markdown("""
<div class="g-card">
  <div style="display:flex;align-items:center;gap:0.7rem;margin-bottom:1rem">
    <div style="background:rgba(16,185,129,0.12);border:1px solid rgba(16,185,129,0.25);
         border-radius:8px;padding:0.4rem 0.8rem;font-size:0.72rem;font-weight:700;
         color:#34d399;letter-spacing:0.08em;text-transform:uppercase">Phase 2</div>
    <div style="font-size:0.95rem;font-weight:700;color:#F0F4FF">Answering Questions</div>
  </div>
  <div style="color:#8892A4;font-size:0.8rem;margin-bottom:0.8rem;font-style:italic">Happens every time someone asks a question</div>
  <div style="display:flex;align-items:center;gap:0.4rem;flex-wrap:wrap">
    <div style="background:rgba(17,24,39,0.9);border:1px solid rgba(255,255,255,0.08);
         border-radius:8px;padding:0.5rem 0.8rem;font-size:0.82rem;color:#c7d2fe;font-weight:600">❓ Question</div>
    <div style="color:#6366f1;font-size:1rem">→</div>
    <div style="background:rgba(17,24,39,0.9);border:1px solid rgba(255,255,255,0.08);
         border-radius:8px;padding:0.5rem 0.8rem;font-size:0.82rem;color:#c7d2fe;font-weight:600">🔍 Search</div>
    <div style="color:#6366f1;font-size:1rem">→</div>
    <div style="background:rgba(17,24,39,0.9);border:1px solid rgba(255,255,255,0.08);
         border-radius:8px;padding:0.5rem 0.8rem;font-size:0.82rem;color:#c7d2fe;font-weight:600">📄 Chunks</div>
    <div style="color:#6366f1;font-size:1rem">→</div>
    <div style="background:rgba(17,24,39,0.9);border:1px solid rgba(255,255,255,0.08);
         border-radius:8px;padding:0.5rem 0.8rem;font-size:0.82rem;color:#c7d2fe;font-weight:600">🤖 LLM</div>
    <div style="color:#6366f1;font-size:1rem">→</div>
    <div style="background:rgba(17,24,39,0.9);border:1px solid rgba(255,255,255,0.08);
         border-radius:8px;padding:0.5rem 0.8rem;font-size:0.82rem;color:#c7d2fe;font-weight:600">💬 Answer</div>
  </div>
</div>
""", unsafe_allow_html=True)

# Full pipeline visualization
st.markdown("""
<div style="margin:1.5rem 0 0.3rem">
  <div style="font-size:0.7rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;
       color:#8892A4;text-align:center;margin-bottom:0.6rem">
    FULL PIPELINE VISUALIZED
  </div>
</div>

<div class="pipeline-wrap">
  <div class="pipe-box" style="border-color:rgba(99,102,241,0.4)">
    <span class="pipe-icon">❓</span>
    <div class="pipe-lbl">Input</div>
    <div class="pipe-nm">Your Question</div>
  </div>
  <div class="pipe-arr">→</div>
  <div class="pipe-box" style="border-color:rgba(139,92,246,0.4)">
    <span class="pipe-icon">🔢</span>
    <div class="pipe-lbl">Embedding</div>
    <div class="pipe-nm">Meaning Vector</div>
  </div>
  <div class="pipe-arr">→</div>
  <div class="pipe-box" style="border-color:rgba(168,85,247,0.4)">
    <span class="pipe-icon">🔍</span>
    <div class="pipe-lbl">Search</div>
    <div class="pipe-nm">Vector DB</div>
  </div>
  <div class="pipe-arr">→</div>
  <div class="pipe-box" style="border-color:rgba(236,72,153,0.4)">
    <span class="pipe-icon">📄</span>
    <div class="pipe-lbl">Retrieved</div>
    <div class="pipe-nm">Top Chunks</div>
  </div>
  <div class="pipe-arr">→</div>
  <div class="pipe-box" style="border-color:rgba(245,158,11,0.4)">
    <span class="pipe-icon">🤖</span>
    <div class="pipe-lbl">LLM</div>
    <div class="pipe-nm">Generate</div>
  </div>
  <div class="pipe-arr">→</div>
  <div class="pipe-box" style="border-color:rgba(16,185,129,0.4)">
    <span class="pipe-icon">💬</span>
    <div class="pipe-lbl">Output</div>
    <div class="pipe-nm">Answer</div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="fancy-div"></div>', unsafe_allow_html=True)

# ── STEP-BY-STEP TABS ─────────────────────────────────────────
st.markdown("""
<div class="sec-head">
  <div class="sec-label">Deep Dive</div>
  <div class="sec-title">🔬 Each Step Explained with Live Examples</div>
</div>
""", unsafe_allow_html=True)

tabs = st.tabs([
    "✂️ Step 1: Chunking",
    "🔢 Step 2: Embedding",
    "🔍 Step 3: Vector Search",
    "📄 Step 4: Retrieval",
    "🤖 Step 5: Generation",
])

# ── TAB 1: CHUNKING ───────────────────────────────────────────
with tabs[0]:
    c1, c2 = st.columns([1, 1], gap="large")
    with c1:
        st.markdown("""
<div class="g-card">
  <h3 style="font-size:1.05rem;font-weight:700;color:#F0F4FF;margin:0 0 1rem">✂️ What is Chunking?</h3>
  <p style="color:#94a3b8;font-size:0.88rem;line-height:1.65">
    <strong style="color:#c7d2fe">Splitting a long document into small, searchable pieces.</strong>
  </p>
  <p style="color:#94a3b8;font-size:0.88rem;line-height:1.65">
    If your document is 50 pages, comparing all of it to a question at once is slow and imprecise.
    Small chunks = faster + more precise search.
  </p>

  <div style="background:rgba(5,11,24,0.7);border:1px solid rgba(99,102,241,0.12);border-radius:10px;
       padding:1rem;margin:1rem 0;font-size:0.82rem;font-family:'JetBrains Mono',monospace">
    <div style="color:#6366f1;margin-bottom:0.4rem;font-size:0.72rem;font-weight:700;letter-spacing:0.08em">OVERLAP EXAMPLE</div>
    <div style="color:#a7f3d0">Chunk 1: "Einstein was born in 1879. He studied physics"</div>
    <div style="color:#fbbf24;margin:0.3rem 0">Chunk 2:      "He studied physics. Later he published..."</div>
    <div style="color:#8892A4;margin-top:0.5rem">↑ Overlap prevents mid-sentence splits ↑</div>
  </div>

  <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:0.6rem;margin-top:1rem">
    <div style="background:rgba(239,68,68,0.07);border:1px solid rgba(239,68,68,0.2);border-radius:8px;
         padding:0.6rem;text-align:center">
      <div style="font-size:0.72rem;font-weight:700;color:#f87171;text-transform:uppercase;letter-spacing:0.06em">Too Small</div>
      <div style="font-size:1.2rem;font-weight:700;color:#fca5a5">50</div>
      <div style="font-size:0.7rem;color:#8892A4">chars · Loses context</div>
    </div>
    <div style="background:rgba(16,185,129,0.07);border:1px solid rgba(16,185,129,0.25);border-radius:8px;
         padding:0.6rem;text-align:center">
      <div style="font-size:0.72rem;font-weight:700;color:#34d399;text-transform:uppercase;letter-spacing:0.06em">Just Right</div>
      <div style="font-size:1.2rem;font-weight:700;color:#a7f3d0">300</div>
      <div style="font-size:0.7rem;color:#8892A4">chars · ✅ Sweet spot</div>
    </div>
    <div style="background:rgba(245,158,11,0.07);border:1px solid rgba(245,158,11,0.2);border-radius:8px;
         padding:0.6rem;text-align:center">
      <div style="font-size:0.72rem;font-weight:700;color:#fbbf24;text-transform:uppercase;letter-spacing:0.06em">Too Large</div>
      <div style="font-size:1.2rem;font-weight:700;color:#fde68a">1000</div>
      <div style="font-size:0.7rem;color:#8892A4">chars · Loses precision</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    with c2:
        st.markdown("### 📝 Live Chunking Demo")
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
            st.markdown(f"""
<div style="background:rgba(16,185,129,0.07);border:1px solid rgba(16,185,129,0.2);
     border-radius:8px;padding:0.7rem 1rem;margin-bottom:0.8rem;display:flex;align-items:center;gap:0.5rem">
  <span style="font-size:1.2rem">✂️</span>
  <span style="font-size:0.92rem;font-weight:700;color:#a7f3d0">Result: {len(chunks)} chunks created</span>
</div>
""", unsafe_allow_html=True)
            for i, chunk in enumerate(chunks, 1):
                st.markdown(f"""
<div style="background:rgba(13,21,38,0.8);border:1px solid rgba(255,255,255,0.07);
     border-left:3px solid #6366f1;border-radius:8px;padding:0.8rem;margin:0.35rem 0">
  <div style="font-size:0.68rem;font-weight:700;color:#6366f1;letter-spacing:0.08em;
       text-transform:uppercase;margin-bottom:0.35rem">Chunk #{i}</div>
  <div style="color:#c7d2fe;font-size:0.87rem;line-height:1.55">{chunk}</div>
</div>
""", unsafe_allow_html=True)

# ── TAB 2: EMBEDDING ──────────────────────────────────────────
with tabs[1]:
    e1, e2 = st.columns([1, 1], gap="large")
    with e1:
        st.markdown("""
<div class="g-card">
  <h3 style="font-size:1.05rem;font-weight:700;color:#F0F4FF;margin:0 0 1rem">🔢 What is Embedding?</h3>
  <p style="color:#94a3b8;font-size:0.88rem;line-height:1.65">
    Converting text into a list of numbers that represent its <strong style="color:#c7d2fe">meaning</strong>.
    Computers can compare numbers extremely fast, enabling semantic search.
  </p>

  <div class="info-box" style="margin:0.8rem 0">
    <strong>Analogy:</strong> Imagine plotting countries on a map by culture.
    Italy and Spain end up near each other (both Mediterranean). Antarctica is far from both.
    Embeddings do the same thing — in 384 dimensions.
  </div>

  <div style="background:rgba(5,11,24,0.7);border:1px solid rgba(99,102,241,0.12);border-radius:10px;
       padding:1rem;margin:0.8rem 0;font-family:'JetBrains Mono',monospace;font-size:0.8rem">
    <div style="color:#6366f1;margin-bottom:0.6rem;font-size:0.68rem;font-weight:700;letter-spacing:0.08em">SIMILAR WORDS → SIMILAR VECTORS</div>
    <div style="color:#a7f3d0">"car"        → [0.12, -0.45, 0.87, ...]</div>
    <div style="color:#a7f3d0">"automobile" → [0.11, -0.44, 0.88, ...]  ← nearly identical!</div>
    <div style="color:#f87171">"pizza"      → [0.93,  0.22, -0.33, ...]  ← very different</div>
  </div>

  <div style="background:rgba(99,102,241,0.06);border:1px solid rgba(99,102,241,0.15);
       border-radius:8px;padding:0.8rem;font-size:0.83rem;color:#c7d2fe">
    <strong>Model used:</strong> <code style="background:rgba(0,0,0,0.3);padding:0.1rem 0.4rem;border-radius:4px">all-MiniLM-L6-v2</code><br>
    Free, open-source · 22MB · Produces 384-dimensional vectors
  </div>
</div>
""", unsafe_allow_html=True)

    with e2:
        st.markdown("### 🔬 See Embeddings Live")
        words = st.text_input("Enter comma-separated words:", "cat, kitten, dog, car, automobile, pizza")

        if st.button("🔢 Embed These Words", type="primary") and words:
            word_list = [w.strip() for w in words.split(",") if w.strip()]
            if word_list:
                with st.spinner("Computing embeddings…"):
                    from rag_core.utils import embed_texts
                    import numpy as np
                    import plotly.graph_objects as go

                    vecs = embed_texts(word_list)
                    st.markdown("**First 8 dimensions of each embedding:**")
                    for word, vec in zip(word_list, vecs):
                        short_vec = ", ".join([f"{v:.2f}" for v in vec[:8]])
                        st.markdown(f"""
<div style="background:rgba(13,21,38,0.8);border:1px solid rgba(99,102,241,0.15);
     border-radius:8px;padding:0.7rem 0.9rem;margin:0.3rem 0">
  <strong style="color:#818cf8">{word}</strong><br>
  <code style="color:#94a3b8;font-size:0.78rem;font-family:'JetBrains Mono',monospace">[{short_vec}, …] (384 total)</code>
</div>
""", unsafe_allow_html=True)

                    if len(word_list) > 1:
                        norms = np.linalg.norm(vecs, axis=1, keepdims=True)
                        normalized = vecs / (norms + 1e-8)
                        sim_matrix = normalized @ normalized.T

                        fig = go.Figure(data=go.Heatmap(
                            z=sim_matrix, x=word_list, y=word_list,
                            colorscale="Purples",
                            text=[[f"{v:.2f}" for v in row] for row in sim_matrix],
                            texttemplate="%{text}",
                        ))
                        fig.update_layout(
                            title="Semantic Similarity Heatmap (1.0 = identical meaning)",
                            height=350,
                            paper_bgcolor="#050B18",
                            plot_bgcolor="#0D1526",
                            font=dict(color="#e2e8f0", family="Inter"),
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        st.caption("Close to 1.0 = similar meaning · Close to 0.0 = different meaning")

# ── TAB 3: VECTOR SEARCH ──────────────────────────────────────
with tabs[2]:
    st.markdown("""
<div class="g-card" style="margin-bottom:1rem">
  <h3 style="font-size:1.05rem;font-weight:700;color:#F0F4FF;margin:0 0 0.8rem">🔍 Vector Search (FAISS)</h3>
  <p style="color:#94a3b8;font-size:0.88rem;line-height:1.65;margin-bottom:1rem">
    Finding the text chunks whose vectors are <strong style="color:#c7d2fe">closest</strong> to your query vector in
    high-dimensional space. FAISS is a library optimized for this at massive scale.
  </p>
  <div style="overflow-x:auto">
    <table style="width:100%;border-collapse:collapse;font-size:0.82rem">
      <thead>
        <tr style="border-bottom:1px solid rgba(99,102,241,0.2)">
          <th style="text-align:left;padding:0.5rem 0.8rem;color:#818cf8;font-weight:700">Approach</th>
          <th style="text-align:left;padding:0.5rem 0.8rem;color:#818cf8;font-weight:700">How</th>
          <th style="text-align:left;padding:0.5rem 0.8rem;color:#818cf8;font-weight:700">Speed</th>
          <th style="text-align:left;padding:0.5rem 0.8rem;color:#818cf8;font-weight:700">Accuracy</th>
        </tr>
      </thead>
      <tbody>
        <tr style="border-bottom:1px solid rgba(255,255,255,0.04)">
          <td style="padding:0.5rem 0.8rem;color:#c7d2fe;font-weight:600">FAISS IndexFlatL2</td>
          <td style="padding:0.5rem 0.8rem;color:#94a3b8">Compare all vectors exactly</td>
          <td style="padding:0.5rem 0.8rem;color:#fbbf24">⚡⚡</td>
          <td style="padding:0.5rem 0.8rem;color:#34d399">100%</td>
        </tr>
        <tr>
          <td style="padding:0.5rem 0.8rem;color:#c7d2fe;font-weight:600">FAISS IVF</td>
          <td style="padding:0.5rem 0.8rem;color:#94a3b8">Cluster vectors, search nearby clusters</td>
          <td style="padding:0.5rem 0.8rem;color:#34d399">⚡⚡⚡</td>
          <td style="padding:0.5rem 0.8rem;color:#fbbf24">~95%</td>
        </tr>
      </tbody>
    </table>
  </div>
</div>
""", unsafe_allow_html=True)

    import numpy as np
    import plotly.graph_objects as go

    np.random.seed(42)
    n_docs = 20
    doc_points = np.random.randn(n_docs, 2) * 2
    query_point = np.array([1.2, 0.8])
    distances = np.sqrt(((doc_points - query_point) ** 2).sum(axis=1))
    top3 = np.argsort(distances)[:3]

    fig = go.Figure()
    not_top = [i for i in range(n_docs) if i not in top3]
    fig.add_trace(go.Scatter(
        x=doc_points[not_top, 0], y=doc_points[not_top, 1],
        mode='markers+text', name='Document Chunks',
        marker=dict(color='#334155', size=11, line=dict(color='#475569', width=1)),
        text=[f"Doc {i}" for i in not_top],
        textposition="top center",
        textfont=dict(size=8, color="#64748b"),
    ))
    colors = ["#10b981", "#34d399", "#6ee7b7"]
    labels = ["🥇 Best match", "🥈 2nd match", "🥉 3rd match"]
    for rank, idx in enumerate(top3):
        fig.add_trace(go.Scatter(
            x=[doc_points[idx, 0]], y=[doc_points[idx, 1]],
            mode='markers+text', name=labels[rank],
            marker=dict(color=colors[rank], size=20, symbol="star",
                        line=dict(color='white', width=1)),
            text=[labels[rank]], textposition="top center",
            textfont=dict(size=10, color=colors[rank]),
        ))
    fig.add_trace(go.Scatter(
        x=[query_point[0]], y=[query_point[1]],
        mode='markers+text', name='❓ Your Query',
        marker=dict(color='#f59e0b', size=24, symbol="diamond",
                    line=dict(color='white', width=2)),
        text=["❓ Your Query"], textposition="top center",
        textfont=dict(size=11, color="#f59e0b"),
    ))
    for idx in top3:
        fig.add_shape(type="line",
            x0=query_point[0], y0=query_point[1],
            x1=doc_points[idx, 0], y1=doc_points[idx, 1],
            line=dict(color="#6366f1", width=2, dash="dot"))
    fig.update_layout(
        title="Vector Space: Finding nearest document chunks to your query",
        height=440,
        paper_bgcolor="#050B18",
        plot_bgcolor="#0D1526",
        font=dict(color="#e2e8f0", family="Inter"),
        xaxis=dict(gridcolor="#1e293b", title="Dimension 1"),
        yaxis=dict(gridcolor="#1e293b", title="Dimension 2"),
        legend=dict(bgcolor="rgba(13,21,38,0.9)", bordercolor="rgba(99,102,241,0.2)", borderwidth=1),
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Simplified 2D view — real vectors have 384 dimensions")

# ── TAB 4: RETRIEVAL ──────────────────────────────────────────
with tabs[3]:
    r1, r2 = st.columns([1, 1], gap="large")
    with r1:
        st.markdown("""
<div class="g-card">
  <h3 style="font-size:1.05rem;font-weight:700;color:#F0F4FF;margin:0 0 1rem">📄 Step 4: Retrieval</h3>
  <p style="color:#94a3b8;font-size:0.88rem;line-height:1.65">
    Taking the <strong style="color:#c7d2fe">top-k closest chunks</strong> and packaging them as context for the LLM.
  </p>

  <div style="margin:1rem 0">
    <div style="font-size:0.75rem;font-weight:700;color:#6366f1;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.6rem">
      Top-k Trade-offs
    </div>
    <div style="display:flex;flex-direction:column;gap:0.4rem">
      <div style="display:flex;align-items:center;gap:0.8rem;background:rgba(13,21,38,0.7);
           border-radius:8px;padding:0.6rem 0.8rem">
        <code style="color:#818cf8;font-size:0.85rem;font-family:'JetBrains Mono',monospace;min-width:30px">k=1</code>
        <div style="font-size:0.82rem;color:#94a3b8">Very focused · May miss important context</div>
      </div>
      <div style="display:flex;align-items:center;gap:0.8rem;background:rgba(13,21,38,0.7);
           border:1px solid rgba(16,185,129,0.2);border-radius:8px;padding:0.6rem 0.8rem">
        <code style="color:#34d399;font-size:0.85rem;font-family:'JetBrains Mono',monospace;min-width:30px">k=3</code>
        <div style="font-size:0.82rem;color:#94a3b8">✅ Good balance · Standard choice</div>
      </div>
      <div style="display:flex;align-items:center;gap:0.8rem;background:rgba(13,21,38,0.7);
           border-radius:8px;padding:0.6rem 0.8rem">
        <code style="color:#fbbf24;font-size:0.85rem;font-family:'JetBrains Mono',monospace;min-width:30px">k=10</code>
        <div style="font-size:0.82rem;color:#94a3b8">More context · Higher cost</div>
      </div>
    </div>
  </div>

  <div class="info-box" style="font-size:0.83rem">
    <strong>Relevance score guide:</strong><br>
    🟢 0.7–1.0 = Excellent match<br>
    🟡 0.5–0.7 = Good match<br>
    🔴 Below 0.5 = Probably irrelevant
  </div>
</div>
""", unsafe_allow_html=True)

    with r2:
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
            y=[f"Chunk {i+1}: {c[:35]}…" for i, c in enumerate(chunks_example)],
            orientation='h',
            marker_color=colors,
            text=[f"{s:.2f}" for s in scores],
            textposition='outside',
        ))
        fig.update_layout(
            title="Query: 'Who first walked on the Moon?'",
            xaxis_title="Relevance Score",
            height=300,
            paper_bgcolor="#050B18",
            plot_bgcolor="#0D1526",
            font=dict(color="#e2e8f0", family="Inter"),
            xaxis=dict(range=[0, 1.15], gridcolor="#1e293b"),
            yaxis=dict(gridcolor="#1e293b"),
            margin=dict(l=10, r=40, t=50, b=30),
        )
        st.plotly_chart(fig, use_container_width=True)
        st.success("✅ Top 2 chunks are highly relevant (>0.7)")
        st.error("❌ Bottom 3 chunks are unrelated to the query")

# ── TAB 5: GENERATION ─────────────────────────────────────────
with tabs[4]:
    g1, g2 = st.columns([1, 1], gap="large")
    with g1:
        st.markdown("""
<div class="g-card">
  <h3 style="font-size:1.05rem;font-weight:700;color:#F0F4FF;margin:0 0 1rem">🤖 Step 5: Generation</h3>
  <p style="color:#94a3b8;font-size:0.88rem;line-height:1.65">
    The LLM reads the retrieved chunks as context and writes an answer
    <strong style="color:#c7d2fe">grounded in your documents</strong>.
  </p>

  <div style="margin:1rem 0">
    <div style="font-size:0.75rem;font-weight:700;color:#6366f1;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.6rem">
      Two Modes Available
    </div>
    <div style="display:flex;flex-direction:column;gap:0.5rem">
      <div style="background:rgba(16,185,129,0.07);border:1px solid rgba(16,185,129,0.2);
           border-radius:8px;padding:0.8rem">
        <div style="font-size:0.82rem;font-weight:700;color:#34d399;margin-bottom:0.3rem">✅ Demo Mode (offline)</div>
        <div style="font-size:0.8rem;color:#94a3b8">Extracts the most relevant sentence from retrieved chunks.
        No LLM needed! Shows you exactly what retrieval found.</div>
      </div>
      <div style="background:rgba(99,102,241,0.06);border:1px solid rgba(99,102,241,0.18);
           border-radius:8px;padding:0.8rem">
        <div style="font-size:0.82rem;font-weight:700;color:#818cf8;margin-bottom:0.3rem">🦙 Ollama Mode (optional)</div>
        <div style="font-size:0.8rem;color:#94a3b8">Connects to a real local LLM for fluent, natural answers.
        Install Ollama to enable this.</div>
      </div>
    </div>
  </div>

  <div class="info-box" style="font-size:0.83rem">
    <strong>Key instruction in the prompt:</strong><br>
    <code style="background:rgba(0,0,0,0.3);padding:0.15rem 0.5rem;border-radius:4px;
         font-family:'JetBrains Mono',monospace">"Answer ONLY from the context above."</code><br>
    This stops the LLM from using its own potentially wrong knowledge.
  </div>
</div>
""", unsafe_allow_html=True)

    with g2:
        st.markdown("### 🔑 The Actual Prompt Structure")
        st.code("""# This is what gets sent to the LLM:

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

st.markdown('<div class="fancy-div"></div>', unsafe_allow_html=True)

# ── PUTTING IT ALL TOGETHER ───────────────────────────────────
st.markdown("""
<div class="sec-head">
  <div class="sec-label">Summary</div>
  <div class="sec-title">🎯 The Complete Pipeline in Code</div>
</div>
""", unsafe_allow_html=True)

with st.expander("▶️ See the Complete RAG Pipeline — 10 Lines of Code"):
    st.code("""from rag_core import NaiveRAG

# 1. Create RAG instance
rag = NaiveRAG()

# 2. Add your documents (chunking + embedding happens here automatically)
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

# ── SIDEBAR ───────────────────────────────────────────────────
sidebar_nav("2")
with st.sidebar:
    st.divider()
    st.markdown("""
<div style="background:rgba(99,102,241,0.07);border:1px solid rgba(99,102,241,0.15);
     border-radius:10px;padding:0.8rem 1rem">
  <div style="font-size:0.72rem;font-weight:700;color:#6366f1;text-transform:uppercase;
       letter-spacing:0.08em;margin-bottom:0.4rem">Up Next</div>
  <div style="font-size:0.85rem;color:#c7d2fe;font-weight:600">⭐ Test Any RAG</div>
  <div style="font-size:0.78rem;color:#8892A4;margin-top:0.2rem">Try it live — no setup needed!</div>
</div>
""", unsafe_allow_html=True)
