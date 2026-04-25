"""
app.py — RAG Master Guide
Main landing page.  Run with: streamlit run app.py
"""

import streamlit as st
from ui_styles import apply_global_styles, sidebar_nav

st.set_page_config(
    page_title="RAG Master Guide",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_global_styles()

# ── HERO ─────────────────────────────────────────────────────
st.markdown("""
<div class="hero-wrap">
  <div class="hero-badge">✦ Zero to Hero Course</div>
  <div class="hero-title">RAG Master Guide</div>
  <div class="hero-sub">
    Understand Retrieval-Augmented Generation from the ground up.<br>
    Theory · Visualization · Live Demo — all in one place.
  </div>
</div>
""", unsafe_allow_html=True)

# ── STAT METRICS ─────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("RAG Architectures", "11", help="From Naive to Agentic RAG")
with c2:
    st.metric("Sample Topics", "5", help="Space, Animals, India, Tech, Sports")
with c3:
    st.metric("Setup Time", "5 min", help="No API keys required!")
with c4:
    st.metric("Skill Required", "Zero", help="Designed for complete beginners")

st.markdown('<div class="fancy-div"></div>', unsafe_allow_html=True)

# ── WHAT IS RAG ───────────────────────────────────────────────
st.markdown("""
<div class="sec-head">
  <div class="sec-label">The 30-Second Explanation</div>
  <div class="sec-title">What is RAG?</div>
</div>
""", unsafe_allow_html=True)

col_a, col_b = st.columns(2, gap="large")

with col_a:
    st.markdown("""
<div class="g-card">
  <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:1rem">
    <span style="font-size:1.4rem">🤔</span>
    <span style="font-size:0.85rem;font-weight:700;color:#f87171;text-transform:uppercase;letter-spacing:0.06em">Without RAG</span>
  </div>
  <div style="background:rgba(239,68,68,0.06);border:1px solid rgba(239,68,68,0.15);border-radius:8px;padding:0.9rem;margin-bottom:1rem;font-style:italic;color:#fca5a5;font-size:0.92rem;line-height:1.6">
    "Einstein was born in 18…something." <span style="color:#6b7280;font-style:normal">(guessing)</span>
  </div>
  <p style="color:#94a3b8;font-size:0.88rem;line-height:1.65;margin:0">
    The AI only knows what it learned before its training cutoff.
    It may <strong style="color:#f87171">hallucinate</strong> facts confidently.
  </p>
</div>
""", unsafe_allow_html=True)

with col_b:
    st.markdown("""
<div class="g-card">
  <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:1rem">
    <span style="font-size:1.4rem">✅</span>
    <span style="font-size:0.85rem;font-weight:700;color:#34d399;text-transform:uppercase;letter-spacing:0.06em">With RAG</span>
  </div>
  <div style="background:rgba(16,185,129,0.06);border:1px solid rgba(16,185,129,0.15);border-radius:8px;padding:0.9rem;margin-bottom:1rem;font-style:italic;color:#a7f3d0;font-size:0.92rem;line-height:1.6">
    "Based on your document: Einstein was born in 1879." <span style="color:#6b7280;font-style:normal">(retrieved)</span>
  </div>
  <p style="color:#94a3b8;font-size:0.88rem;line-height:1.65;margin:0">
    The AI first reads <strong style="color:#34d399">YOUR documents</strong>, then answers.
    Facts come from verified sources — no guessing.
  </p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="info-box">
  💡 <strong>Simple analogy:</strong> RAG is like an <strong>"open book exam"</strong> for AI.<br>
  <span style="opacity:0.85">Without RAG = AI relies purely on memorized knowledge (closed book).<br>
  With RAG = AI reads the relevant pages before answering (open book).</span>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="fancy-div"></div>', unsafe_allow_html=True)

# ── LEARNING PATH ─────────────────────────────────────────────
st.markdown("""
<div class="sec-head">
  <div class="sec-label">Structured Learning Path</div>
  <div class="sec-title">🗺️ Your Journey Through RAG</div>
</div>
""", unsafe_allow_html=True)

lp_cols = st.columns(4, gap="medium")
pages_data = [
    ("1️⃣", "When Should I Use RAG?",
     "Understand exactly when RAG helps — and when it doesn't. Interactive quiz included.",
     "Start Here →", "1"),
    ("2️⃣", "How RAG Works",
     "Trace every step RAG takes to answer your question. Live interactive demos.",
     "Visual Deep-Dive →", "2"),
    ("⭐", "Test Any RAG",
     "Try 9 RAG architectures live. Paste any text, ask questions, see the magic.",
     "Try It Now →", "3"),
    ("4️⃣", "Compare RAG Types",
     "Same question, 3 RAG types. See exactly what's different and why.",
     "Compare →", "4"),
]

for col, (emoji, title, desc, cta, num) in zip(lp_cols, pages_data):
    with col:
        star_style = "border-color:rgba(99,102,241,0.4);box-shadow:0 0 20px rgba(99,102,241,0.12)" if num == "3" else ""
        st.markdown(f"""
<div class="lp-card" style="{star_style}">
  <div class="lp-bg-num">{num}</div>
  <div class="lp-emoji">{emoji}</div>
  <div class="lp-title">{title}</div>
  <div class="lp-desc">{desc}</div>
  <div class="lp-cta">{cta}</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="fancy-div"></div>', unsafe_allow_html=True)

# ── RAG TYPES OVERVIEW ────────────────────────────────────────
st.markdown("""
<div class="sec-head">
  <div class="sec-label">What You'll Learn</div>
  <div class="sec-title">📖 The 3 Core RAG Types</div>
</div>
""", unsafe_allow_html=True)

rt1, rt2, rt3 = st.columns(3, gap="medium")

with rt1:
    st.markdown("""
<div class="g-card">
  <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:1rem">
    <span style="font-size:1.6rem">🔵</span>
    <div>
      <div style="font-size:0.95rem;font-weight:700;color:#60a5fa">Naive RAG</div>
      <div style="font-size:0.72rem;color:#8892A4;font-weight:500">The Foundation</div>
    </div>
  </div>
  <p style="color:#94a3b8;font-size:0.85rem;line-height:1.6;margin-bottom:1rem">
    Converts everything to meaning-vectors and finds the closest semantic match.
  </p>
  <div style="display:flex;flex-direction:column;gap:0.3rem">
    <div style="font-size:0.82rem;color:#a7f3d0">✅ Easy to understand</div>
    <div style="font-size:0.82rem;color:#a7f3d0">✅ Fast retrieval</div>
    <div style="font-size:0.82rem;color:#a7f3d0">✅ Best starting point</div>
    <div style="font-size:0.82rem;color:#fca5a5">❌ Misses exact keywords</div>
  </div>
</div>
""", unsafe_allow_html=True)

with rt2:
    st.markdown("""
<div class="g-card">
  <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:1rem">
    <span style="font-size:1.6rem">🟣</span>
    <div>
      <div style="font-size:0.95rem;font-weight:700;color:#a78bfa">Hybrid RAG</div>
      <div style="font-size:0.72rem;color:#8892A4;font-weight:500">Keyword + Semantic</div>
    </div>
  </div>
  <p style="color:#94a3b8;font-size:0.85rem;line-height:1.6;margin-bottom:1rem">
    Combines BM25 keyword search with semantic vector search for the best of both worlds.
  </p>
  <div style="display:flex;flex-direction:column;gap:0.3rem">
    <div style="font-size:0.82rem;color:#a7f3d0">✅ Best of both worlds</div>
    <div style="font-size:0.82rem;color:#a7f3d0">✅ Handles names & tickers</div>
    <div style="font-size:0.82rem;color:#a7f3d0">✅ Production standard</div>
    <div style="font-size:0.82rem;color:#fca5a5">❌ Slightly more complex</div>
  </div>
</div>
""", unsafe_allow_html=True)

with rt3:
    st.markdown("""
<div class="g-card">
  <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:1rem">
    <span style="font-size:1.6rem">🟢</span>
    <div>
      <div style="font-size:0.95rem;font-weight:700;color:#34d399">Conversational RAG</div>
      <div style="font-size:0.72rem;color:#8892A4;font-weight:500">Multi-Turn Memory</div>
    </div>
  </div>
  <p style="color:#94a3b8;font-size:0.85rem;line-height:1.6;margin-bottom:1rem">
    Remembers your entire conversation, enabling follow-up questions naturally.
  </p>
  <div style="display:flex;flex-direction:column;gap:0.3rem">
    <div style="font-size:0.82rem;color:#a7f3d0">✅ Follow-up questions</div>
    <div style="font-size:0.82rem;color:#a7f3d0">✅ Multi-turn chat</div>
    <div style="font-size:0.82rem;color:#a7f3d0">✅ Chatbot use case</div>
    <div style="font-size:0.82rem;color:#fca5a5">❌ Context can grow large</div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="fancy-div"></div>', unsafe_allow_html=True)

# ── QUICK START ───────────────────────────────────────────────
with st.expander("⚡ Quick Start — Get Running in 5 Minutes", expanded=False):
    st.markdown("""
<div style="margin-bottom:0.8rem;color:#94a3b8;font-size:0.9rem">
  Get the full app running locally — no API keys required.
</div>
""", unsafe_allow_html=True)
    st.code("""# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/rag-master-guide
cd rag-master-guide

# 2. Install dependencies (one time only)
pip install -r requirements.txt

# 3. Launch the app
streamlit run app.py
# Opens at http://localhost:8501
# No API key needed — works fully offline!
""", language="bash")

    col_qs1, col_qs2 = st.columns(2)
    with col_qs1:
        st.success("**✅ What happens on first run:**\n- Downloads 22MB embedding model (once)\n- All demos use built-in sample data\n- Runs 100% locally, no internet needed")
    with col_qs2:
        st.info("**💡 Optional upgrade:**\n- Install [Ollama](https://ollama.ai) for real AI answers\n- Any local model works (Llama, Mistral, etc.)\n- Demo mode still works perfectly without it")

# ── SIDEBAR ───────────────────────────────────────────────────
sidebar_nav("home")

with st.sidebar:
    st.divider()
    st.markdown('<div style="font-size:0.68rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:#6366f1;margin-bottom:0.5rem">Status</div>', unsafe_allow_html=True)

    try:
        from rag_core.utils import check_ollama_running
        ollama_ok = check_ollama_running()
        if ollama_ok:
            st.success("✅ App + Ollama ready")
        else:
            st.success("✅ App ready (demo mode)")
            st.info("💡 Install Ollama for richer answers")
    except Exception:
        st.info("⏳ First run: downloading model…")

    st.divider()
    st.markdown("""
<div style="font-size:0.78rem;color:#4A5568;line-height:1.6">
  Built for beginners. No jargon. Everything explained from first principles.
</div>
""", unsafe_allow_html=True)
    st.markdown("[⭐ Star on GitHub](https://github.com)")
