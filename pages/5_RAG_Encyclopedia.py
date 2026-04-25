"""
pages/5_RAG_Encyclopedia.py
Complete reference for all RAG architectures.
Theory + Visual Pipeline + Code + Interview Q&A for every major type.
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd
from rag_diagrams.pipeline import get_rag_diagram
from ui_styles import apply_global_styles, sidebar_nav

st.set_page_config(page_title="RAG Encyclopedia", page_icon="📖", layout="wide")
apply_global_styles()

# ── PAGE HEADER ───────────────────────────────────────────────
st.markdown("""
<div style="padding:1.5rem 0 0.5rem">
  <div class="sec-label">Page 5 of 6</div>
  <h1 style="font-size:2rem;font-weight:800;color:#F0F4FF;margin:0.3rem 0;letter-spacing:-0.02em">
    📖 RAG Encyclopedia
  </h1>
  <p style="color:#8892A4;font-size:0.95rem;margin:0">
    Theory · Pipeline · Code · Interview Q&amp;A for all 11 RAG architectures.
  </p>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="fancy-div"></div>', unsafe_allow_html=True)

# ── ENCYCLOPEDIA DATA ─────────────────────────────────────────
ENCYCLOPEDIA = [
    {
        "name": "Naive RAG", "emoji": "🔵", "tagline": "The Foundation",
        "complexity": "⭐ Simple", "speed": "⚡⚡⚡ Fast", "color": "#3B82F6",
        "introduced": "2020 — Lewis et al.",
        "theory": """**The original, simplest RAG architecture.** Every other RAG type builds on this foundation.

**Core idea:** Convert everything to meaning-vectors (embeddings), then find the closest match.

**Pipeline:**
1. **Chunk** your documents into ~300-char pieces
2. **Embed** each chunk → 384 numbers per chunk
3. **Store** all embeddings in FAISS vector database
4. At query time: **embed query** → **find similar vectors** → **retrieve top-k chunks**
5. Pass chunks to LLM → **generate answer**

**Why it fails:** Purely semantic — misses exact keyword matches like "NASA" matching "National Aeronautics".""",
        "use_when": "Simple Q&A, prototypes, learning, corpora where semantic search is enough",
        "avoid_when": "Need exact keyword matches (names, codes, product IDs), very large corpora",
        "code": '''from rag_core import NaiveRAG

rag = NaiveRAG(chunk_size=300, overlap=50)
rag.add_documents(["Your document text here..."])
result = rag.ask("Your question?")
print(result.answer)
print(f"Top match score: {result.retrieved_docs[0].score:.2f}")''',
        "interview_q": "Explain Naive RAG and its limitations.",
        "interview_a": "Naive RAG embeds documents and queries into vector space, retrieves the top-k nearest chunks by cosine similarity, then feeds them to an LLM. Limitations: pure semantic search misses exact keyword matches; chunk boundaries can split context; no query refinement if results are poor.",
    },
    {
        "name": "Hybrid RAG", "emoji": "🟣", "tagline": "Keyword + Semantic",
        "complexity": "⭐⭐ Medium", "speed": "⚡⚡ Medium", "color": "#8B5CF6",
        "introduced": "2021 — Combines BM25 + DPR",
        "theory": """**Combines two complementary search methods:**

- **BM25 (keyword search):** Finds documents containing the EXACT words. Great for names, codes, acronyms.
- **Vector search (semantic search):** Finds documents with the SAME MEANING even if words differ.

**Fusion with RRF (Reciprocal Rank Fusion):**
```
score(doc) = 1/(60 + rank_bm25) + 1/(60 + rank_vector)
```
Documents appearing high in BOTH lists get extra credit. The constant 60 is empirically proven to work well.""",
        "use_when": "Stock tickers, product codes, names, legal keywords, any query needing exact + semantic",
        "avoid_when": "Pure concept-level tasks where keywords are irrelevant; memory-constrained",
        "code": '''from rag_core import HybridRAG

rag = HybridRAG()
rag.add_documents(["Tesla TSLA stock earnings..."])

# Both "TSLA" (keyword) and "stock performance" (semantic) work!
result = rag.ask("What are TSLA earnings?")
for doc in result.retrieved_docs:
    print(f"{doc.retrieval_method}: {doc.score:.3f}")''',
        "interview_q": "Why use Hybrid RAG instead of pure vector search?",
        "interview_a": "Hybrid RAG combines BM25 (keyword-based) with vector search (semantic). BM25 excels at exact matches — names, stock tickers, product codes — while vector search captures synonyms and paraphrases. RRF fusion rewards documents appearing high in both ranked lists.",
    },
    {
        "name": "Conversational RAG", "emoji": "🟢", "tagline": "Multi-Turn Memory",
        "complexity": "⭐⭐ Medium", "speed": "⚡⚡ Medium", "color": "#10B981",
        "introduced": "2022 — LangChain ConversationalRetrievalChain",
        "theory": """**Extends Naive RAG with conversation memory.**

**Problem with stateless RAG:**
```
Q: "Tell me about Einstein"
Q: "When was he born?"  ← who is "he"?  ← Naive RAG doesn't know!
```

**Solution:** Store every Q&A turn as embeddings. On new query, ALSO search past turns.

**On each new query:**
1. Embed query
2. Search BOTH document index AND history index
3. Retrieve top-k docs + top-2 history turns
4. Combine → LLM → answer
5. Store new turn → update history index""",
        "use_when": "Customer support chatbots, research assistants, multi-turn Q&A",
        "avoid_when": "Stateless APIs, batch processing, single-turn questions",
        "code": '''from rag_core import ConversationalRAG

rag = ConversationalRAG()
rag.add_documents(["Tell me about Tesla..."])

r1 = rag.ask("Who is Elon Musk?")
r2 = rag.ask("What companies does he run?")  # uses turn 1 context!
r3 = rag.ask("How many employees do they have?")  # uses turns 1+2!

print(f"History: {len(rag.history)} turns stored")''',
        "interview_q": "How does Conversational RAG handle follow-up questions like 'What about him?'",
        "interview_a": "Conversational RAG embeds each past Q&A turn and stores them in a separate FAISS index. On each new query, it retrieves from both documents AND conversation history. Follow-up pronouns are resolved through context from previous turns.",
    },
    {
        "name": "Rerank RAG", "emoji": "🔶", "tagline": "Two-Stage Precision",
        "complexity": "⭐⭐ Medium", "speed": "⚡ Slower", "color": "#F59E0B",
        "introduced": "2019 — MS MARCO paper, cross-encoders",
        "theory": """**Two-stage retrieval: fast → precise**

- **Stage 1 (Bi-encoder, fast):** Retrieve top 20-50 candidates via vector search
- **Stage 2 (Cross-encoder, precise):** Re-score all candidates considering query-document interaction
- Return the top 3 from Stage 2

**Why cross-encoder is more accurate:**
Bi-encoders embed query and docs SEPARATELY. Cross-encoders look at query AND document TOGETHER — allowing nuanced relevance scoring.

**Improvement over Naive RAG:** ~15-25% higher NDCG@10 on typical benchmarks.""",
        "use_when": "Legal contracts, medical Q&A, finance (accuracy critical), enterprise search",
        "avoid_when": "Latency-sensitive (<100ms needed), simple chatbots, resource-constrained environments",
        "code": '''from rag_core import RerankRAG

rag = RerankRAG(
    first_stage_k=20,   # retrieve 20 candidates first
    second_stage_k=3    # keep top 3 after reranking
)
rag.add_documents(["Contract text..."])
result = rag.ask("What are the payment terms?")

for doc in result.retrieved_docs:
    print(f"Score: {doc.score:.3f} | {doc.retrieval_method}")''',
        "interview_q": "Why is a cross-encoder more accurate than a bi-encoder for reranking?",
        "interview_a": "Bi-encoders embed query and document independently, losing query-document interaction. Cross-encoders process query and document together as a single input, allowing attention to flow between them. Trade-off: cross-encoders can't pre-encode documents (they need the query), so they're only practical for a small pre-filtered candidate set.",
    },
    {
        "name": "Contextual RAG", "emoji": "🟡", "tagline": "Token-Efficient",
        "complexity": "⭐⭐ Medium", "speed": "⚡⚡ Medium", "color": "#EAB308",
        "introduced": "2023 — LangChain ContextualCompressionRetriever",
        "theory": """**The insight: Retrieved chunks contain a lot of noise.**

Contextual RAG **compresses** retrieved chunks:
1. Split chunk into sentences
2. Embed each sentence AND the query
3. Compute cosine similarity for each sentence
4. Keep only sentences above a threshold (e.g., cosine > 0.3)
5. Send only the relevant sentences to LLM

**Benefits:**
- **Token savings:** 60-80% fewer tokens sent to LLM
- **Better answers:** LLM isn't confused by irrelevant context
- **Cost reduction:** Fewer tokens = lower API costs""",
        "use_when": "Long documents (books, reports), cost-sensitive apps, when token budget is limited",
        "avoid_when": "Short docs, real-time systems (compression adds latency), highly dense technical text",
        "code": '''from rag_core import ContextualRAG

rag = ContextualRAG(
    compression_threshold=0.15  # keep sentences above this similarity
)
rag.add_documents(["Long article with lots of text..."])
result = rag.ask("When was Einstein born?")

for doc in result.retrieved_docs:
    print(f"{doc.retrieval_method}")  # shows "compressed (XX% kept)"''',
        "interview_q": "How does Contextual Compression RAG reduce hallucinations?",
        "interview_a": "By compressing retrieved chunks to only relevant sentences, we reduce the noise the LLM sees. LLMs are more likely to hallucinate when given large amounts of irrelevant context. A focused context leads to more grounded answers.",
    },
    {
        "name": "Self-Reflective RAG", "emoji": "🔮", "tagline": "Knows What It Doesn't Know",
        "complexity": "⭐⭐⭐ Hard", "speed": "⚡ Slower", "color": "#6366F1",
        "introduced": "2023 — SELF-RAG (Asai et al., NeurIPS 2023)",
        "theory": """**Paper:** SELF-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection

**Four reflection tokens:**
- `[Retrieve]` — should I even retrieve for this query?
- `[IsRel]` — is this retrieved chunk relevant?
- `[IsSup]` — does my answer support the retrieved text?
- `[IsUseful]` — is my final answer useful?

**Pipeline:**
1. Decide if retrieval is needed
2. Retrieve
3. Score each doc: is it relevant?
4. If NOT relevant → expand query → retry
5. Generate answer
6. Grade: is answer grounded in docs?""",
        "use_when": "Medical Q&A, fact-checking, academic research, reliability > speed",
        "avoid_when": "Real-time systems, simple chatbots, when you need <200ms response",
        "code": '''from rag_core import SelfReflectiveRAG

rag = SelfReflectiveRAG(
    relevance_threshold=0.45,
    max_retries=2
)
rag.add_documents(["Medical research papers..."])
result = rag.ask("What is the dosage for aspirin?")

for step in result.steps:
    print(f"{step['step']}: {step['detail']}")''',
        "interview_q": "What makes SELF-RAG different from standard RAG?",
        "interview_a": "SELF-RAG adds four critique tokens that allow the model to self-evaluate: should I retrieve? Is this chunk relevant? Is my answer supported by docs? Is the answer useful? This enables the model to skip retrieval for questions it can answer directly, and retry with different queries when retrieved docs are irrelevant.",
    },
    {
        "name": "Corrective RAG", "emoji": "✅", "tagline": "Fact-Checker",
        "complexity": "⭐⭐⭐ Hard", "speed": "⚡ Slower", "color": "#10B981",
        "introduced": "2024 — CRAG (Yan et al.)",
        "theory": """**Problem:** Standard RAG assumes retrieved docs are relevant. If they're not, the LLM hallucinates.

**CRAG solution:** Evaluate retrieval quality BEFORE generating. Three outcomes:

| Score | Evaluation | Action |
|-------|-----------|--------|
| High | **CORRECT** | Use docs confidently |
| Medium | **AMBIGUOUS** | Use docs but flag uncertainty |
| Low | **INCORRECT** | Warn user docs may not answer |

**Key insight:** It's better to say "I'm not sure" than to confidently give a wrong answer.""",
        "use_when": "Compliance, medical diagnosis, financial advice — wrong answers are dangerous",
        "avoid_when": "Creative apps, casual chatbots, when some uncertainty is acceptable",
        "code": '''from rag_core import CorrectiveRAG

rag = CorrectiveRAG()
rag.add_documents(["Your domain documents..."])

result = rag.ask("What is the maximum safe dosage?")
print(result.answer)  # might include "⚠️ Low confidence"
print(f"Confidence: {result.confidence_score:.2f}")''',
        "interview_q": "How does CRAG reduce hallucination compared to standard RAG?",
        "interview_a": "CRAG adds an evaluation step to classify whether retrieved docs are CORRECT, AMBIGUOUS, or INCORRECT for the query. Based on this, it adjusts the answer — returning confident answers when relevant, flagging uncertainty when partially relevant, or warning when clearly irrelevant.",
    },
    {
        "name": "Adaptive RAG", "emoji": "🔀", "tagline": "Smart Router",
        "complexity": "⭐⭐⭐ Hard", "speed": "⚡⚡ Variable", "color": "#EC4899",
        "introduced": "2024 — Adaptive-RAG (Jeong et al.)",
        "theory": """**Core insight:** One RAG strategy doesn't fit all queries.

| Query Type | Example | Best Strategy |
|-----------|---------|---------------|
| Simple factual | "What year did WWII end?" | No retrieval (LLM knows this) |
| Medium | "What are Tesla's 2024 revenues?" | Single RAG retrieval |
| Complex | "Compare Tesla vs Rivian growth strategy" | Multi-step retrieval |

**Benefits:**
- Simple queries: 3x faster (no retrieval needed)
- Complex queries: 2x more accurate (better RAG)
- Overall better speed/accuracy tradeoff than any single approach""",
        "use_when": "Production systems with mixed query types, when you want optimal speed AND accuracy",
        "avoid_when": "When all queries are similar complexity (routing overhead not worth it)",
        "code": '''from rag_core import AdaptiveRAG

rag = AdaptiveRAG()
rag.add_documents(["Mixed content..."])

r1 = rag.ask("What year?")          # → routes to Naive RAG
r2 = rag.ask("What is TSLA price?") # → routes to Hybrid RAG
r3 = rag.ask("Compare Tesla vs Apple business strategy")  # → Rerank

print(r1.rag_type)  # "Adaptive RAG → Naive RAG"''',
        "interview_q": "How does Adaptive RAG decide which retrieval strategy to use?",
        "interview_a": "Adaptive-RAG trains a lightweight classifier to predict query complexity from the question text. It classifies queries as single-hop, multi-hop, or no-retrieval needed. In production, heuristics work well: query length, comparison words, named entities, and numbers are strong signals of complexity.",
    },
    {
        "name": "Multi-Hop RAG", "emoji": "🔗", "tagline": "Chain-of-Retrieval",
        "complexity": "⭐⭐⭐ Hard", "speed": "⚡ Slower", "color": "#F97316",
        "introduced": "2021 — HotpotQA, IRCOT",
        "theory": """**For questions that require multiple steps to answer:**

Example: "What nationality is the CEO of the company that makes iPhone?"
- Step 1: Find → "iPhone is made by Apple"
- Step 2: Find → "Apple's CEO is Tim Cook"
- Step 3: Find → "Tim Cook is American"
- Synthesis: "The CEO is American"

**No single retrieval can answer this** because the answer depends on intermediate findings.

**Error propagation risk:** If Hop 1 gives wrong entity, Hop 2 goes completely wrong. Solution: Use Corrective RAG at each hop.""",
        "use_when": "Research assistants, genealogy, supply chain Q&A, knowledge graph traversal",
        "avoid_when": "Simple factual questions, real-time systems, self-contained context",
        "code": '''from rag_core import MultiHopRAG

rag = MultiHopRAG(max_hops=2)
rag.add_documents(["Company info, people info, product info..."])

result = rag.ask("Who invented the telescope and what did they discover?")

for step in result.steps:
    print(f"{step['step']}: {step['detail']}")
# → Hop 1: Retrieved info about telescope inventor
# → Hop 2: Retrieved info about Galileo's discoveries''',
        "interview_q": "Explain Multi-hop RAG and when it's needed.",
        "interview_a": "Multi-hop RAG chains multiple retrieval steps where each hop's results inform the next query. It's needed for bridge questions — where the answer to Question A is used to form Question B. Key challenges are error propagation and latency from multiple retrieval rounds.",
    },
    {
        "name": "Graph RAG", "emoji": "🕸️", "tagline": "Relationship-Aware",
        "complexity": "⭐⭐⭐ Hard", "speed": "⚡ Slower", "color": "#8B5CF6",
        "introduced": "2024 — Microsoft GraphRAG (Edge et al.)",
        "theory": """**Paper:** From Local to Global: A Graph RAG Approach to Query-Focused Summarization (Microsoft, 2024)

**Why vector search misses relationships:**
- "Tesla and SpaceX are both founded by Elon Musk"
- Query: "What do Tesla and SpaceX have in common?"
- Vector search: finds separate chunks about each company
- Graph RAG: traverses edges → finds shared node (Elon Musk) → answers directly

**Microsoft's result:** GraphRAG outperforms standard RAG on global summarization by 15-30%.""",
        "use_when": "Org charts, supply chains, knowledge bases with rich relationships",
        "avoid_when": "Unstructured text with no clear entities, real-time, simpler use cases",
        "code": '''# Graph RAG (conceptual — production needs Neo4j)
graph = {
    "Einstein": {"born_in": "Germany", "published": "Theory of Relativity"},
    "Germany": {"capital": "Berlin"},
    "Theory of Relativity": {"published_year": "1905"},
}

# Query: "Where was the author of Relativity born?"
# → Find "Theory of Relativity" → traverse "published" edge
# → Find "Einstein" → traverse "born_in" edge → "Germany"''',
        "interview_q": "Why does Microsoft's GraphRAG outperform standard RAG for summarization?",
        "interview_a": "Standard RAG struggles with global queries ('What are the main themes?') because no single chunk captures the big picture. GraphRAG builds a knowledge graph and creates community summaries at multiple levels. For global queries it can retrieve high-level summaries across an entire corpus.",
    },
    {
        "name": "Agentic RAG", "emoji": "🤖", "tagline": "Self-Directing Agent",
        "complexity": "⭐⭐⭐ Hard", "speed": "⚡ Slowest", "color": "#F97316",
        "introduced": "2023 — ReAct, LangChain Agents",
        "theory": """**RAG controlled by an AI agent that plans its own actions.**

Standard RAG: fixed pipeline (always retrieve → always generate)
Agentic RAG: LLM decides WHAT to do at each step

**Agent loop:**
```
LOOP:
  1. Think: "What information do I have? What do I need?"
  2. Act: Choose action (retrieve docs, search web, call API…)
  3. Observe: Get result of action
  4. Think: "Is this enough to answer?"
UNTIL: Confident enough to answer
```

**Cost warning:** Each loop iteration = LLM call. A 5-step agent = 5x cost.""",
        "use_when": "Research automation, complex analysis, multi-source synthesis",
        "avoid_when": "Simple Q&A, latency-critical, cost-sensitive, when a fixed pipeline works fine",
        "code": '''from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool

tools = [
    Tool(name="rag_search", func=rag.retrieve, description="Search knowledge base"),
    Tool(name="calculator", func=calc, description="Do math"),
    Tool(name="web_search", func=web, description="Search internet"),
]

agent = create_react_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, max_iterations=5)
result = executor.invoke({"input": "Research Tesla and compare financials to NIO"})''',
        "interview_q": "What's the difference between Agentic RAG and standard RAG?",
        "interview_a": "Standard RAG follows a fixed pipeline: retrieve → generate. Agentic RAG uses an LLM to plan and execute its own retrieval strategy using a ReAct loop. The agent decides what to retrieve, when, which tools to use, and when it has enough information. This enables complex multi-step tasks but at higher cost and latency.",
    },
]

