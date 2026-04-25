"""
pages/4_Compare_RAGs.py

Side-by-side comparison of all 3 RAG types on the same question.
See exactly HOW they differ:
  - Which chunks they retrieved
  - How long each took
  - What scores they gave
  - How answers compare
"""

import streamlit as st
import sys
import os
import plotly.graph_objects as go
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from rag_core import NaiveRAG, HybridRAG, ConversationalRAG, check_ollama_running
from data import get_topic_names, get_sample_doc

st.set_page_config(page_title="Compare RAG Types", page_icon="4️⃣", layout="wide")

st.title("4️⃣ Compare RAG Types Side-by-Side")
st.markdown("*Run the SAME question through all 3 RAG types. See what's different — and why.*")
st.divider()

with st.sidebar:
    st.markdown("## ⚙️ Settings")
    use_ollama = False
    if check_ollama_running():
        use_ollama = st.toggle("🦙 Use Ollama LLM", value=True)
    top_k = st.slider("Retrieve top-k", 1, 5, 3)
    st.divider()
    st.markdown("## 🗺️ Navigation")
    st.page_link("app.py", label="🏠 Home")
    st.page_link("pages/1_When_To_Use_RAG.py", label="1️⃣ When to Use RAG")
    st.page_link("pages/2_How_RAG_Works.py", label="2️⃣ How RAG Works")
    st.page_link("pages/3_Test_Any_RAG.py", label="3️⃣ Test Any RAG ⭐")
    st.page_link("pages/4_Compare_RAGs.py", label="4️⃣ Compare RAG Types")

# ── SETUP ──────────────────────────────────────────────────
st.subheader("📄 Choose Knowledge Base")

col1, col2 = st.columns([2, 1])
with col1:
    topic_names = get_topic_names()
    selected_topic = st.selectbox("Select topic:", topic_names, key="compare_topic")
    topic_data = get_sample_doc(selected_topic)

    with st.expander("Preview document"):
        st.text(topic_data["text"][:500] + "...")

with col2:
    st.markdown("**Try these questions:**")
    for q in topic_data["suggested_questions"][:3]:
        if st.button(f"❓ {q}", key=f"cmp_{q[:15]}", use_container_width=True):
            st.session_state["cmp_question"] = q

question = st.text_input(
    "Question to compare across all RAG types:",
    value=st.session_state.get("cmp_question", ""),
    placeholder="Ask anything about the topic above...",
    key="compare_question",
)

run_compare = st.button("⚖️ Compare All 3 RAG Types", type="primary", use_container_width=False)

