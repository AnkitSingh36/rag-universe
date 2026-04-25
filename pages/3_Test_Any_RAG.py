"""
pages/3_Test_Any_RAG.py

The main demo page.
Users can:
  1. Choose or paste their own documents
  2. Select any RAG type
  3. Ask a question
  4. See the FULL visualization of what happened:
     - Which chunks were created
     - Which chunks were retrieved (with scores)
     - Which parts of the original text are highlighted
     - How long each step took
"""

import streamlit as st
import time
import sys
import os
import re
import plotly.graph_objects as go

# Make sure rag_core is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from rag_core import NaiveRAG, HybridRAG, ConversationalRAG, ALL_RAG_TYPES, check_ollama_running
from rag_core.utils import chunk_text
from data import get_topic_names, get_sample_doc

st.set_page_config(page_title="Test Any RAG", page_icon="⭐", layout="wide")

st.title("⭐ Test Any RAG — Live Demo")
st.markdown("*Load any document, choose a RAG type, ask a question, see exactly how it works.*")
st.divider()

# ─────────────────────────────────────────────────────────────────
# SIDEBAR: Settings
# ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    use_ollama = False
    if check_ollama_running():
        use_ollama = st.toggle("🦙 Use Ollama LLM", value=True, help="Ollama detected! Enables real LLM answers.")
        st.success("✅ Ollama is running")
    else:
        st.info("💡 Demo mode (no LLM needed)\nInstall [Ollama](https://ollama.ai) for richer answers")

    top_k = st.slider("Retrieve top-k chunks", 1, 5, 3)

    st.divider()
    st.markdown("## 🗺️ Navigation")
    st.page_link("app.py", label="🏠 Home")
    st.page_link("pages/1_When_To_Use_RAG.py", label="1️⃣ When to Use RAG")
    st.page_link("pages/2_How_RAG_Works.py", label="2️⃣ How RAG Works")
    st.page_link("pages/3_Test_Any_RAG.py", label="3️⃣ Test Any RAG ⭐")
    st.page_link("pages/4_Compare_RAGs.py", label="4️⃣ Compare RAG Types")


# ─────────────────────────────────────────────────────────────────
# STEP 1: Load Documents
# ─────────────────────────────────────────────────────────────────
st.subheader("📄 Step 1: Choose Your Knowledge Base")

doc_source = st.radio(
    "Where should RAG get its knowledge?",
    ["📚 Use a sample topic", "✏️ Paste your own text"],
    horizontal=True,
)

doc_text = ""
doc_label = "document"

if "📚" in doc_source:
    topic_names = get_topic_names()
    selected_topic = st.selectbox("Pick a topic:", topic_names)
    topic_data = get_sample_doc(selected_topic)

    col1, col2 = st.columns([2, 1])
    with col1:
        with st.expander(f"📖 Preview: {selected_topic}", expanded=True):
            st.markdown(topic_data["text"][:800] + "...")

    with col2:
        st.markdown("**💡 Try asking:**")
        for q in topic_data["suggested_questions"][:4]:
            if st.button(f"❓ {q}", key=f"btn_{q[:20]}", use_container_width=True):
                st.session_state["prefill_question"] = q

    doc_text = topic_data["text"]
    doc_label = selected_topic

else:
    doc_text = st.text_area(
        "Paste any text here (news article, Wikipedia, your notes, anything!):",
        height=200,
        placeholder="Paste any text here. Can be from any topic.\n\nExample: Copy-paste a Wikipedia article, a news story, your study notes, a company document...",
    )

if not doc_text.strip():
    st.warning("👆 Please select a topic or paste some text to continue.")
    st.stop()

# Show chunking preview
with st.expander("🔪 See how your text gets chunked (Step 1 of RAG pipeline)"):
    chunks_preview = chunk_text(doc_text, 300, 50)
    st.markdown(f"**Your text → {len(chunks_preview)} chunks**")

    cols = st.columns(3)
    for i, chunk in enumerate(chunks_preview[:6]):
        with cols[i % 3]:
            st.markdown(f"""
<div style="background:#1e293b;border:1px solid #334155;border-radius:8px;padding:0.8rem;margin:0.3rem 0;height:120px;overflow:hidden">
<small style="color:#6366f1;font-weight:700">Chunk #{i+1}</small><br>
<span style="color:#e2e8f0;font-size:0.82rem">{chunk[:150]}{'...' if len(chunk)>150 else ''}</span>
</div>
""", unsafe_allow_html=True)
    if len(chunks_preview) > 6:
        st.caption(f"... and {len(chunks_preview) - 6} more chunks")

