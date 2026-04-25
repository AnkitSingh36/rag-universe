"""
pages/1_When_To_Use_RAG.py

Interactive guide: WHEN does RAG help vs when it doesn't?
Includes a decision quiz, real-world scenario cards, and side-by-side comparison.
"""

import streamlit as st

st.set_page_config(page_title="When to Use RAG?", page_icon="1️⃣", layout="wide")

st.title("1️⃣ When Should I Use RAG?")
st.markdown("*Before writing any code — understand if RAG is even the right tool for your problem.*")
st.divider()

# ── DECISION QUIZ ──────────────────────────────────────────
st.subheader("🧩 Quick Quiz: Does Your Project Need RAG?")
st.markdown("Answer these 5 questions to find out:")

col1, col2 = st.columns([2, 1])

with col1:
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

with col2:
    # Score calculation
    yes_signals = [
        q1 is not None and "Yes" in q1,
        q2 is not None and "Yes" in q2,
        q3 is not None and "Very" in q3,
        q4 is not None and "Specific" in q4,
        q5 is not None and "documents" in q5,
    ]

    answered = sum(1 for q in [q1, q2, q3, q4, q5] if q is not None)
    yes_count = sum(yes_signals)

    st.markdown("### 📊 Your Score")

    if answered == 0:
        st.info("👆 Answer the questions to see your result")
    elif answered < 5:
        st.warning(f"Answer all 5 questions ({answered}/5 done)")
    else:
        if yes_count >= 4:
            st.success("## ✅ YES — Use RAG!")
            st.markdown(f"**Score: {yes_count}/5**")
            st.markdown("""
Your project is a great candidate for RAG.

RAG will help you:
- Answer from your specific data
- Reduce hallucinations
- Keep answers current
            """)
        elif yes_count >= 2:
            st.warning("## 🤔 MAYBE — Consider RAG")
            st.markdown(f"**Score: {yes_count}/5**")
            st.markdown("""
RAG could help but isn't essential.

Try a simple RAG prototype first.
If it improves quality, keep it.
If not, stick with a direct LLM.
            """)
        else:
            st.error("## ❌ SKIP RAG for now")
            st.markdown(f"**Score: {yes_count}/5**")
            st.markdown("""
Your use case doesn't need RAG.

A direct LLM call will work better:
- Simpler to build
- Faster
- Lower cost
            """)

st.divider()

# ── REAL-WORLD SCENARIOS ───────────────────────────────────
st.subheader("🌍 Real-World Scenarios — Use RAG or Not?")
st.markdown("Click any scenario to see the reasoning:")

scenarios = [
    {
        "title": "📈 Stock Trading Assistant",
        "use_rag": True,
        "rag_type": "Hybrid + Streaming RAG",
        "problem": "Trader asks: 'What's TSLA's trend this week based on news?'",
        "why_rag": "Needs REAL-TIME news + historical earnings context. Pure LLM doesn't have today's data.",
        "why_not_llm": "LLM was trained months ago. Can't answer questions about last week's news.",
    },
    {
        "title": "🏥 Hospital Patient QA",
        "use_rag": True,
        "rag_type": "Rerank RAG (high accuracy)",
        "problem": "Doctor asks: 'What medications is patient John Doe currently on?'",
        "why_rag": "Patient data is private, not in LLM training. RAG searches the hospital database.",
        "why_not_llm": "LLM has never seen this patient's records. Making it up is dangerous.",
    },
    {
        "title": "⚖️ Legal Contract Search",
        "use_rag": True,
        "rag_type": "Hybrid RAG (keywords matter in law)",
        "problem": "Lawyer asks: 'What does clause 5.2 say about liability?'",
        "why_rag": "Specific clause numbers need exact keyword matching + context.",
        "why_not_llm": "LLM doesn't have your specific 200-page contract.",
    },
    {
        "title": "📚 Company Knowledge Base",
        "use_rag": True,
        "rag_type": "Conversational RAG (multi-turn)",
        "problem": "Employee asks: 'What's our parental leave policy?' → 'How do I apply?'",
        "why_rag": "Company policies change. HR docs need to be retrievable + updated.",
        "why_not_llm": "LLM doesn't know YOUR company's specific policies.",
    },
    {
        "title": "✍️ Writing a Poem",
        "use_rag": False,
        "rag_type": "No RAG needed",
        "problem": "User asks: 'Write me a poem about the ocean'",
        "why_rag": "RAG wouldn't help here — no documents needed for creative writing.",
        "why_not_llm": "LLM is GREAT at this. Direct LLM call is simpler and faster.",
    },
    {
        "title": "🧮 Math Problem Solver",
        "use_rag": False,
        "rag_type": "No RAG needed",
        "problem": "User asks: 'Solve 2x + 5 = 13'",
        "why_rag": "Pure reasoning task. No documents needed.",
        "why_not_llm": "LLM can solve math directly — or use a calculator tool.",
    },
    {
        "title": "🌐 General Knowledge Quiz",
        "use_rag": False,
        "rag_type": "No RAG needed (usually)",
        "problem": "User asks: 'What is the capital of France?'",
        "why_rag": "LLM already knows this. Adding RAG just adds latency.",
        "why_not_llm": "This is why LLMs exist — stable, well-known facts.",
    },
    {
        "title": "💬 Customer Support Bot",
        "use_rag": True,
        "rag_type": "Conversational RAG",
        "problem": "Customer asks: 'My order #5432 is late. When will it arrive?'",
        "why_rag": "Order data is in YOUR database, not in LLM training.",
        "why_not_llm": "Order #5432 doesn't exist in any LLM. It's YOUR data.",
    },
    {
        "title": "🔬 Research Paper QA",
        "use_rag": True,
        "rag_type": "Multi-hop RAG",
        "problem": "Researcher asks: 'What do the latest papers say about mRNA vaccines?'",
        "why_rag": "Papers published after LLM training cutoff need RAG. Complex multi-doc reasoning.",
        "why_not_llm": "LLM may have outdated or hallucinated research findings.",
    },
]

