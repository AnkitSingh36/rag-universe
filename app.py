"""
app.py — RAG Master Guide
Main landing page of the Streamlit app.

Run with: streamlit run app.py
"""

import streamlit as st

# ── Page configuration ─────────────────────────────────────
st.set_page_config(
    page_title="RAG Master Guide",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ──────────────────────────────────────────────
st.markdown("""
<style>
    /* Main font and background */
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Space Grotesk', sans-serif;
    }

    /* Hero title */
    .hero-title {
        font-size: 3.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #6366f1, #8b5cf6, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1.2;
        margin-bottom: 0.5rem;
    }

    .hero-sub {
        font-size: 1.3rem;
        color: #94a3b8;
        margin-bottom: 2rem;
    }

    /* Step cards */
    .step-card {
        background: linear-gradient(135deg, #1e293b, #0f172a);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 1.8rem;
        text-align: center;
        transition: transform 0.2s ease;
    }

    .step-card:hover {
        transform: translateY(-4px);
        border-color: #6366f1;
    }

    .step-emoji {
        font-size: 3rem;
        margin-bottom: 0.8rem;
    }

    .step-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #e2e8f0;
        margin-bottom: 0.5rem;
    }

    .step-desc {
        font-size: 0.9rem;
        color: #94a3b8;
    }

    /* Info boxes */
    .info-box {
        background: #0f172a;
        border-left: 4px solid #6366f1;
        border-radius: 8px;
        padding: 1.2rem 1.5rem;
        margin: 1rem 0;
        color: #e2e8f0;
    }

    .rag-tag {
        display: inline-block;
        background: #1e293b;
        border: 1px solid #475569;
        border-radius: 999px;
        padding: 0.3rem 0.9rem;
        font-size: 0.85rem;
        color: #94a3b8;
        margin: 0.2rem;
    }

    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ── HERO SECTION ───────────────────────────────────────────
st.markdown('<div class="hero-title">🧠 RAG Master Guide</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-sub">Learn Retrieval-Augmented Generation from zero to hero.<br>'
    'Theory • Visualization • Live Demo • All in one place.</div>',
    unsafe_allow_html=True,
)

# Quick stat row
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("RAG Types", "3", help="Naive, Hybrid, Conversational")
with c2:
    st.metric("Sample Topics", "5", help="Space, Animals, India, Tech, Sports")
with c3:
    st.metric("Setup Time", "5 min", help="No API keys needed!")
with c4:
    st.metric("Skill Level", "Zero", help="Designed for complete beginners")

st.divider()

# ── WHAT IS RAG? ───────────────────────────────────────────
st.subheader("🤔 What is RAG — in 30 seconds?")

col1, col2 = st.columns(2)
with col1:
    st.markdown("""
**Without RAG (pure AI):**

> "Einstein was born in 18…something."
> *(guessing from training)*

The AI only knows what it learned before its cutoff date.
It might make up facts confidently. This is called **hallucination**.
    """)

with col2:
    st.markdown("""
**With RAG (your documents + AI):**

> "Based on your document: Einstein was born in 1879."
> *(retrieved from YOUR text)*

The AI first reads YOUR documents, then answers.
No more guessing. Facts come from verified sources. ✅
    """)

st.markdown("""
<div class="info-box">
💡 <strong>Simple analogy:</strong> RAG is like an "open book exam" for AI.<br>
Without RAG = AI has to remember everything from memory (closed book).<br>
With RAG = AI can read the relevant pages before answering (open book).
</div>
""", unsafe_allow_html=True)

st.divider()

# ── NAVIGATE ──────────────────────────────────────────────
st.subheader("🗺️ Your Learning Path")

cols = st.columns(4)
pages = [
    ("1️⃣", "When Should I Use RAG?", "Start here. Understand WHEN RAG helps vs when it doesn't.", "👈 Go to page 1"),
    ("2️⃣", "How RAG Works", "See the exact steps RAG follows to answer your question.", "👈 Go to page 2"),
    ("3️⃣", "Test Any RAG", "Try it yourself! Paste any text and ask questions.", "⭐ START HERE"),
    ("4️⃣", "Compare RAG Types", "Run the same question through 3 RAG types. See the difference.", "👈 Go to page 4"),
]

for col, (num, title, desc, cta) in zip(cols, pages):
    with col:
        st.markdown(f"""
<div class="step-card">
  <div class="step-emoji">{num}</div>
  <div class="step-title">{title}</div>
  <div class="step-desc">{desc}</div>
  <br><small style="color:#6366f1">{cta}</small>
</div>
""", unsafe_allow_html=True)

st.divider()

# ── RAG TYPES OVERVIEW ─────────────────────────────────────
st.subheader("📖 3 RAG Types You'll Learn")

t1, t2, t3 = st.columns(3)

with t1:
    st.markdown("#### 🔵 Naive RAG")
    st.markdown("""
**The Simple One**

Converts everything to meaning-vectors and finds closest match.

- ✅ Easy to understand
- ✅ Fast retrieval
- ✅ Best starting point
- ❌ Misses exact keywords
    """)

with t2:
    st.markdown("#### 🟣 Hybrid RAG")
    st.markdown("""
**The Smart One**

Keyword search **+** Semantic search, combined.

- ✅ Best of both worlds
- ✅ Handles names, tickers
- ✅ Production standard
- ❌ Slightly more complex
    """)

with t3:
    st.markdown("#### 🟢 Conversational RAG")
    st.markdown("""
**The Memory One**

Remembers your whole conversation.

- ✅ Follow-up questions
- ✅ Multi-turn chat
- ✅ Chatbot use case
- ❌ Context can grow large
    """)

st.divider()

# ── QUICK START ────────────────────────────────────────────
with st.expander("⚡ Quick Start — Run This in 5 Minutes", expanded=False):
    st.code("""# 1. Clone the project
git clone https://github.com/YOUR_USERNAME/rag-master-guide
cd rag-master-guide

# 2. Install dependencies (one time)
pip install -r requirements.txt

# 3. Launch the app
streamlit run app.py

# The app opens at http://localhost:8501
# No API key needed — works fully offline!
""", language="bash")

    st.markdown("""
**What happens on first run:**
- Downloads a 22MB embedding model automatically (one time only)
- All demos use built-in sample data
- Optional: Install [Ollama](https://ollama.ai) for richer AI-generated answers
    """)

# ── SIDEBAR ────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🧠 RAG Master Guide")
    st.markdown("---")
    st.markdown("### Navigate")
    st.page_link("pages/1_When_To_Use_RAG.py", label="1️⃣ When Should I Use RAG?")
    st.page_link("pages/2_How_RAG_Works.py", label="2️⃣ How RAG Works")
    st.page_link("pages/3_Test_Any_RAG.py", label="3️⃣ Test Any RAG ⭐")
    st.page_link("pages/4_Compare_RAGs.py", label="4️⃣ Compare RAG Types")
    st.markdown("---")
    st.markdown("### Status")

    # Check if embedding model is cached
    try:
        from rag_core.utils import check_ollama_running
        ollama_ok = check_ollama_running()
        st.success("✅ App ready") if not ollama_ok else st.success("✅ App + Ollama ready")
        if not ollama_ok:
            st.info("💡 Install Ollama for richer answers (optional)")
    except Exception:
        st.info("⏳ First run: downloading model...")

    st.markdown("---")
    st.markdown("### About")
    st.markdown("Built for beginners. No jargon. Everything explained.")
    st.markdown("[⭐ Star on GitHub](https://github.com)")