st.divider()

# ─────────────────────────────────────────────────────────────────
# STEP 2: Choose RAG Type
# ─────────────────────────────────────────────────────────────────
st.subheader("🔧 Step 2: Choose RAG Type")

rag_col1, rag_col2, rag_col3 = st.columns(3)

rag_info = {
    "🔵 Naive RAG": {
        "emoji": "🔵",
        "tagline": "The Simple One",
        "how": "Converts everything to vectors, finds closest match",
        "best_for": "Simple factual questions",
        "speed": "⚡⚡⚡",
        "accuracy": "⭐⭐⭐",
    },
    "🟣 Hybrid RAG": {
        "emoji": "🟣",
        "tagline": "The Smart One",
        "how": "Keyword match + Semantic match, combined",
        "best_for": "Mixed keywords + meaning",
        "speed": "⚡⚡",
        "accuracy": "⭐⭐⭐⭐",
    },
    "🟢 Conversational RAG": {
        "emoji": "🟢",
        "tagline": "The Memory One",
        "how": "Remembers your full conversation",
        "best_for": "Multi-turn chat / follow-ups",
        "speed": "⚡⚡",
        "accuracy": "⭐⭐⭐⭐",
    },
    "🔶 Rerank RAG": {
        "emoji": "🔶",
        "tagline": "The Precise One",
        "how": "Fast vector search → precise cross-encoder reranking",
        "best_for": "Legal, medical, finance (accuracy critical)",
        "speed": "⚡",
        "accuracy": "⭐⭐⭐⭐⭐",
    },
    "🟡 Contextual RAG": {
        "emoji": "🟡",
        "tagline": "The Efficient One",
        "how": "Retrieves chunks then compresses away irrelevant sentences",
        "best_for": "Long documents, token-budget-constrained apps",
        "speed": "⚡⚡",
        "accuracy": "⭐⭐⭐⭐",
    },
    "🔮 Self-Reflective RAG": {
        "emoji": "🔮",
        "tagline": "The Self-Aware One",
        "how": "Reflects on retrieval quality, retries if docs are irrelevant",
        "best_for": "High-reliability use cases, fact-checking",
        "speed": "⚡",
        "accuracy": "⭐⭐⭐⭐⭐",
    },
    "✅ Corrective RAG": {
        "emoji": "✅",
        "tagline": "The Fact-Checker",
        "how": "Evaluates if retrieved docs actually answer the question",
        "best_for": "Compliance, medical, financial — wrong answer = big problem",
        "speed": "⚡",
        "accuracy": "⭐⭐⭐⭐⭐",
    },
    "🔀 Adaptive RAG": {
        "emoji": "🔀",
        "tagline": "The Smart Router",
        "how": "Classifies query complexity, routes to best RAG type",
        "best_for": "Mixed query types in production",
        "speed": "⚡⚡",
        "accuracy": "⭐⭐⭐⭐⭐",
    },
    "🔗 Multi-Hop RAG": {
        "emoji": "🔗",
        "tagline": "The Chain-of-Thought One",
        "how": "Chains multiple retrievals: Hop1 → extract entity → Hop2",
        "best_for": "Multi-step questions requiring intermediate lookups",
        "speed": "⚡",
        "accuracy": "⭐⭐⭐⭐",
    },
}

selected_rag = st.radio(
    "Pick a RAG type to test:",
    list(ALL_RAG_TYPES.keys()),
    horizontal=True,
    key="rag_type_selector",
)

info = rag_info[selected_rag]
st.markdown(f"""
<div style="background:#1e293b;border:1px solid #6366f1;border-radius:12px;padding:1.2rem;display:flex;gap:1.5rem;align-items:center">
  <span style="font-size:2.5rem">{info['emoji']}</span>
  <div>
    <strong style="color:#e2e8f0;font-size:1.1rem">{selected_rag}</strong> — <em style="color:#94a3b8">{info['tagline']}</em><br>
    <span style="color:#94a3b8;font-size:0.9rem">How: {info['how']}</span><br>
    <span style="color:#94a3b8;font-size:0.9rem">Best for: {info['best_for']} | Speed: {info['speed']} | Accuracy: {info['accuracy']}</span>
  </div>
</div>
""", unsafe_allow_html=True)

st.divider()

# ─────────────────────────────────────────────────────────────────
# STEP 3: Ask Question & Run
# ─────────────────────────────────────────────────────────────────
st.subheader("❓ Step 3: Ask a Question")

