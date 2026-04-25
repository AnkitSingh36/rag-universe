"""
pages/3_Test_Any_RAG.py — Main interactive demo.
Users choose documents, pick a RAG type, ask questions, see full visualization.
"""

import streamlit as st
import time, sys, os, re
import plotly.graph_objects as go

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from rag_core import NaiveRAG, HybridRAG, ConversationalRAG, ALL_RAG_TYPES, check_ollama_running
from rag_core.utils import chunk_text
from data import get_topic_names, get_sample_doc
from ui_styles import apply_global_styles, sidebar_nav

st.set_page_config(page_title="Test Any RAG", page_icon="⭐", layout="wide")
apply_global_styles()

# ── PAGE HEADER ───────────────────────────────────────────────
st.markdown("""
<div style="padding:1.5rem 0 0.5rem">
  <div class="sec-label">Page 3 of 6 — Interactive Demo</div>
  <h1 style="font-size:2rem;font-weight:800;color:#F0F4FF;margin:0.3rem 0;letter-spacing:-0.02em">
    ⭐ Test Any RAG — Live Demo
  </h1>
  <p style="color:#8892A4;font-size:0.95rem;margin:0">
    Load any document · Choose a RAG type · Ask a question · See exactly how it works.
  </p>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="fancy-div"></div>', unsafe_allow_html=True)

# ── SIDEBAR SETTINGS ──────────────────────────────────────────
with st.sidebar:
    st.markdown("""
<div style="padding:0.4rem 0 0.6rem">
  <div style="font-size:0.68rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;
       color:#6366f1;margin-bottom:0.5rem">⚙️ Settings</div>
</div>
""", unsafe_allow_html=True)

    use_ollama = False
    if check_ollama_running():
        use_ollama = st.toggle("🦙 Use Ollama LLM", value=True,
                               help="Ollama detected! Enables real LLM answers.")
        st.success("✅ Ollama ready")
    else:
        st.info("💡 Demo mode — no LLM needed.\nInstall Ollama for richer answers.")

    top_k = st.slider("Retrieve top-k chunks", 1, 5, 3,
                      help="How many document chunks to retrieve for each question")

sidebar_nav("3")

# ─────────────────────────────────────────────────────────────
# STEP INDICATORS
# ─────────────────────────────────────────────────────────────
def step_header(num: str, title: str, subtitle: str = ""):
    st.markdown(f"""
<div style="display:flex;align-items:center;gap:0.8rem;margin:0.5rem 0 1rem">
  <div style="background:linear-gradient(135deg,#6366f1,#8b5cf6);
       border-radius:50%;width:36px;height:36px;display:flex;align-items:center;
       justify-content:center;font-size:0.9rem;font-weight:700;color:white;flex-shrink:0;
       box-shadow:0 4px 12px rgba(99,102,241,0.4)">{num}</div>
  <div>
    <div style="font-size:1.1rem;font-weight:700;color:#F0F4FF">{title}</div>
    {'<div style="font-size:0.82rem;color:#8892A4;margin-top:0.1rem">' + subtitle + '</div>' if subtitle else ''}
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# STEP 1: LOAD DOCUMENTS
# ─────────────────────────────────────────────────────────────
step_header("1", "Choose Your Knowledge Base",
            "Select a sample topic or paste your own text")

doc_source = st.radio(
    "Where should RAG get its knowledge?",
    ["📚 Use a sample topic", "✏️ Paste your own text"],
    horizontal=True,
)

doc_text = ""
doc_label = "document"

if "📚" in doc_source:
    topic_names = get_topic_names()
    col_topic, col_qs = st.columns([2, 1], gap="large")

    with col_topic:
        selected_topic = st.selectbox("Pick a topic:", topic_names)
        topic_data = get_sample_doc(selected_topic)

        with st.expander(f"📖 Preview: {selected_topic}", expanded=True):
            st.markdown(f'<div style="color:#94a3b8;font-size:0.88rem;line-height:1.6">{topic_data["text"][:800]}…</div>', unsafe_allow_html=True)

    with col_qs:
        st.markdown("""
<div style="font-size:0.75rem;font-weight:700;color:#6366f1;text-transform:uppercase;
     letter-spacing:0.08em;margin-bottom:0.6rem">💡 Try These Questions</div>
""", unsafe_allow_html=True)
        for q in topic_data["suggested_questions"][:4]:
            if st.button(f"❓ {q}", key=f"btn_{q[:20]}", use_container_width=True):
                st.session_state["prefill_question"] = q

    doc_text = topic_data["text"]
    doc_label = selected_topic
else:
    doc_text = st.text_area(
        "Paste any text (article, Wikipedia page, study notes, company docs…):",
        height=200,
        placeholder="Copy-paste any text here. Wikipedia articles, news stories, PDFs, meeting notes — anything works!",
    )

if not doc_text.strip():
    st.markdown("""
<div style="background:rgba(245,158,11,0.07);border:1px solid rgba(245,158,11,0.2);
     border-radius:10px;padding:1rem 1.2rem;color:#fde68a;font-size:0.9rem">
  👆 Please select a topic or paste some text above to continue.
</div>
""", unsafe_allow_html=True)
    st.stop()

with st.expander("✂️ Preview: How your text gets chunked"):
    chunks_preview = chunk_text(doc_text, 300, 50)
    st.markdown(f"""
<div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.8rem">
  <span style="font-size:0.9rem;font-weight:700;color:#a7f3d0">Your text → {len(chunks_preview)} chunks created</span>
  <span class="bdg bdg-green">{len(chunks_preview)} chunks</span>
</div>
""", unsafe_allow_html=True)

    preview_cols = st.columns(3)
    for i, chunk in enumerate(chunks_preview[:6]):
        with preview_cols[i % 3]:
            st.markdown(f"""
<div style="background:rgba(13,21,38,0.8);border:1px solid rgba(255,255,255,0.07);
     border-left:3px solid #6366f1;border-radius:8px;padding:0.7rem;margin:0.3rem 0;height:110px;overflow:hidden">
  <div style="font-size:0.65rem;font-weight:700;color:#6366f1;letter-spacing:0.08em;
       text-transform:uppercase;margin-bottom:0.3rem">Chunk #{i+1}</div>
  <div style="color:#94a3b8;font-size:0.8rem;line-height:1.5">{chunk[:130]}{'…' if len(chunk)>130 else ''}</div>
</div>
""", unsafe_allow_html=True)
    if len(chunks_preview) > 6:
        st.caption(f"… and {len(chunks_preview) - 6} more chunks")

st.markdown('<div class="fancy-div"></div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# STEP 2: CHOOSE RAG TYPE
# ─────────────────────────────────────────────────────────────
step_header("2", "Choose RAG Type",
            "Each architecture retrieves documents differently")

rag_info = {
    "🔵 Naive RAG":          {"emoji": "🔵", "tagline": "The Foundation", "how": "Converts everything to vectors, finds closest semantic match", "best_for": "Simple factual Q&A", "speed": "⚡⚡⚡", "accuracy": "⭐⭐⭐"},
    "🟣 Hybrid RAG":         {"emoji": "🟣", "tagline": "Keyword + Semantic", "how": "BM25 keyword match + vector search, fused with RRF", "best_for": "Names, codes, mixed queries", "speed": "⚡⚡", "accuracy": "⭐⭐⭐⭐"},
    "🟢 Conversational RAG": {"emoji": "🟢", "tagline": "Multi-Turn Memory", "how": "Remembers your full conversation history", "best_for": "Multi-turn chat & follow-ups", "speed": "⚡⚡", "accuracy": "⭐⭐⭐⭐"},
    "🔶 Rerank RAG":         {"emoji": "🔶", "tagline": "Two-Stage Precision", "how": "Fast vector retrieval → precise cross-encoder reranking", "best_for": "Legal, medical, finance", "speed": "⚡", "accuracy": "⭐⭐⭐⭐⭐"},
    "🟡 Contextual RAG":     {"emoji": "🟡", "tagline": "Token-Efficient", "how": "Retrieves chunks then compresses away irrelevant sentences", "best_for": "Long docs, token-budget apps", "speed": "⚡⚡", "accuracy": "⭐⭐⭐⭐"},
    "🔮 Self-Reflective RAG":{"emoji": "🔮", "tagline": "Self-Aware", "how": "Reflects on quality, retries with expanded query if needed", "best_for": "High-reliability use cases", "speed": "⚡", "accuracy": "⭐⭐⭐⭐⭐"},
    "✅ Corrective RAG":     {"emoji": "✅", "tagline": "Fact-Checker", "how": "Evaluates if retrieved docs actually answer the question", "best_for": "Compliance, medical, financial", "speed": "⚡", "accuracy": "⭐⭐⭐⭐⭐"},
    "🔀 Adaptive RAG":       {"emoji": "🔀", "tagline": "Smart Router", "how": "Classifies query complexity, routes to best RAG type", "best_for": "Mixed query types in production", "speed": "⚡⚡", "accuracy": "⭐⭐⭐⭐⭐"},
    "🔗 Multi-Hop RAG":      {"emoji": "🔗", "tagline": "Chain-of-Retrieval", "how": "Chains multiple retrievals: Hop1 → extract entity → Hop2", "best_for": "Multi-step questions", "speed": "⚡", "accuracy": "⭐⭐⭐⭐"},
}

selected_rag = st.radio(
    "Pick a RAG type:",
    list(ALL_RAG_TYPES.keys()),
    horizontal=True,
    key="rag_type_selector",
)

info = rag_info[selected_rag]
st.markdown(f"""
<div style="background:rgba(13,21,38,0.9);border:1px solid rgba(99,102,241,0.25);
     border-radius:14px;padding:1.2rem 1.5rem;display:flex;gap:1.2rem;align-items:flex-start;
     box-shadow:0 4px 20px rgba(99,102,241,0.08);margin-top:0.5rem">
  <div style="font-size:2.2rem;flex-shrink:0;line-height:1.2">{info['emoji']}</div>
  <div style="flex:1">
    <div style="display:flex;align-items:center;gap:0.6rem;flex-wrap:wrap;margin-bottom:0.3rem">
      <span style="font-size:1rem;font-weight:700;color:#e2e8f0">{selected_rag}</span>
      <span style="font-size:0.72rem;color:#8892A4;font-style:italic">{info['tagline']}</span>
    </div>
    <div style="font-size:0.84rem;color:#94a3b8;margin-bottom:0.4rem">
      <strong style="color:#818cf8">How:</strong> {info['how']}
    </div>
    <div style="display:flex;gap:1.5rem;flex-wrap:wrap">
      <span style="font-size:0.8rem;color:#94a3b8"><strong style="color:#6366f1">Best for:</strong> {info['best_for']}</span>
      <span style="font-size:0.8rem;color:#94a3b8"><strong style="color:#6366f1">Speed:</strong> {info['speed']}</span>
      <span style="font-size:0.8rem;color:#94a3b8"><strong style="color:#6366f1">Accuracy:</strong> {info['accuracy']}</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="fancy-div"></div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# STEP 3: ASK QUESTION
# ─────────────────────────────────────────────────────────────
step_header("3", "Ask a Question",
            "Type any question about your document above")

default_q = st.session_state.get("prefill_question", "")
question = st.text_input(
    "Your question:",
    value=default_q,
    placeholder="e.g. 'Who first walked on the Moon?' — ask anything about your document",
    key="question_input",
)

run_btn = st.button("🔍 Run RAG", type="primary", use_container_width=False)

# ─────────────────────────────────────────────────────────────
# RUN & SHOW RESULTS
# ─────────────────────────────────────────────────────────────
if run_btn and question.strip() and doc_text.strip():

    cache_key = f"rag_{selected_rag}_{hash(doc_text[:100])}"
    if cache_key not in st.session_state:
        with st.spinner("📚 Building index (chunking + embedding your text)…"):
            rag = ALL_RAG_TYPES[selected_rag]()
            n_chunks = rag.add_documents([doc_text], source=doc_label)
            st.session_state[cache_key] = rag
            st.session_state[f"{cache_key}_n"] = n_chunks
    else:
        rag = st.session_state[cache_key]
        n_chunks = st.session_state[f"{cache_key}_n"]

    with st.spinner(f"🔍 Running {selected_rag}…"):
        result = rag.ask(question, top_k=top_k, use_ollama=use_ollama)

    st.markdown('<div class="fancy-div"></div>', unsafe_allow_html=True)

    # Results header
    st.markdown("""
<div class="sec-head" style="margin-top:0">
  <div class="sec-label">Output</div>
  <div class="sec-title">📊 Results</div>
</div>
""", unsafe_allow_html=True)

    # Metrics
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("⏱️ Retrieval", f"{result.retrieval_ms:.0f} ms")
    with m2:
        st.metric("✍️ Generation", f"{result.generation_ms:.0f} ms")
    with m3:
        st.metric("📄 Chunks Searched", result.total_chunks_searched)
    with m4:
        top_score = result.top_doc.score if result.top_doc else 0
        st.metric("🎯 Top Match", f"{top_score:.2f}")

    st.markdown('<div class="fancy-div"></div>', unsafe_allow_html=True)

    # Two-column results layout
    left_col, right_col = st.columns([3, 2], gap="large")

    with left_col:
        # Answer box
        st.markdown(f"""
<div class="ans-box">
  <div class="ans-label">🤖 {result.rag_type}</div>
  <div class="ans-text">{result.answer}</div>
</div>
""", unsafe_allow_html=True)

        # Retrieved chunks
        st.markdown("""
<div style="font-size:0.75rem;font-weight:700;color:#6366f1;text-transform:uppercase;
     letter-spacing:0.08em;margin:1rem 0 0.6rem">📄 Retrieved Chunks — What RAG Found</div>
""", unsafe_allow_html=True)

        for i, doc in enumerate(result.retrieved_docs):
            sc = doc.score
            score_color = "#10b981" if sc > 0.6 else "#f59e0b" if sc > 0.35 else "#ef4444"
            score_pct = int(sc * 100)
            bdg_cls = "bdg-green" if sc > 0.6 else "bdg-amber" if sc > 0.35 else "bdg-red"

            highlighted = doc.content
            for word in question.lower().split():
                if len(word) > 3:
                    pattern = re.compile(re.escape(word), re.IGNORECASE)
                    highlighted = pattern.sub(
                        f'<mark style="background:#fbbf24;color:#1e293b;border-radius:3px;'
                        f'padding:0 2px">{word}</mark>',
                        highlighted
                    )

            st.markdown(f"""
<div class="chunk-card" style="border-left:3px solid {score_color}">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem">
    <div style="display:flex;align-items:center;gap:0.5rem">
      <span class="bdg {bdg_cls}">#{i+1}</span>
      <span style="color:{score_color};font-size:0.82rem;font-weight:700">
        {doc.retrieval_method.upper()} · {score_pct}%
      </span>
    </div>
    <span style="background:rgba(255,255,255,0.05);color:#64748b;padding:0.15rem 0.5rem;
         border-radius:999px;font-size:0.72rem">Chunk #{doc.chunk_index}</span>
  </div>
  <div style="color:#cbd5e1;font-size:0.88rem;line-height:1.65">{highlighted}</div>
</div>
""", unsafe_allow_html=True)

    with right_col:
        # Relevance bar chart
        st.markdown("""<div style="font-size:0.75rem;font-weight:700;color:#6366f1;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.5rem">📊 Relevance Scores</div>""", unsafe_allow_html=True)
        if result.retrieved_docs:
            bar_labels = [f"Chunk #{d.chunk_index} ({d.retrieval_method[:6]})" for d in result.retrieved_docs]
            bar_values = [d.score for d in result.retrieved_docs]
            bar_colors = ["#10b981" if s > 0.6 else "#f59e0b" if s > 0.35 else "#ef4444" for s in bar_values]

            fig = go.Figure(go.Bar(
                x=bar_values, y=bar_labels,
                orientation='h',
                marker_color=bar_colors,
                text=[f"{v:.2f}" for v in bar_values],
                textposition='outside',
            ))
            fig.update_layout(
                height=180 + len(result.retrieved_docs) * 40,
                paper_bgcolor="#050B18",
                plot_bgcolor="#0D1526",
                font=dict(color="#e2e8f0", size=11, family="Inter"),
                xaxis=dict(range=[0, 1.15], gridcolor="#1e293b", title="Score"),
                yaxis=dict(gridcolor="#1e293b"),
                margin=dict(l=5, r=30, t=5, b=5),
            )
            st.plotly_chart(fig, use_container_width=True)

        # Time breakdown
        st.markdown("""<div style="font-size:0.75rem;font-weight:700;color:#6366f1;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.5rem">⏱️ Time Breakdown</div>""", unsafe_allow_html=True)
        fig2 = go.Figure(go.Bar(
            x=["Retrieval", "Generation"],
            y=[result.retrieval_ms, result.generation_ms],
            marker_color=["#6366f1", "#10b981"],
            text=[f"{result.retrieval_ms:.0f}ms", f"{result.generation_ms:.0f}ms"],
            textposition='outside',
        ))
        fig2.update_layout(
            height=200,
            paper_bgcolor="#050B18",
            plot_bgcolor="#0D1526",
            font=dict(color="#e2e8f0", size=11, family="Inter"),
            yaxis=dict(title="ms", gridcolor="#1e293b"),
            xaxis=dict(gridcolor="#1e293b"),
            margin=dict(l=5, r=5, t=5, b=5),
        )
        st.plotly_chart(fig2, use_container_width=True)

        # Pipeline log
        st.markdown("""<div style="font-size:0.75rem;font-weight:700;color:#6366f1;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.5rem">🔄 Pipeline Steps Log</div>""", unsafe_allow_html=True)
        for i, step in enumerate(result.steps):
            st.markdown(f"""
<div class="log-item">
  <div class="log-n">{i+1}</div>
  <div>
    <div class="log-sname">{step['step']}</div>
    <div class="log-sdetail">{step['detail']}</div>
  </div>
</div>
""", unsafe_allow_html=True)

    # Conversation history (Conversational RAG only)
    if selected_rag == "🟢 Conversational RAG" and result.conversation_history:
        st.markdown('<div class="fancy-div"></div>', unsafe_allow_html=True)
        st.markdown(f"""
<div style="font-size:0.75rem;font-weight:700;color:#6366f1;text-transform:uppercase;
     letter-spacing:0.08em;margin-bottom:0.6rem">
  💬 Conversation History — {len(result.conversation_history)} turns in memory
</div>
""", unsafe_allow_html=True)

        for i, turn in enumerate(result.conversation_history):
            cq, ca = st.columns(2)
            with cq:
                st.markdown(f"""
<div style="background:rgba(13,21,38,0.8);border:1px solid rgba(99,102,241,0.15);
     border-radius:8px;padding:0.7rem;margin:0.25rem 0">
  <div style="font-size:0.68rem;font-weight:700;color:#6366f1;text-transform:uppercase;
       letter-spacing:0.08em;margin-bottom:0.3rem">Turn {i+1} — Question</div>
  <div style="color:#e2e8f0;font-size:0.87rem">{turn['q']}</div>
</div>
""", unsafe_allow_html=True)
            with ca:
                st.markdown(f"""
<div style="background:rgba(6,78,59,0.15);border:1px solid rgba(16,185,129,0.2);
     border-radius:8px;padding:0.7rem;margin:0.25rem 0">
  <div style="font-size:0.68rem;font-weight:700;color:#34d399;text-transform:uppercase;
       letter-spacing:0.08em;margin-bottom:0.3rem">Answer</div>
  <div style="color:#e2e8f0;font-size:0.87rem">{turn['a'][:120]}{'…' if len(turn['a'])>120 else ''}</div>
</div>
""", unsafe_allow_html=True)

elif run_btn and not question.strip():
    st.error("Please type a question first!")
elif run_btn and not doc_text.strip():
    st.error("Please add some documents first!")

# ── TIPS ─────────────────────────────────────────────────────
st.markdown('<div class="fancy-div"></div>', unsafe_allow_html=True)
with st.expander("💡 Tips for Better RAG Results"):
    tip1, tip2 = st.columns(2)
    with tip1:
        st.markdown("""
**Make your questions specific:**
- ❌ "Tell me about space"
- ✅ "Which mission first landed on the Moon?"

**The document should contain the answer:**
- RAG can only answer from what's in your documents
- Low scores (< 0.4) = answer not in docs
        """)
    with tip2:
        st.markdown("""
**Score guide:**
- 🟢 0.7–1.0 = Excellent match
- 🟡 0.4–0.7 = OK match
- 🔴 0.0–0.4 = Poor match (not in docs)

**Compare different RAG types:**
- Use Page 4 to run the same question through all 3 types side-by-side
        """)