# ── QUICK OVERVIEW GRID ───────────────────────────────────────
st.markdown("""
<div class="sec-head">
  <div class="sec-label">All Architectures</div>
  <div class="sec-title">🗺️ 11 RAG Architectures at a Glance</div>
</div>
""", unsafe_allow_html=True)

grid_cols = st.columns(4, gap="small")
for i, rag in enumerate(ENCYCLOPEDIA):
    with grid_cols[i % 4]:
        st.markdown(f"""
<div class="enc-card" style="background:{rag['color']}10;border:1px solid {rag['color']}35">
  <div class="enc-emoji">{rag['emoji']}</div>
  <div class="enc-name">{rag['name']}</div>
  <div class="enc-meta">{rag['complexity'].split()[0]} · {rag['speed'].split()[0]}</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="fancy-div"></div>', unsafe_allow_html=True)

# ── SEARCH & FILTER ───────────────────────────────────────────
st.markdown("""
<div class="sec-head">
  <div class="sec-label">Reference Library</div>
  <div class="sec-title">🔍 Detailed Architecture Cards</div>
</div>
""", unsafe_allow_html=True)

col_search, col_filter = st.columns([3, 1])
with col_search:
    search = st.text_input("Search by name, complexity, or tagline:", placeholder="e.g. 'Hybrid' or 'Hard' or 'memory'")
with col_filter:
    st.markdown('<div style="height:28px"></div>', unsafe_allow_html=True)

filtered = [r for r in ENCYCLOPEDIA if not search
            or search.lower() in r['name'].lower()
            or search.lower() in r['complexity'].lower()
            or search.lower() in r['tagline'].lower()
            or search.lower() in r['theory'].lower()]

st.markdown(f"""
<div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:1rem">
  <span class="bdg bdg-purple">Showing {len(filtered)}/{len(ENCYCLOPEDIA)} architectures</span>
  {'<span class="bdg bdg-amber">Search active</span>' if search else ''}
</div>
""", unsafe_allow_html=True)

for rag in filtered:
    with st.expander(f"{rag['emoji']}  {rag['name']} — {rag['tagline']}   [{rag['complexity']} · {rag['speed']}]"):
        col_left, col_right = st.columns([1, 1], gap="large")

        with col_left:
            st.markdown("#### 🎨 Pipeline Visualization")
            diagram_html = get_rag_diagram(rag['name'])
            st.markdown(diagram_html, unsafe_allow_html=True)

            st.markdown("#### 📋 When to Use")
            uw1, uw2 = st.columns(2)
            with uw1:
                st.success(f"✅ **Use when:**\n{rag['use_when']}")
            with uw2:
                st.error(f"❌ **Avoid when:**\n{rag['avoid_when']}")

        with col_right:
            st.markdown(f"#### 📖 Theory   `{rag['introduced']}`")
            st.markdown(rag['theory'])

            st.markdown("#### 💻 Quick Code")
            st.code(rag['code'], language="python")

            st.markdown("#### 🎓 Interview Q&A")
            st.markdown(f"**Q: {rag['interview_q']}**")
            st.info(f"**A:** {rag['interview_a']}")

st.markdown('<div class="fancy-div"></div>', unsafe_allow_html=True)

# ── COMPARISON TABLE ──────────────────────────────────────────
st.markdown("""
<div class="sec-head">
  <div class="sec-label">Quick Reference</div>
  <div class="sec-title">⚖️ All 11 — Comparison Table</div>
</div>
""", unsafe_allow_html=True)

comparison_data = {
    "RAG Type": [r["emoji"] + " " + r["name"] for r in ENCYCLOPEDIA],
    "Complexity": [r["complexity"] for r in ENCYCLOPEDIA],
    "Speed": [r["speed"] for r in ENCYCLOPEDIA],
    "Best For": [r["use_when"][:55] + "…" for r in ENCYCLOPEDIA],
}
st.dataframe(pd.DataFrame(comparison_data), use_container_width=True, hide_index=True)

# ── SIDEBAR ───────────────────────────────────────────────────
sidebar_nav("5")
