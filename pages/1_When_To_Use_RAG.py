"""
pages/1_When_To_Use_RAG.py
Interactive guide: WHEN does RAG help vs when it doesn't?
"""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from ui_styles import apply_global_styles, sidebar_nav

st.set_page_config(page_title="When to Use RAG?", page_icon="1️⃣", layout="wide")
apply_global_styles()

# ── PAGE HEADER ───────────────────────────────────────────────
st.markdown("""
<div style="padding:1.5rem 0 0.5rem">
  <div class="sec-label">Page 1 of 6</div>
  <h1 style="font-size:2rem;font-weight:800;color:#F0F4FF;margin:0.3rem 0;letter-spacing:-0.02em">
    When Should I Use RAG?
  </h1>
  <p style="color:#8892A4;font-size:0.95rem;margin:0">
    Before writing any code — understand if RAG is even the right tool for your problem.
  </p>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="fancy-div"></div>', unsafe_allow_html=True)

# ── DECISION QUIZ ─────────────────────────────────────────────
st.markdown("""
<div class="sec-head">
  <div class="sec-label">Interactive Assessment</div>
  <div class="sec-title">🧩 Does Your Project Need RAG?</div>
</div>
<p style="color:#8892A4;font-size:0.9rem;margin-bottom:1rem">Answer 5 questions to find out if RAG is right for your use case.</p>
""", unsafe_allow_html=True)

col_quiz, col_score = st.columns([3, 2], gap="large")

with col_quiz:
    q1 = st.radio(
        "**Q1. Does your AI need to answer questions about YOUR specific documents or data?**",
        ["Yes — it needs to know about MY files, database, or documents",
         "No — general knowledge is fine"],
        index=None, key="q1"
    )
    q2 = st.radio(
        "**Q2. Does the information your AI needs change over time?**",
        ["Yes — information gets updated (news, prices, policies, etc.)",
         "No — the facts are mostly stable and permanent"],
        index=None, key="q2"
    )
    q3 = st.radio(
        "**Q3. How serious are hallucinations (the AI making up false facts)?**",
        ["Very serious — wrong answers could cause harm or legal issues",
         "Not critical — a few wrong answers are acceptable"],
        index=None, key="q3"
    )
    q4 = st.radio(
        "**Q4. What kind of questions will users ask?**",
        ["Specific questions with factual answers from a document",
         "Creative/general questions (write a poem, explain a concept)"],
        index=None, key="q4"
    )
    q5 = st.radio(
        "**Q5. How large is your knowledge base?**",
        ["I have documents, PDFs, or databases — not just internet knowledge",
         "I want to use only what the AI already knows from training"],
        index=None, key="q5"
    )

with col_score:
    yes_signals = [
        q1 is not None and "Yes" in q1,
        q2 is not None and "Yes" in q2,
        q3 is not None and "Very" in q3,
        q4 is not None and "Specific" in q4,
        q5 is not None and "documents" in q5,
    ]
    answered = sum(1 for q in [q1, q2, q3, q4, q5] if q is not None)
    yes_count = sum(yes_signals)

    st.markdown("""
<div style="background:rgba(13,21,38,0.9);border:1px solid rgba(99,102,241,0.15);
     border-radius:16px;padding:1.5rem;text-align:center;">
  <div style="font-size:0.7rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;
       color:#6366f1;margin-bottom:0.8rem">Your Score</div>
""", unsafe_allow_html=True)

    if answered == 0:
        st.info("👆 Answer the questions on the left to see your result")
    elif answered < 5:
        progress_val = answered / 5
        st.progress(progress_val, text=f"Progress: {answered}/5 questions answered")
        st.warning(f"Answer all 5 questions to get your recommendation")
    else:
        # Show score visualization
        score_pct = yes_count / 5
        score_color = "#10b981" if yes_count >= 4 else "#f59e0b" if yes_count >= 2 else "#ef4444"
        score_label = "YES — Use RAG!" if yes_count >= 4 else "MAYBE — Consider RAG" if yes_count >= 2 else "SKIP RAG for now"
        score_icon = "✅" if yes_count >= 4 else "🤔" if yes_count >= 2 else "❌"

        st.markdown(f"""
<div style="text-align:center;padding:1rem 0">
  <div style="font-size:3rem;margin-bottom:0.5rem">{score_icon}</div>
  <div style="font-size:1.3rem;font-weight:800;color:{score_color}">{score_label}</div>
  <div style="font-size:2rem;font-weight:700;color:{score_color};margin:0.5rem 0">{yes_count}/5</div>
  <div style="background:rgba(255,255,255,0.05);border-radius:99px;height:8px;overflow:hidden;margin:0.8rem 0">
    <div style="height:100%;width:{int(score_pct*100)}%;background:{score_color};border-radius:99px;
         transition:width 0.5s ease"></div>
  </div>
</div>
""", unsafe_allow_html=True)

        if yes_count >= 4:
            st.success("**Your project is a great fit for RAG!**\n\nRAG will help you answer from specific data, reduce hallucinations, and keep answers current.")
        elif yes_count >= 2:
            st.warning("**RAG could help but isn't essential.**\n\nBuild a simple prototype first. If it improves quality, keep it.")
        else:
            st.error("**Your use case doesn't need RAG.**\n\nA direct LLM call will be simpler, faster, and cheaper.")

    st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="fancy-div"></div>', unsafe_allow_html=True)

# ── REAL-WORLD SCENARIOS ──────────────────────────────────────
st.markdown("""
<div class="sec-head">
  <div class="sec-label">Real-World Examples</div>
  <div class="sec-title">🌍 Use RAG or Not? — 9 Scenarios</div>
</div>
<p style="color:#8892A4;font-size:0.9rem;margin-bottom:1rem">Click any scenario to see the detailed reasoning.</p>
""", unsafe_allow_html=True)

scenarios = [
    {
        "title": "📈 Stock Trading Assistant", "use_rag": True,
        "rag_type": "Hybrid + Streaming RAG",
        "problem": "Trader asks: 'What's TSLA's trend this week based on news?'",
        "why_rag": "Needs REAL-TIME news + historical earnings context. Pure LLM doesn't have today's data.",
        "why_not_llm": "LLM was trained months ago. Can't answer questions about last week's news.",
    },
    {
        "title": "🏥 Hospital Patient QA", "use_rag": True,
        "rag_type": "Rerank RAG (high accuracy)",
        "problem": "Doctor asks: 'What medications is patient John Doe currently on?'",
        "why_rag": "Patient data is private, not in LLM training. RAG searches the hospital database.",
        "why_not_llm": "LLM has never seen this patient's records. Making it up is dangerous.",
    },
    {
        "title": "⚖️ Legal Contract Search", "use_rag": True,
        "rag_type": "Hybrid RAG (keywords matter in law)",
        "problem": "Lawyer asks: 'What does clause 5.2 say about liability?'",
        "why_rag": "Specific clause numbers need exact keyword matching + context.",
        "why_not_llm": "LLM doesn't have your specific 200-page contract.",
    },
    {
        "title": "📚 Company Knowledge Base", "use_rag": True,
        "rag_type": "Conversational RAG (multi-turn)",
        "problem": "Employee asks: 'What's our parental leave policy?' → 'How do I apply?'",
        "why_rag": "Company policies change. HR docs need to be retrievable + updated.",
        "why_not_llm": "LLM doesn't know YOUR company's specific policies.",
    },
    {
        "title": "✍️ Writing a Poem", "use_rag": False,
        "rag_type": "No RAG needed",
        "problem": "User asks: 'Write me a poem about the ocean'",
        "why_rag": "RAG wouldn't help here — no documents needed for creative writing.",
        "why_not_llm": "LLM is GREAT at this. Direct LLM call is simpler and faster.",
    },
    {
        "title": "🧮 Math Problem Solver", "use_rag": False,
        "rag_type": "No RAG needed",
        "problem": "User asks: 'Solve 2x + 5 = 13'",
        "why_rag": "Pure reasoning task. No documents needed.",
        "why_not_llm": "LLM can solve math directly — or use a calculator tool.",
    },
    {
        "title": "🌐 General Knowledge Quiz", "use_rag": False,
        "rag_type": "No RAG needed (usually)",
        "problem": "User asks: 'What is the capital of France?'",
        "why_rag": "LLM already knows this. Adding RAG just adds latency.",
        "why_not_llm": "This is why LLMs exist — stable, well-known facts.",
    },
    {
        "title": "💬 Customer Support Bot", "use_rag": True,
        "rag_type": "Conversational RAG",
        "problem": "Customer asks: 'My order #5432 is late. When will it arrive?'",
        "why_rag": "Order data is in YOUR database, not in LLM training.",
        "why_not_llm": "Order #5432 doesn't exist in any LLM. It's YOUR data.",
    },
    {
        "title": "🔬 Research Paper QA", "use_rag": True,
        "rag_type": "Multi-hop RAG",
        "problem": "Researcher asks: 'What do the latest papers say about mRNA vaccines?'",
        "why_rag": "Papers published after LLM training cutoff need RAG. Complex multi-doc reasoning.",
        "why_not_llm": "LLM may have outdated or hallucinated research findings.",
    },
]

for i in range(0, len(scenarios), 3):
    sc_cols = st.columns(3, gap="medium")
    for col, sc in zip(sc_cols, scenarios[i:i+3]):
        with col:
            badge = "✅ USE RAG" if sc["use_rag"] else "❌ SKIP RAG"
            badge_cls = "bdg-green" if sc["use_rag"] else "bdg-red"
            with st.expander(f"{sc['title']}"):
                st.markdown(f'<span class="bdg {badge_cls}">{badge}</span>', unsafe_allow_html=True)
                st.markdown(f"**Problem:** {sc['problem']}")
                st.markdown(f"**Recommended:** `{sc['rag_type']}`")
                if sc["use_rag"]:
                    st.success(f"**Why RAG?** {sc['why_rag']}")
                    st.error(f"**Why not just LLM?** {sc['why_not_llm']}")
                else:
                    st.success(f"**Why skip RAG?** {sc['why_rag']}")
                    st.info(f"**Just use LLM because:** {sc['why_not_llm']}")

st.markdown('<div class="fancy-div"></div>', unsafe_allow_html=True)

# ── GOLDEN RULES ──────────────────────────────────────────────
st.markdown("""
<div class="sec-head">
  <div class="sec-label">Key Takeaway</div>
  <div class="sec-title">🏆 The Golden Rule of RAG</div>
</div>
""", unsafe_allow_html=True)

gr1, gr2, gr3 = st.columns(3, gap="medium")
with gr1:
    st.markdown("""
<div class="g-card">
  <div style="font-size:1.5rem;margin-bottom:0.7rem">📌</div>
  <div style="font-size:0.85rem;font-weight:700;color:#818cf8;margin-bottom:0.5rem;text-transform:uppercase;letter-spacing:0.06em">Use RAG when...</div>
  <ul style="color:#94a3b8;font-size:0.85rem;line-height:1.8;padding-left:1.2rem;margin:0">
    <li>Question needs info from YOUR specific documents</li>
    <li>Not public knowledge</li>
    <li>Updated frequently</li>
    <li>Verifiable / factual answers required</li>
  </ul>
</div>
""", unsafe_allow_html=True)

with gr2:
    st.markdown("""
<div class="g-card">
  <div style="font-size:1.5rem;margin-bottom:0.7rem">🚀</div>
  <div style="font-size:0.85rem;font-weight:700;color:#34d399;margin-bottom:0.5rem;text-transform:uppercase;letter-spacing:0.06em">RAG shines for...</div>
  <ul style="color:#94a3b8;font-size:0.85rem;line-height:1.8;padding-left:1.2rem;margin:0">
    <li>Enterprise chatbots</li>
    <li>Legal / medical Q&amp;A</li>
    <li>Customer support bots</li>
    <li>Research assistants</li>
    <li>Personal document Q&amp;A</li>
  </ul>
</div>
""", unsafe_allow_html=True)

with gr3:
    st.markdown("""
<div class="g-card">
  <div style="font-size:1.5rem;margin-bottom:0.7rem">⚡</div>
  <div style="font-size:0.85rem;font-weight:700;color:#fbbf24;margin-bottom:0.5rem;text-transform:uppercase;letter-spacing:0.06em">Skip RAG for...</div>
  <ul style="color:#94a3b8;font-size:0.85rem;line-height:1.8;padding-left:1.2rem;margin:0">
    <li>Creative writing & storytelling</li>
    <li>Math and logic problems</li>
    <li>Code generation</li>
    <li>General conversation</li>
    <li>Simple factual Q&amp;A</li>
  </ul>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="info-box" style="margin-top:1.5rem">
  💡 <strong>Key insight:</strong> RAG = "Open book exam". If the answer is already in the LLM's memory
  and doesn't change, don't waste compute retrieving documents. If the answer is in YOUR private data
  or changes over time, use RAG.
</div>
""", unsafe_allow_html=True)

# ── SIDEBAR ───────────────────────────────────────────────────
sidebar_nav("1")
with st.sidebar:
    st.divider()
    st.markdown("""
<div style="background:rgba(99,102,241,0.07);border:1px solid rgba(99,102,241,0.15);
     border-radius:10px;padding:0.8rem 1rem">
  <div style="font-size:0.72rem;font-weight:700;color:#6366f1;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.4rem">
    Up Next
  </div>
  <div style="font-size:0.85rem;color:#c7d2fe;font-weight:600">2️⃣ How RAG Works</div>
  <div style="font-size:0.78rem;color:#8892A4;margin-top:0.2rem">See the pipeline step by step</div>
</div>
""", unsafe_allow_html=True)
