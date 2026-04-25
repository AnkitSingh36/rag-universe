"""
pages/4_Compare_RAGs.py
Side-by-side comparison of all 3 RAG types on the same question.
"""

import streamlit as st
import sys, os
import plotly.graph_objects as go
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from rag_core import NaiveRAG, HybridRAG, ConversationalRAG, check_ollama_running
from data import get_topic_names, get_sample_doc
from ui_styles import apply_global_styles, sidebar_nav

st.set_page_config(page_title="Compare RAG Types", page_icon="4️⃣", layout="wide")
apply_global_styles()

# ── PAGE HEADER ───────────────────────────────────────────────
st.markdown("""
<div style="padding:1.5rem 0 0.5rem">
  <div class="sec-label">Page 4 of 6</div>
  <h1 style="font-size:2rem;font-weight:800;color:#F0F4FF;margin:0.3rem 0;letter-spacing:-0.02em">
    Compare RAG Types Side-by-Side
  </h1>
  <p style="color:#8892A4;font-size:0.95rem;margin:0">
    Run the <strong style="color:#c7d2fe">same question</strong> through all 3 RAG types.
    See what's different — and why.
  </p>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="fancy-div"></div>', unsafe_allow_html=True)

# ── SIDEBAR SETTINGS ──────────────────────────────────────────
with st.sidebar:
    st.markdown("""<div style="font-size:0.68rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:#6366f1;margin-bottom:0.5rem">⚙️ Settings</div>""", unsafe_allow_html=True)
    use_ollama = False
    if check_ollama_running():
        use_ollama = st.toggle("🦙 Use Ollama LLM", value=True)
        st.success("✅ Ollama ready")
    else:
        st.info("💡 Demo mode")
    top_k = st.slider("Retrieve top-k", 1, 5, 3)

sidebar_nav("4")

# ── SETUP ─────────────────────────────────────────────────────
st.markdown("""
<div class="sec-head">
  <div class="sec-label">Setup</div>
  <div class="sec-title">📄 Choose Your Knowledge Base & Question</div>
</div>
""", unsafe_allow_html=True)

col_setup1, col_setup2 = st.columns([2, 1], gap="large")
with col_setup1:
    topic_names = get_topic_names()
    selected_topic = st.selectbox("Select topic:", topic_names, key="compare_topic")
    topic_data = get_sample_doc(selected_topic)

    with st.expander(f"📖 Preview: {selected_topic}"):
        st.text(topic_data["text"][:500] + "…")

with col_setup2:
    st.markdown("""<div style="font-size:0.75rem;font-weight:700;color:#6366f1;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.5rem">💡 Try These Questions</div>""", unsafe_allow_html=True)
    for q in topic_data["suggested_questions"][:3]:
        if st.button(f"❓ {q}", key=f"cmp_{q[:15]}", use_container_width=True):
            st.session_state["cmp_question"] = q

question = st.text_input(
    "Question to compare across all RAG types:",
    value=st.session_state.get("cmp_question", ""),
    placeholder="Ask anything about the topic above…",
    key="compare_question",
)

run_compare = st.button("⚖️ Compare All 3 RAG Types", type="primary")

# ── RUN COMPARISON ────────────────────────────────────────────
if run_compare and question.strip():

    doc_text = topic_data["text"]
    results = {}
    rag_configs = {
        "🔵 Naive RAG": NaiveRAG,
        "🟣 Hybrid RAG": HybridRAG,
        "🟢 Conversational RAG": ConversationalRAG,
    }

    progress_bar = st.progress(0)
    status_text = st.empty()

    for i, (name, RAGClass) in enumerate(rag_configs.items()):
        status_text.markdown(f'<div style="color:#94a3b8;font-size:0.88rem">🔄 Running {name}…</div>', unsafe_allow_html=True)
        progress_bar.progress((i + 1) / len(rag_configs))
        rag = RAGClass()
        rag.add_documents([doc_text], source=selected_topic)
        results[name] = rag.ask(question, top_k=top_k, use_ollama=use_ollama)
        time.sleep(0.1)

    progress_bar.empty()
    status_text.empty()

    st.markdown('<div class="fancy-div"></div>', unsafe_allow_html=True)
    st.markdown("""
<div class="sec-head" style="margin-top:0">
  <div class="sec-label">Comparison Results</div>
  <div class="sec-title">📊 Head-to-Head Analysis</div>
</div>
""", unsafe_allow_html=True)

    # ── SUMMARY STATS ──────────────────────────────────────────
    rag_borders = ["#3B82F6", "#8B5CF6", "#10B981"]
    stat_cols = st.columns(len(results))

    for col, (name, result), border in zip(stat_cols, results.items(), rag_borders):
        top_score = result.top_doc.score if result.top_doc else 0
        sc_cls = "bdg-green" if top_score > 0.6 else "bdg-amber" if top_score > 0.35 else "bdg-red"
        with col:
            st.markdown(f"""
<div class="cmp-card" style="border-top:3px solid {border}">
  <div style="font-size:1.8rem;margin-bottom:0.3rem">{name.split()[0]}</div>
  <div style="font-size:0.92rem;font-weight:700;color:#F0F4FF;margin-bottom:0.7rem">{name[2:]}</div>
  <div style="height:1px;background:rgba(255,255,255,0.06);margin:0.6rem 0"></div>
  <div style="display:flex;flex-direction:column;gap:0.3rem">
    <div style="font-size:0.82rem;color:#94a3b8">
      <span style="color:#6366f1;font-weight:600">Retrieval:</span> {result.retrieval_ms:.0f} ms
    </div>
    <div style="font-size:0.82rem;color:#94a3b8">
      <span style="color:#10b981;font-weight:600">Top Score:</span>
      <span class="bdg {sc_cls}" style="margin-left:0.3rem">{top_score:.2f}</span>
    </div>
    <div style="font-size:0.82rem;color:#94a3b8">
      <span style="color:#f59e0b;font-weight:600">Chunks:</span> {result.total_chunks_searched}
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    st.markdown('<div class="fancy-div"></div>', unsafe_allow_html=True)

    # ── CHARTS ─────────────────────────────────────────────────
    chart1, chart2 = st.columns(2, gap="large")

    with chart1:
        st.markdown("""<div style="font-size:0.75rem;font-weight:700;color:#6366f1;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.5rem">⏱️ Latency Comparison</div>""", unsafe_allow_html=True)
        names = list(results.keys())
        ret_times = [r.retrieval_ms for r in results.values()]
        gen_times = [r.generation_ms for r in results.values()]

        fig_lat = go.Figure()
        fig_lat.add_trace(go.Bar(name="Retrieval", x=names, y=ret_times,
                                  marker_color="#6366f1",
                                  text=[f"{v:.0f}ms" for v in ret_times],
                                  textposition='outside'))
        fig_lat.add_trace(go.Bar(name="Generation", x=names, y=gen_times,
                                  marker_color="#10b981",
                                  text=[f"{v:.0f}ms" for v in gen_times],
                                  textposition='outside'))
        fig_lat.update_layout(
            barmode='group', height=300,
            paper_bgcolor="#050B18", plot_bgcolor="#0D1526",
            font=dict(color="#e2e8f0", family="Inter"),
            xaxis=dict(gridcolor="#1e293b"),
            yaxis=dict(gridcolor="#1e293b", title="ms"),
            legend=dict(bgcolor="rgba(13,21,38,0.9)", bordercolor="rgba(99,102,241,0.2)", borderwidth=1),
            margin=dict(l=10, r=10, t=10, b=10),
        )
        st.plotly_chart(fig_lat, use_container_width=True)

    with chart2:
        st.markdown("""<div style="font-size:0.75rem;font-weight:700;color:#6366f1;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.5rem">🎯 Retrieved Chunk Scores</div>""", unsafe_allow_html=True)
        fig_score = go.Figure()
        palette = ["#3B82F6", "#8B5CF6", "#10B981"]
        for (name, result), color in zip(results.items(), palette):
            chunk_labels = [f"#{d.chunk_index}" for d in result.retrieved_docs]
            chunk_scores = [d.score for d in result.retrieved_docs]
            fig_score.add_trace(go.Bar(
                name=name[2:], x=chunk_labels[:top_k], y=chunk_scores[:top_k],
                marker_color=color,
                text=[f"{v:.2f}" for v in chunk_scores[:top_k]],
                textposition='outside',
            ))
        fig_score.update_layout(
            barmode='group', height=300,
            paper_bgcolor="#050B18", plot_bgcolor="#0D1526",
            font=dict(color="#e2e8f0", family="Inter"),
            xaxis=dict(gridcolor="#1e293b", title="Chunk #"),
            yaxis=dict(gridcolor="#1e293b", title="Score", range=[0, 1.15]),
            legend=dict(bgcolor="rgba(13,21,38,0.9)", bordercolor="rgba(99,102,241,0.2)", borderwidth=1),
            margin=dict(l=10, r=10, t=10, b=10),
        )
        st.plotly_chart(fig_score, use_container_width=True)

    st.markdown('<div class="fancy-div"></div>', unsafe_allow_html=True)

    # ── ANSWERS SIDE BY SIDE ───────────────────────────────────
    st.markdown("""<div style="font-size:0.75rem;font-weight:700;color:#6366f1;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.8rem">💬 Answers Side by Side</div>""", unsafe_allow_html=True)
    ans_cols = st.columns(3, gap="medium")

    for col, (name, result), border in zip(ans_cols, results.items(), rag_borders):
        with col:
            st.markdown(f"""
<div style="background:rgba(5,11,24,0.8);border:1px solid {border}40;
     border-top:2px solid {border};border-radius:12px;padding:1.1rem;min-height:140px">
  <div style="font-size:0.72rem;font-weight:700;color:{border};text-transform:uppercase;
       letter-spacing:0.08em;margin-bottom:0.5rem">{name[2:]}</div>
  <div style="color:#e2e8f0;font-size:0.87rem;line-height:1.65">{result.answer}</div>
</div>
""", unsafe_allow_html=True)

    st.markdown('<div class="fancy-div"></div>', unsafe_allow_html=True)

    # ── CHUNKS COMPARISON ─────────────────────────────────────
    st.markdown("""<div style="font-size:0.75rem;font-weight:700;color:#6366f1;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.8rem">📄 Retrieved Chunks Per RAG Type</div>""", unsafe_allow_html=True)
    chunk_cols = st.columns(3, gap="medium")

    for col, (name, result), border in zip(chunk_cols, results.items(), rag_borders):
        with col:
            st.markdown(f'<div style="font-size:0.82rem;font-weight:700;color:{border};margin-bottom:0.5rem">{name}</div>', unsafe_allow_html=True)
            for i, doc in enumerate(result.retrieved_docs):
                sc = doc.score
                score_color = "#10b981" if sc > 0.6 else "#f59e0b" if sc > 0.35 else "#ef4444"
                st.markdown(f"""
<div style="background:rgba(13,21,38,0.8);border:1px solid rgba(255,255,255,0.06);
     border-left:3px solid {score_color};border-radius:8px;padding:0.6rem 0.8rem;margin:0.3rem 0">
  <div style="font-size:0.7rem;font-weight:700;color:{score_color};margin-bottom:0.25rem">
    #{i+1} Score: {sc:.2f} · {doc.retrieval_method}
  </div>
  <div style="color:#94a3b8;font-size:0.8rem;line-height:1.5">
    {doc.content[:110]}{'…' if len(doc.content)>110 else ''}
  </div>
</div>
""", unsafe_allow_html=True)

    st.markdown('<div class="fancy-div"></div>', unsafe_allow_html=True)

    # ── INSIGHTS ───────────────────────────────────────────────
    st.markdown("""
<div class="sec-head">
  <div class="sec-label">Analysis</div>
  <div class="sec-title">🧠 What Does This Tell You?</div>
</div>
""", unsafe_allow_html=True)

    all_ret_times = {n: r.retrieval_ms for n, r in results.items()}
    fastest = min(all_ret_times, key=all_ret_times.get)
    all_scores = {n: r.top_doc.score if r.top_doc else 0 for n, r in results.items()}
    highest_score = max(all_scores, key=all_scores.get)

    naive_chunks = {d.chunk_index for d in results.get("🔵 Naive RAG", type('', (), {'retrieved_docs': []})()).retrieved_docs} if "🔵 Naive RAG" in results else set()
    hybrid_chunks = {d.chunk_index for d in results.get("🟣 Hybrid RAG", type('', (), {'retrieved_docs': []})()).retrieved_docs} if "🟣 Hybrid RAG" in results else set()
    overlap = len(naive_chunks & hybrid_chunks)

    ic1, ic2, ic3 = st.columns(3, gap="medium")
    with ic1:
        st.info(f"⚡ **Fastest Retrieval**\n\n{fastest[2:]} at {all_ret_times[fastest]:.0f}ms\n\nFor latency-critical systems, this is your choice.")
    with ic2:
        st.success(f"🎯 **Highest Match Score**\n\n{highest_score[2:]} with {all_scores[highest_score]:.2f}\n\nBest at finding relevant content for this query.")
    with ic3:
        st.warning(f"🔀 **Naive vs Hybrid Overlap**\n\n{overlap}/{top_k} same chunks retrieved\n\n{'Good agreement' if overlap == top_k else 'Hybrid found different chunks — may be more accurate'}.")

elif run_compare and not question.strip():
    st.error("Please type a question first!")

else:
    # Empty state hint
    st.markdown("""
<div style="background:rgba(99,102,241,0.05);border:1px solid rgba(99,102,241,0.15);
     border-radius:14px;padding:2rem;text-align:center;margin:1rem 0">
  <div style="font-size:2rem;margin-bottom:0.8rem">⚖️</div>
  <div style="font-size:1rem;font-weight:700;color:#c7d2fe;margin-bottom:0.4rem">
    Select a topic, type a question, and click Compare
  </div>
  <div style="font-size:0.88rem;color:#64748b">
    All 3 RAG types will run on the same input so you can see exactly how they differ.
  </div>
</div>
""", unsafe_allow_html=True)

    st.markdown("""
<div class="sec-head">
  <div class="sec-label">Guide</div>
  <div class="sec-title">🤔 What to Look For When Comparing</div>
</div>
""", unsafe_allow_html=True)

    table_rows = [
        ("Hybrid has higher score than Naive", "Your query had keywords (names, codes) that helped BM25"),
        ("Same answer from all 3", "The answer was clearly in the document — all methods found it"),
        ("Different answers", "They retrieved different chunks — one may be more relevant"),
        ("Naive is fastest", "Vector-only search has less overhead than hybrid"),
        ("Conversational is slower", "It also searches conversation history on top of documents"),
        ("Score below 0.35", "The answer probably isn't in your documents at all"),
    ]

    st.markdown("""
<div style="border:1px solid rgba(99,102,241,0.15);border-radius:12px;overflow:hidden">
  <table style="width:100%;border-collapse:collapse;font-size:0.87rem">
    <thead>
      <tr style="background:rgba(99,102,241,0.1)">
        <th style="padding:0.75rem 1rem;text-align:left;color:#818cf8;font-weight:700;width:50%">Observation</th>
        <th style="padding:0.75rem 1rem;text-align:left;color:#818cf8;font-weight:700">What It Means</th>
      </tr>
    </thead>
    <tbody>
""" + "".join([f"""
      <tr style="border-top:1px solid rgba(255,255,255,0.04)">
        <td style="padding:0.65rem 1rem;color:#c7d2fe;font-weight:600">{obs}</td>
        <td style="padding:0.65rem 1rem;color:#94a3b8">{meaning}</td>
      </tr>
""" for obs, meaning in table_rows]) + """
    </tbody>
  </table>
</div>
""", unsafe_allow_html=True)