for i in range(0, len(scenarios), 3):
    cols = st.columns(3)
    for col, sc in zip(cols, scenarios[i:i+3]):
        with col:
            badge = "✅ USE RAG" if sc["use_rag"] else "❌ SKIP RAG"
            color = "#064e3b" if sc["use_rag"] else "#450a0a"
            border = "#10b981" if sc["use_rag"] else "#ef4444"

            with st.expander(f"{sc['title']} → {badge}"):
                st.markdown(f"**Problem:** {sc['problem']}")
                st.markdown(f"**Recommended:** `{sc['rag_type']}`")
                if sc["use_rag"]:
                    st.success(f"**Why RAG?** {sc['why_rag']}")
                    st.error(f"**Why not just LLM?** {sc['why_not_llm']}")
                else:
                    st.success(f"**Why skip RAG?** {sc['why_rag']}")
                    st.info(f"**Just use LLM because:** {sc['why_not_llm']}")

st.divider()

# ── THE GOLDEN RULE ───────────────────────────────────────
st.subheader("🏆 The Golden Rule")

c1, c2, c3 = st.columns(3)
with c1:
    st.info("**Use RAG when...**\n\nYour question needs information that is:\n- In YOUR specific documents\n- Not public knowledge\n- Updated frequently\n- Verifiable / factual")
with c2:
    st.success("**RAG shines for...**\n\n- Enterprise chatbots\n- Legal / medical Q&A\n- Customer support\n- Research assistants\n- Personal document Q&A")
with c3:
    st.warning("**Skip RAG for...**\n\n- Creative writing\n- Math and logic\n- Code generation\n- General conversation\n- Simple factual Q&A (capital cities, etc.)")

st.markdown("""
> **Key insight:** RAG = "Open book exam". If the answer is already in the LLM's memory and doesn't change,
> don't waste compute retrieving documents. If the answer is in YOUR private data or changes over time, use RAG.
""")

# Sidebar navigation
with st.sidebar:
    st.markdown("## 🗺️ Navigation")
    st.page_link("app.py", label="🏠 Home")
    st.page_link("pages/1_When_To_Use_RAG.py", label="1️⃣ When to Use RAG")
    st.page_link("pages/2_How_RAG_Works.py", label="2️⃣ How RAG Works")
    st.page_link("pages/3_Test_Any_RAG.py", label="3️⃣ Test Any RAG ⭐")
    st.page_link("pages/4_Compare_RAGs.py", label="4️⃣ Compare RAG Types")
    st.divider()
    st.markdown("**Next:** [How RAG Works →](pages/2_How_RAG_Works.py)")