# Pre-fill from topic suggestion or session state
default_q = st.session_state.get("prefill_question", "")

question = st.text_input(
    "Type your question:",
    value=default_q,
    placeholder="e.g. 'Who first walked on the Moon?' or any question about your document above",
    key="question_input",
)

run_button = st.button("🔍 Run RAG", type="primary", use_container_width=False)

# ─────────────────────────────────────────────────────────────────
# RUN RAG & SHOW RESULTS
# ─────────────────────────────────────────────────────────────────
if run_button and question.strip() and doc_text.strip():

    # Build RAG (or reuse from session if same doc + type)
    cache_key = f"rag_{selected_rag}_{hash(doc_text[:100])}"
    if cache_key not in st.session_state:
        with st.spinner("📚 Building index (loading embedding model, chunking, embedding)..."):
            rag = ALL_RAG_TYPES[selected_rag]()
            n_chunks = rag.add_documents([doc_text], source=doc_label)
            st.session_state[cache_key] = rag
            st.session_state[f"{cache_key}_n"] = n_chunks
    else:
        rag = st.session_state[cache_key]
        n_chunks = st.session_state[f"{cache_key}_n"]

    # Run query
    with st.spinner(f"🔍 Running {selected_rag}..."):
        result = rag.ask(question, top_k=top_k, use_ollama=use_ollama)

    # ── RESULTS ──────────────────────────────────────────
    st.divider()
    st.subheader("📊 Results")

    # Metrics row
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("🔍 Retrieval Time", f"{result.retrieval_ms:.0f}ms")
    with m2:
        st.metric("✍️ Generation Time", f"{result.generation_ms:.0f}ms")
    with m3:
        st.metric("📄 Chunks Searched", result.total_chunks_searched)
    with m4:
        st.metric("🎯 Top Match Score", f"{result.top_doc.score:.2f}" if result.top_doc else "N/A")

    st.divider()

    # Main results layout
    left, right = st.columns([3, 2])

    # ── LEFT: ANSWER + RETRIEVED DOCS ────────────────────
    with left:
        # Answer box
        st.markdown("### 💬 Answer")
        st.markdown(f"""
<div style="background:linear-gradient(135deg,#064e3b,#022c22);border:1px solid #10b981;border-radius:12px;padding:1.5rem;margin-bottom:1rem">
<div style="color:#6ee7b7;font-size:0.8rem;font-weight:700;margin-bottom:0.5rem">🤖 {result.rag_type}</div>
<div style="color:#e2e8f0;font-size:1rem;line-height:1.6">{result.answer}</div>
</div>
""", unsafe_allow_html=True)

        # Retrieved chunks
        st.markdown("### 📄 Retrieved Chunks (What RAG found)")
        for i, doc in enumerate(result.retrieved_docs):
            score_color = "#10b981" if doc.score > 0.6 else "#f59e0b" if doc.score > 0.35 else "#ef4444"
            score_pct = int(doc.score * 100)

            # Highlight query terms in the chunk
            highlighted = doc.content
            for word in question.lower().split():
                if len(word) > 3:
                    pattern = re.compile(re.escape(word), re.IGNORECASE)
                    highlighted = pattern.sub(
                        f'<mark style="background:#fbbf24;color:#1e293b;border-radius:3px">{word}</mark>',
                        highlighted
                    )

            st.markdown(f"""
<div style="background:#1e293b;border:1px solid #334155;border-left:4px solid {score_color};border-radius:8px;padding:1rem;margin:0.5rem 0">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem">
    <span style="color:{score_color};font-weight:700;font-size:0.85rem">
      #{i+1} {doc.retrieval_method.upper()} — Score: {score_pct}%
    </span>
    <span style="background:{score_color}22;color:{score_color};padding:2px 8px;border-radius:999px;font-size:0.75rem">
      Chunk #{doc.chunk_index}
    </span>
  </div>
  <div style="background:#1a0a00;border-radius:4px;padding:0 0 0 0">
    <div style="color:#cbd5e1;font-size:0.9rem;line-height:1.6">{highlighted}</div>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── RIGHT: VISUALIZATIONS ────────────────────────────
    with right:
        # Relevance bar chart
        st.markdown("### 📊 Relevance Scores")
        if result.retrieved_docs:
            bar_labels = [f"Chunk #{d.chunk_index} ({d.retrieval_method[:6]})" for d in result.retrieved_docs]
            bar_values = [d.score for d in result.retrieved_docs]
            bar_colors = [
                "#10b981" if s > 0.6 else "#f59e0b" if s > 0.35 else "#ef4444"
                for s in bar_values
            ]

            fig = go.Figure(go.Bar(
                x=bar_values,
                y=bar_labels,
                orientation='h',
                marker_color=bar_colors,
                text=[f"{v:.2f}" for v in bar_values],
                textposition='outside',
            ))
            fig.update_layout(
                height=200 + len(result.retrieved_docs) * 40,
                paper_bgcolor="#0f172a",
                plot_bgcolor="#1e293b",
                font=dict(color="#e2e8f0", size=11),
                xaxis=dict(range=[0, 1.1], gridcolor="#334155", title="Score"),
                yaxis=dict(gridcolor="#334155"),
                margin=dict(l=10, r=10, t=10, b=10),
            )
            st.plotly_chart(fig, use_container_width=True)

        # Latency breakdown
        st.markdown("### ⏱️ Time Breakdown")
        fig2 = go.Figure(go.Bar(
            x=["Retrieval", "Generation"],
            y=[result.retrieval_ms, result.generation_ms],
            marker_color=["#6366f1", "#10b981"],
            text=[f"{result.retrieval_ms:.0f}ms", f"{result.generation_ms:.0f}ms"],
            textposition='outside',
        ))
        fig2.update_layout(
            height=200,
            paper_bgcolor="#0f172a",
            plot_bgcolor="#1e293b",
            font=dict(color="#e2e8f0", size=11),
            yaxis=dict(title="ms", gridcolor="#334155"),
            xaxis=dict(gridcolor="#334155"),
            margin=dict(l=10, r=10, t=10, b=10),
        )
        st.plotly_chart(fig2, use_container_width=True)

        # Pipeline steps log
        st.markdown("### 🔄 Pipeline Steps Log")
        for i, step in enumerate(result.steps):
            st.markdown(f"""
<div style="display:flex;gap:0.8rem;align-items:flex-start;margin:0.4rem 0">
  <div style="background:#6366f1;color:white;border-radius:999px;width:22px;height:22px;display:flex;align-items:center;justify-content:center;font-size:0.75rem;font-weight:700;flex-shrink:0">{i+1}</div>
  <div>
    <strong style="color:#e2e8f0;font-size:0.85rem">{step['step']}</strong><br>
    <span style="color:#94a3b8;font-size:0.8rem">{step['detail']}</span>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── CONVERSATION HISTORY (for Conversational RAG) ────
    if selected_rag == "Conversational RAG" and result.conversation_history:
        st.divider()
        st.markdown("### 💬 Conversation History")
        st.markdown(f"*{len(result.conversation_history)} turns stored in memory*")

        for i, turn in enumerate(result.conversation_history):
            col_q, col_a = st.columns([1, 1])
            with col_q:
                st.markdown(f"""
<div style="background:#1e293b;border:1px solid #334155;border-radius:8px;padding:0.8rem;margin:0.3rem 0">
  <small style="color:#6366f1">Turn {i+1} — Question</small><br>
  <span style="color:#e2e8f0;font-size:0.9rem">{turn['q']}</span>
</div>
""", unsafe_allow_html=True)
            with col_a:
                st.markdown(f"""
<div style="background:#064e3b22;border:1px solid #10b981;border-radius:8px;padding:0.8rem;margin:0.3rem 0">
  <small style="color:#10b981">Answer</small><br>
  <span style="color:#e2e8f0;font-size:0.9rem">{turn['a'][:120]}{'...' if len(turn['a'])>120 else ''}</span>
</div>
""", unsafe_allow_html=True)

elif run_button and not question.strip():
    st.error("Please type a question first!")
elif run_button and not doc_text.strip():
    st.error("Please add some documents first!")

# ─────────────────────────────────────────────────────────────────
# TIP BOXES
# ─────────────────────────────────────────────────────────────────
st.divider()
with st.expander("💡 Tips for Better RAG Results"):
    st.markdown("""
**Make your questions specific:**
- ❌ "Tell me about space"
- ✅ "Which mission first landed on the Moon?"

**The document should contain the answer:**
- RAG can only answer from what's in your documents
- If the answer isn't there, RAG will get low scores

**Try different RAG types on the same question:**
- Use the Compare page (Page 4) to see differences

**Relevance score guide:**
- 0.7 - 1.0 = Great match ✅
- 0.4 - 0.7 = OK match ⚠️
- 0.0 - 0.4 = Poor match ❌ (answer not in your docs)
    """)