# ── RUN COMPARISON ──────────────────────────────────────────
if run_compare and question.strip():

    doc_text = topic_data["text"]
    results = {}

    rag_configs = {
        "🔵 Naive RAG": NaiveRAG,
        "🟣 Hybrid RAG": HybridRAG,
        "🟢 Conversational RAG": ConversationalRAG,
    }

    progress = st.progress(0, text="Running comparison...")
    for i, (name, RAGClass) in enumerate(rag_configs.items()):
        progress.progress((i + 1) / len(rag_configs), text=f"Running {name}...")
        rag = RAGClass()
        rag.add_documents([doc_text], source=selected_topic)
        results[name] = rag.ask(question, top_k=top_k, use_ollama=use_ollama)
        time.sleep(0.1)  # Let progress bar render

    progress.empty()

    st.divider()
    st.subheader("📊 Comparison Results")

    # ── SUMMARY METRICS ─────────────────────────────────────
    st.markdown("#### ⚡ Quick Stats")
    mc = st.columns(len(results))

    for col, (name, result) in zip(mc, results.items()):
        with col:
            top_score = result.top_doc.score if result.top_doc else 0
            st.markdown(f"""
<div style="background:#1e293b;border:1px solid #334155;border-radius:12px;padding:1.2rem;text-align:center">
  <div style="font-size:1.5rem">{name.split()[0]}</div>
  <div style="color:#e2e8f0;font-weight:700;font-size:0.95rem;margin:0.3rem 0">{name[2:]}</div>
  <hr style="border-color:#334155;margin:0.5rem 0">
  <div style="color:#6366f1;font-size:0.85rem">Retrieval: {result.retrieval_ms:.0f}ms</div>
  <div style="color:#10b981;font-size:0.85rem">Top Score: {top_score:.2f}</div>
  <div style="color:#f59e0b;font-size:0.85rem">Chunks: {result.total_chunks_searched}</div>
</div>
""", unsafe_allow_html=True)

    # ── COMPARISON CHART: Latency ────────────────────────────
    st.markdown("#### ⏱️ Latency Comparison")
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        fig_lat = go.Figure()
        names = list(results.keys())
        ret_times = [r.retrieval_ms for r in results.values()]
        gen_times = [r.generation_ms for r in results.values()]

        fig_lat.add_trace(go.Bar(name="Retrieval", x=names, y=ret_times,
                                  marker_color="#6366f1",
                                  text=[f"{v:.0f}ms" for v in ret_times],
                                  textposition='outside'))
        fig_lat.add_trace(go.Bar(name="Generation", x=names, y=gen_times,
                                  marker_color="#10b981",
                                  text=[f"{v:.0f}ms" for v in gen_times],
                                  textposition='outside'))

        fig_lat.update_layout(
            title="Latency (ms) — lower is faster",
            barmode='group',
            height=320,
            paper_bgcolor="#0f172a",
            plot_bgcolor="#1e293b",
            font=dict(color="#e2e8f0"),
            xaxis=dict(gridcolor="#334155"),
            yaxis=dict(gridcolor="#334155", title="ms"),
            legend=dict(bgcolor="#1e293b"),
        )
        st.plotly_chart(fig_lat, use_container_width=True)

    with col_chart2:
        fig_score = go.Figure()
        for name, result in results.items():
            chunk_labels = [f"#{d.chunk_index}" for d in result.retrieved_docs]
            chunk_scores = [d.score for d in result.retrieved_docs]
            fig_score.add_trace(go.Bar(
                name=name[2:],
                x=chunk_labels[:top_k],
                y=chunk_scores[:top_k],
                text=[f"{v:.2f}" for v in chunk_scores[:top_k]],
                textposition='outside',
            ))

        fig_score.update_layout(
            title="Top Retrieved Chunk Scores",
            barmode='group',
            height=320,
            paper_bgcolor="#0f172a",
            plot_bgcolor="#1e293b",
            font=dict(color="#e2e8f0"),
            xaxis=dict(gridcolor="#334155", title="Chunk #"),
            yaxis=dict(gridcolor="#334155", title="Score", range=[0, 1.1]),
            legend=dict(bgcolor="#1e293b"),
        )
        st.plotly_chart(fig_score, use_container_width=True)

    st.divider()

    # ── SIDE-BY-SIDE ANSWERS ─────────────────────────────────
    st.markdown("#### 💬 Answers Side by Side")
    answer_cols = st.columns(3)
    answer_borders = ["#3B82F6", "#8B5CF6", "#10B981"]

    for col, (name, result), border in zip(answer_cols, results.items(), answer_borders):
        with col:
            st.markdown(f"**{name}**")
            st.markdown(f"""
<div style="background:#0f172a;border:1px solid {border};border-radius:12px;padding:1.2rem;min-height:150px">
  <div style="color:#e2e8f0;font-size:0.9rem;line-height:1.6">{result.answer}</div>
</div>
""", unsafe_allow_html=True)

    st.divider()

    # ── RETRIEVED CHUNKS COMPARISON ──────────────────────────
    st.markdown("#### 📄 Which Chunks Did Each RAG Retrieve?")
    rc = st.columns(3)

    for col, (name, result), border in zip(rc, results.items(), answer_borders):
        with col:
            st.markdown(f"**{name}**")
            for i, doc in enumerate(result.retrieved_docs):
                score_color = "#10b981" if doc.score > 0.6 else "#f59e0b" if doc.score > 0.35 else "#ef4444"
                st.markdown(f"""
<div style="background:#1e293b;border-left:3px solid {score_color};border-radius:6px;padding:0.7rem;margin:0.3rem 0">
  <small style="color:{score_color}">#{i+1} Score: {doc.score:.2f} | {doc.retrieval_method}</small><br>
  <span style="color:#e2e8f0;font-size:0.82rem">{doc.content[:120]}{'...' if len(doc.content)>120 else ''}</span>
</div>
""", unsafe_allow_html=True)

    st.divider()

    # ── INSIGHTS ─────────────────────────────────────────────
    st.markdown("#### 🧠 What Does This Tell You?")

    all_ret_times = {n: r.retrieval_ms for n, r in results.items()}
    fastest = min(all_ret_times, key=all_ret_times.get)
    all_scores = {n: r.top_doc.score if r.top_doc else 0 for n, r in results.items()}
    highest_score = max(all_scores, key=all_scores.get)

    ic1, ic2, ic3 = st.columns(3)
    with ic1:
        st.info(f"⚡ **Fastest retrieval:** {fastest[2:]} ({all_ret_times[fastest]:.0f}ms)\n\nFor latency-critical systems, this is your choice.")
    with ic2:
        st.success(f"🎯 **Highest match score:** {highest_score[2:]}\n\n({all_scores[highest_score]:.2f}) — Best at finding relevant content for this query.")
    with ic3:
        # Check if hybrid and naive found different chunks
        naive_chunks = {d.chunk_index for d in results.get("🔵 Naive RAG", type('', (), {'retrieved_docs': []})()).retrieved_docs} if "🔵 Naive RAG" in results else set()
        hybrid_chunks = {d.chunk_index for d in results.get("🟣 Hybrid RAG", type('', (), {'retrieved_docs': []})()).retrieved_docs} if "🟣 Hybrid RAG" in results else set()
        overlap = len(naive_chunks & hybrid_chunks)
        st.warning(f"🔀 **Naive vs Hybrid overlap:** {overlap}/{top_k} same chunks\n\nIf different, Hybrid found something Naive missed.")

elif run_compare and not question.strip():
    st.error("Please type a question first!")

else:
    # Show example comparison
    st.info("👆 Select a topic, type a question, and click **Compare All 3 RAG Types** to see how they differ.")

    st.markdown("### 🤔 What to Look For When Comparing")
    st.markdown("""
| Observation | What It Means |
|-------------|---------------|
| **Hybrid has higher score than Naive** | Your query had keywords (names, codes) that helped BM25 |
| **Same answer from all 3** | The answer was clearly in the document — all methods found it |
| **Different answers** | They retrieved different chunks — one may be more relevant |
| **Naive is fastest** | Vector-only search has less overhead |
| **Conversational is slowest** | It also searches conversation history on top of documents |
| **Score below 0.35** | The answer probably isn't in your documents |
    """)
