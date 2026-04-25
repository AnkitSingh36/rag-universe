"""
pages/5_RAG_Encyclopedia.py

The complete reference for all RAG architectures.
Each entry: Theory + Visual Pipeline + When to Use + Code Snippet + Interview Q&A
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from rag_diagrams.pipeline import get_rag_diagram

st.set_page_config(page_title="RAG Encyclopedia", page_icon="📖", layout="wide")

st.title("📖 RAG Encyclopedia — All 11 Architectures")
st.markdown("*Theory + Visual Pipeline + Code + Interview Q&A for every major RAG type.*")
st.divider()

# Encyclopedia data
ENCYCLOPEDIA = [
    {
        "name": "Naive RAG",
        "emoji": "🔵",
        "tagline": "The Foundation",
        "complexity": "⭐ Simple",
        "speed": "⚡⚡⚡ Fast",
        "color": "#3B82F6",
        "introduced": "2020 — Lewis et al.",
        "theory": """
**The original, simplest RAG architecture.** Every other RAG type builds on this foundation.

**Core idea:** Convert everything to meaning-vectors (embeddings), then find the closest match.

**Pipeline:**
1. **Chunk** your documents into ~300-char pieces
2. **Embed** each chunk using a sentence-transformer → 384 numbers per chunk
3. **Store** all embeddings in FAISS vector database
4. At query time: **embed query** → **find similar vectors** (cosine/L2) → **retrieve top-k chunks**
5. Pass chunks to LLM → **generate answer**

**Why it works:** Similar text has similar embedding vectors. "Car" and "automobile" end up close in vector space.

**Why it fails:** Purely semantic — misses exact keyword matches. "NASA" won't match "National Aeronautics" unless trained on that pair.
        """,
        "use_when": "Simple Q&A, prototypes, learning, corpora where semantic search is enough",
        "avoid_when": "Need exact keyword matches (names, codes, product IDs), very large corpora (>500K docs)",
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
        "name": "Hybrid RAG",
        "emoji": "🟣",
        "tagline": "Keyword + Semantic",
        "complexity": "⭐⭐ Medium",
        "speed": "⚡⚡ Medium",
        "color": "#8B5CF6",
        "introduced": "2021 — Combines BM25 + DPR",
        "theory": """
**Combines two complementary search methods:**

- **BM25 (keyword search):** Finds documents containing the EXACT words in your query. Fast, deterministic, great for names, codes, acronyms.
- **Vector search (semantic search):** Finds documents with the SAME MEANING even if words differ.

**Fusion with RRF (Reciprocal Rank Fusion):**
```
score(doc) = 1/(60 + rank_bm25) + 1/(60 + rank_vector)
```
Docs appearing high in BOTH lists get extra credit. The constant 60 prevents division by zero and dampens high-rank outliers.

**Why 60?** It's empirically proven to work well. Papers show RRF with k=60 outperforms most weighted combinations.

**Real world example:** Trading assistant
- Query: "TSLA earnings"
- BM25 finds: "TSLA quarterly..." (exact ticker match)
- Vector finds: "Tesla reported revenue..." (semantic match)
- Hybrid returns BOTH, ranked together ✅
        """,
        "use_when": "Stock tickers, product codes, names, legal keywords, any query needing both exact + semantic",
        "avoid_when": "Pure concept-level tasks where keywords are irrelevant; memory-constrained (two indexes)",
        "code": '''from rag_core import HybridRAG

rag = HybridRAG()
rag.add_documents(["Tesla TSLA stock earnings..."])

# Both "TSLA" (keyword) and "stock performance" (semantic) work!
result = rag.ask("What are TSLA earnings?")
for doc in result.retrieved_docs:
    print(f"{doc.retrieval_method}: {doc.score:.3f}")''',
        "interview_q": "Why use Hybrid RAG instead of pure vector search?",
        "interview_a": "Hybrid RAG combines BM25 (keyword-based) with vector search (semantic). BM25 excels at exact matches — names, stock tickers, product codes — while vector search captures synonyms and paraphrases. Real queries often need both: a user asking about 'TSLA Q4 revenue' needs exact ticker matching (BM25) and contextual understanding (vector). RRF fusion rewards documents appearing high in both ranked lists.",
    },
    {
        "name": "Conversational RAG",
        "emoji": "🟢",
        "tagline": "Multi-Turn Memory",
        "complexity": "⭐⭐ Medium",
        "speed": "⚡⚡ Medium",
        "color": "#10B981",
        "introduced": "2022 — LangChain ConversationalRetrievalChain",
        "theory": """
**Extends Naive RAG with conversation memory.**

**Problem with stateless RAG:**
```
Q: "Tell me about Einstein"
Q: "When was he born?"  ← who is "he"?  ← Naive RAG doesn't know!
```

**Solution:** Store every Q&A turn as embeddings. On new query, ALSO search past turns.

**Memory architecture:**
- Document index (FAISS): your knowledge base
- History index (FAISS): past conversation turns

**On each new query:**
1. Embed query
2. Search BOTH document index AND history index
3. Retrieve top-k docs + top-2 history turns
4. Combine → LLM → answer
5. Store new turn → update history index

**Challenge: Context window grows.** Solution: After N turns, summarize old turns into a shorter "memory summary". Keep recent turns verbatim.
        """,
        "use_when": "Customer support chatbots, research assistants, multi-turn Q&A, any conversational interface",
        "avoid_when": "Stateless APIs (no persistent session), batch processing, single-turn questions",
        "code": '''from rag_core import ConversationalRAG

rag = ConversationalRAG()
rag.add_documents(["Tell me about Tesla..."])

# Multi-turn works!
r1 = rag.ask("Who is Elon Musk?")
r2 = rag.ask("What companies does he run?")  # uses turn 1 context!
r3 = rag.ask("How many employees do they have?")  # uses turns 1+2!

print(f"History: {len(rag.history)} turns stored")''',
        "interview_q": "How does Conversational RAG handle follow-up questions like 'What about him?'",
        "interview_a": "Conversational RAG embeds each past Q&A turn and stores them in a separate FAISS index. On each new query, it retrieves not just from documents but also from conversation history. This means follow-up pronouns ('him', 'it', 'they') are resolved through context from previous turns. The challenge is context window growth — mitigated by summarizing old turns after N messages.",
    },
    {
        "name": "Rerank RAG",
        "emoji": "🔶",
        "tagline": "Two-Stage Precision",
        "complexity": "⭐⭐ Medium",
        "speed": "⚡ Slower",
        "color": "#F59E0B",
        "introduced": "2019 — MS MARCO paper, cross-encoders",
        "theory": """
**Two-stage retrieval: fast → precise**

**Why one stage isn't enough:**
Bi-encoders (like sentence-transformers) embed query and docs SEPARATELY. This is fast but loses query-document interaction.

Cross-encoders look at query AND document TOGETHER: "Given THIS query AND THIS document, how relevant is this document?"

**The architecture:**
- **Stage 1 (Bi-encoder, fast):** Retrieve top 20-50 candidates via vector search
- **Stage 2 (Cross-encoder, precise):** Re-score all candidates considering query-document interaction
- Return the top 3 from Stage 2

**Why not just use cross-encoder everywhere?**
Cross-encoders can't pre-index documents (they need the query). Running cross-encoder on 100K docs = too slow. So: use fast bi-encoder to narrow down, then precise cross-encoder for the shortlist.

**Typical model:** `cross-encoder/ms-marco-MiniLM-L-6-v2`

**Improvement over Naive RAG:** ~15-25% higher NDCG@10 on typical benchmarks.
        """,
        "use_when": "Legal contracts, medical Q&A, finance (accuracy critical), enterprise search",
        "avoid_when": "Latency-sensitive (<100ms needed), simple chatbots, resource-constrained environments",
        "code": '''from rag_core import RerankRAG

rag = RerankRAG(
    first_stage_k=20,   # retrieve 20 candidates first
    second_stage_k=3    # keep top 3 after reranking
)
rag.add_documents(["Contract text..."])
result = rag.ask("What are the payment terms?")

# Notice: higher scores than Naive RAG
for doc in result.retrieved_docs:
    print(f"Score: {doc.score:.3f} | {doc.retrieval_method}")''',
        "interview_q": "Why is a cross-encoder more accurate than a bi-encoder for reranking?",
        "interview_a": "Bi-encoders embed query and document independently, losing query-document interaction. Cross-encoders process query and document together as a single input, allowing attention to flow between them. This captures nuanced relevance like 'not helpful even though keywords match'. The trade-off: cross-encoders can't pre-encode documents (they need the query), making them O(n) per query — only practical for a small pre-filtered candidate set.",
    },
    {
        "name": "Contextual RAG",
        "emoji": "🟡",
        "tagline": "Token-Efficient",
        "complexity": "⭐⭐ Medium",
        "speed": "⚡⚡ Medium",
        "color": "#EAB308",
        "introduced": "2023 — LangChain ContextualCompressionRetriever",
        "theory": """
**The insight: Retrieved chunks contain a lot of noise.**

When you retrieve a 300-char chunk to answer "When was Einstein born?", most of the chunk is irrelevant:

```
"Einstein was born in 1879 in Germany. He developed     ← RELEVANT
the Theory of Relativity which changed physics forever.
He married twice. He played violin. His cat was named    ← IRRELEVANT
..."
```

Contextual RAG **compresses** retrieved chunks:
1. Split chunk into sentences
2. Embed each sentence AND the query
3. Compute cosine similarity for each sentence
4. Keep only sentences above a threshold (e.g., cosine > 0.3)
5. Send only the relevant sentences to LLM

**Benefits:**
- **Token savings:** 60-80% fewer tokens sent to LLM
- **Better answers:** LLM isn't confused by irrelevant context
- **Cost reduction:** Fewer tokens = lower API costs

**When to skip compression:**
- Short documents (not worth the overhead)
- Highly dense text (every sentence is relevant)
        """,
        "use_when": "Long documents (books, reports), cost-sensitive apps, when token budget is limited",
        "avoid_when": "Short docs, real-time systems (compression adds latency), highly dense technical text",
        "code": '''from rag_core import ContextualRAG

rag = ContextualRAG(
    compression_threshold=0.15  # keep sentences above this similarity
)
rag.add_documents(["Long article with lots of text..."])
result = rag.ask("When was Einstein born?")

# See how much was compressed
for doc in result.retrieved_docs:
    print(f"{doc.retrieval_method}")  # shows "compressed (XX% kept)"''',
        "interview_q": "How does Contextual Compression RAG reduce hallucinations?",
        "interview_a": "By compressing retrieved chunks to only the relevant sentences, we reduce the noise the LLM sees. LLMs are more likely to hallucinate when given large amounts of irrelevant context because they try to incorporate all the information. A focused, relevant context leads to more grounded answers. The compression also reduces the probability that an irrelevant but prominent sentence dominates the LLM's attention.",
    },
    {
        "name": "Self-Reflective RAG",
        "emoji": "🔮",
        "tagline": "Knows What It Doesn't Know",
        "complexity": "⭐⭐⭐ Hard",
        "speed": "⚡ Slower",
        "color": "#6366F1",
        "introduced": "2023 — SELF-RAG (Asai et al.)",
        "theory": """
**Paper:** *SELF-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection* (Asai et al., NeurIPS 2023)

**Core idea:** RAG shouldn't blindly retrieve for every question. And it shouldn't blindly use what it retrieved.

**Four reflection tokens SELF-RAG adds:**
- `[Retrieve]` — should I even retrieve for this query?
- `[IsRel]` — is this retrieved chunk relevant to my question?
- `[IsSup]` — does my answer support the retrieved text?
- `[IsUseful]` — is my final answer useful?

**Simplified pipeline:**
1. Decide if retrieval is needed
2. Retrieve
3. Score each doc: is it relevant?
4. If NOT relevant → expand query → retry
5. Generate answer
6. Grade: is answer grounded in docs?
7. Return answer + confidence

**Key innovation:** The model learns WHEN to use RAG vs when to answer directly. Not every query needs retrieval. Knowing when to skip is as important as knowing when to retrieve.
        """,
        "use_when": "Medical Q&A, fact-checking, academic research, any system where reliability > speed",
        "avoid_when": "Real-time systems, simple chatbots, when you need <200ms response",
        "code": '''from rag_core import SelfReflectiveRAG

rag = SelfReflectiveRAG(
    relevance_threshold=0.45,  # minimum score to consider docs relevant
    max_retries=2              # how many times to retry with different query
)
rag.add_documents(["Medical research papers..."])
result = rag.ask("What is the dosage for aspirin?")

# See reflection steps
for step in result.steps:
    print(f"{step['step']}: {step['detail']}")

# Self-grading result
print(f"Confidence: {result.confidence_score:.2f}")''',
        "interview_q": "What makes SELF-RAG different from standard RAG?",
        "interview_a": "SELF-RAG adds four critique tokens that allow the model to self-evaluate at each pipeline stage: should I retrieve? Is this chunk relevant? Is my answer supported by docs? Is the answer useful? This enables the model to skip retrieval for questions it can answer directly, retry with different queries when retrieved docs are irrelevant, and grade its own outputs to reduce hallucination. The model is fine-tuned to generate these special tokens, which is the key difference from standard post-hoc evaluation.",
    },
    {
        "name": "Corrective RAG",
        "emoji": "✅",
        "tagline": "Fact-Checker",
        "complexity": "⭐⭐⭐ Hard",
        "speed": "⚡ Slower",
        "color": "#10B981",
        "introduced": "2024 — CRAG (Yan et al.)",
        "theory": """
**Paper:** *Corrective Retrieval Augmented Generation* (Yan et al., 2024)

**Problem:** Standard RAG assumes retrieved docs are relevant and generates answers regardless.
If docs are irrelevant, the LLM hallucinates to fill the gap.

**CRAG solution:** Evaluate retrieval quality BEFORE generating. Three outcomes:

| Evaluation | Score | Action |
|-----------|-------|--------|
| **CORRECT** | High | Use docs confidently |
| **AMBIGUOUS** | Medium | Use docs but flag uncertainty |
| **INCORRECT** | Low | Tell user docs may not have the answer |

**Original CRAG also includes:**
- Web search fallback when local docs fail
- Knowledge refinement (filter/decompose web results)

**Our implementation:** Simplified CRAG using keyword overlap + embedding similarity to evaluate retrieval quality without a separate evaluator LLM.

**Key insight:** It's better to say "I'm not sure" than to confidently give a wrong answer.
        """,
        "use_when": "Compliance systems, medical diagnosis, financial advice, any domain where confident wrong answers are dangerous",
        "avoid_when": "Creative apps, casual chatbots, when some uncertainty is acceptable",
        "code": '''from rag_core import CorrectiveRAG

rag = CorrectiveRAG()
rag.add_documents(["Your domain documents..."])

result = rag.ask("What is the maximum safe dosage?")

# Answer includes confidence classification
print(result.answer)  # might say "⚠️ Low confidence — docs may not contain this"

# Check confidence
print(f"Confidence: {result.confidence_score:.2f}")
for step in result.steps:
    if "Evaluate" in step["step"]:
        print(step["detail"])  # CORRECT / AMBIGUOUS / INCORRECT''',
        "interview_q": "How does CRAG reduce hallucination compared to standard RAG?",
        "interview_a": "CRAG adds an evaluation step after retrieval to classify whether retrieved documents are CORRECT (relevant), AMBIGUOUS (partially relevant), or INCORRECT (irrelevant) for the query. Based on this classification, it adjusts the answer accordingly — returning a confident answer when docs are relevant, flagging uncertainty when partially relevant, or warning the user when docs are clearly irrelevant. This prevents the LLM from generating confident but hallucinated answers from irrelevant context.",
    },
    {
        "name": "Adaptive RAG",
        "emoji": "🔀",
        "tagline": "Smart Router",
        "complexity": "⭐⭐⭐ Hard",
        "speed": "⚡⚡ Variable",
        "color": "#EC4899",
        "introduced": "2024 — Adaptive-RAG (Jeong et al.)",
        "theory": """
**Paper:** *Adaptive-RAG: Learning to Adapt Retrieval-Augmented Large Language Models through Question Complexity* (Jeong et al., 2024)

**Core insight:** One RAG strategy doesn't fit all queries.

| Query Type | Example | Best Strategy |
|-----------|---------|---------------|
| Simple factual | "What year did WWII end?" | No RAG (LLM knows this) |
| Medium | "What are Tesla's 2024 revenues?" | Single RAG retrieval |
| Complex | "Compare Tesla vs Rivian growth strategy" | Multi-step retrieval |

**The router:**
Original paper uses a trained classifier (fine-tuned LM) to predict query complexity.
Our simplified version uses heuristic rules:
- Short + no keywords → SIMPLE → Naive RAG
- Has names/codes/numbers → KEYWORD → Hybrid RAG
- Long + comparison words → COMPLEX → Rerank RAG

**Benefits:**
- Simple queries: 3x faster (no retrieval needed)
- Complex queries: 2x more accurate (better RAG)
- Average: better speed/accuracy tradeoff than any single approach
        """,
        "use_when": "Production systems with mixed query types, when you want optimal speed AND accuracy",
        "avoid_when": "When all your queries are similar complexity (routing overhead not worth it)",
        "code": '''from rag_core import AdaptiveRAG

rag = AdaptiveRAG()
rag.add_documents(["Mixed content..."])

# Each query gets routed to the best RAG type!
r1 = rag.ask("What year?")          # → routes to Naive RAG
r2 = rag.ask("What is TSLA price?") # → routes to Hybrid RAG (has ticker)
r3 = rag.ask("Compare Tesla vs Apple business strategy")  # → routes to Rerank

# See which RAG was chosen
print(r1.rag_type)  # "Adaptive RAG → Naive RAG"
print(r2.rag_type)  # "Adaptive RAG → Hybrid RAG"
print(r3.rag_type)  # "Adaptive RAG → Rerank RAG"''',
        "interview_q": "How does Adaptive RAG decide which retrieval strategy to use?",
        "interview_a": "Adaptive-RAG trains a lightweight classifier to predict query complexity from the question text alone. It uses fine-tuned DistilBERT/similar models to classify queries as single-hop (simple retrieval), multi-hop (chained retrieval), or no-retrieval needed. In production, simpler heuristics work well: query length, presence of comparison words, named entities, and numbers are strong signals of complexity. The key insight is that routing overhead is small compared to the gains from using the right strategy.",
    },
    {
        "name": "Multi-Hop RAG",
        "emoji": "🔗",
        "tagline": "Chain-of-Retrieval",
        "complexity": "⭐⭐⭐ Hard",
        "speed": "⚡ Slower",
        "color": "#F97316",
        "introduced": "2021 — HotpotQA, IRCOT",
        "theory": """
**For questions that require multiple steps to answer:**

Example: "What nationality is the CEO of the company that makes iPhone?"
- Step 1: Find → "iPhone is made by Apple"
- Step 2: Find → "Apple's CEO is Tim Cook"
- Step 3: Find → "Tim Cook is American"
- Synthesis: "The CEO is American"

**No single retrieval can answer this** because the answer depends on intermediate findings.

**Key algorithms:**
- **IRCOT (2022):** Interleave retrieval with chain-of-thought reasoning
- **ReAct (2022):** Reason + Act framework — think, retrieve, think again
- **MDR (2021):** Multi-step dense retrieval using recursive entity expansion

**Error propagation risk:**
If Hop 1 gives wrong entity, Hop 2 goes completely wrong.
Solution: Use Corrective RAG at each hop to verify before proceeding.
        """,
        "use_when": "Research assistants, genealogy, supply chain Q&A ('who makes the chip in X?'), knowledge graph traversal",
        "avoid_when": "Simple factual questions, real-time systems, when context is fully self-contained",
        "code": '''from rag_core import MultiHopRAG

rag = MultiHopRAG(max_hops=2)
rag.add_documents(["Company info, people info, product info..."])

# Multi-step question
result = rag.ask("Who invented the telescope and what did they discover?")

# See each hop
for step in result.steps:
    print(f"{step['step']}: {step['detail']}")
# → Hop 1: Retrieved info about telescope inventor
# → Entity Extract: Found "Galileo"
# → Hop 2: Retrieved info about Galileo's discoveries''',
        "interview_q": "Explain Multi-hop RAG and when it's needed.",
        "interview_a": "Multi-hop RAG chains multiple retrieval steps where each hop's results inform the next query. It's needed for bridge questions — where the answer to Question A is used to form Question B. For example: 'What is the birth city of the author of Harry Potter?' requires knowing J.K. Rowling first, then retrieving her birthplace. The key challenges are error propagation (wrong first hop corrupts second hop) and latency (multiple retrieval rounds). It's best used with Corrective RAG at each step to validate intermediate results.",
    },
    {
        "name": "Graph RAG",
        "emoji": "🕸️",
        "tagline": "Relationship-Aware",
        "complexity": "⭐⭐⭐ Hard",
        "speed": "⚡ Slower",
        "color": "#8B5CF6",
        "introduced": "2024 — Microsoft GraphRAG (Edge et al.)",
        "theory": """
**Paper:** *From Local to Global: A Graph RAG Approach to Query-Focused Summarization* (Edge et al., Microsoft, 2024)

**Why vector search misses relationships:**
- "Tesla and SpaceX are both founded by Elon Musk"
- Query: "What do Tesla and SpaceX have in common?"
- Vector search: finds separate chunks about each company
- Graph RAG: traverses edges → finds shared node (Elon Musk) → answers directly

**Graph construction:**
1. Extract entities (people, places, orgs) from documents
2. Extract relationships (founded_by, works_at, located_in)
3. Build a knowledge graph: nodes = entities, edges = relations
4. Store graph in Neo4j or in-memory dict

**At query time:**
1. Extract query entities
2. Find them in the graph
3. Traverse N hops of edges
4. Collect context from connected nodes
5. LLM answers from graph subgraph

**Microsoft's result:** GraphRAG outperforms standard RAG on global summarization tasks by 15-30% on comprehensiveness metrics.
        """,
        "use_when": "Org charts, supply chains, knowledge bases with rich relationships, 'how are X and Y connected?' queries",
        "avoid_when": "Unstructured text with no clear entities, real-time, simpler use cases",
        "code": '''# Graph RAG (conceptual — production needs Neo4j)
# Our simplified version uses dict-based graph

# Build knowledge graph manually:
graph = {
    "Einstein": {"born_in": "Germany", "published": "Theory of Relativity"},
    "Germany": {"capital": "Berlin"},
    "Theory of Relativity": {"published_year": "1905"},
}

# Query: "Where was the author of Relativity born?"
# → Find "Theory of Relativity" → traverse "published" edge
# → Find "Einstein" → traverse "born_in" edge → "Germany"''',
        "interview_q": "Why does Microsoft's GraphRAG outperform standard RAG for summarization?",
        "interview_a": "Standard RAG struggles with global queries ('What are the main themes?') because no single chunk captures the big picture. GraphRAG builds a knowledge graph from the corpus, then creates community summaries at multiple levels of the graph hierarchy. For global queries, it can retrieve high-level community summaries rather than specific chunks, enabling comprehensive answers across an entire corpus. For local queries (specific entities), it traverses graph relationships to find contextually connected information that vector search would miss.",
    },
    {
        "name": "Agentic RAG",
        "emoji": "🤖",
        "tagline": "Self-Directing Agent",
        "complexity": "⭐⭐⭐ Hard",
        "speed": "⚡ Slowest",
        "color": "#F97316",
        "introduced": "2023 — ReAct, LangChain Agents",
        "theory": """
**RAG controlled by an AI agent that plans its own actions.**

Standard RAG: fixed pipeline (always retrieve → always generate)
Agentic RAG: LLM decides WHAT to do at each step

**Agent loop:**
```
LOOP:
  1. Think: "What information do I have? What do I need?"
  2. Act: Choose action (retrieve docs, search web, call API, calculate, ask user)
  3. Observe: Get result of action
  4. Think: "Is this enough to answer? Need more steps?"
UNTIL: Confident enough to answer
```

**Available tools:**
- RAG retrieval (knowledge base)
- Web search (live internet)
- Calculator
- SQL query
- API calls

**When to use:** Complex tasks requiring multiple diverse information sources, decision trees, or iterative refinement.

**Cost warning:** Each loop iteration = LLM call. A 5-step agent = 5x cost of single RAG call.
        """,
        "use_when": "Research automation, complex analysis, 'find AND summarize AND compare AND recommend', multi-source synthesis",
        "avoid_when": "Simple Q&A, latency-critical, cost-sensitive, when a fixed pipeline works fine",
        "code": '''# Agentic RAG (uses LangChain agents in production)
# Conceptual code showing agent loop:

from langchain.agents import AgentExecutor, create_react_agent
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
        "interview_a": "Standard RAG follows a fixed pipeline: retrieve → generate. Agentic RAG uses an LLM to plan and execute its own retrieval strategy using a ReAct (Reason + Act) loop. The agent decides what to retrieve, when to retrieve, which tools to use, and when it has enough information. This enables handling of complex multi-step tasks but at much higher cost (multiple LLM calls per query) and latency. Agentic RAG is justified when the query complexity can't be anticipated ahead of time.",
    },
]

# ─── DISPLAY ──────────────────────────────────────────────
# Overview grid
st.subheader("🗺️ All 11 Architectures — Quick Overview")

cols = st.columns(4)
for i, rag in enumerate(ENCYCLOPEDIA):
    with cols[i % 4]:
        st.markdown(f"""
<div style="background:{rag['color']}11;border:1px solid {rag['color']};border-radius:10px;
     padding:10px;text-align:center;margin:4px 0;height:90px">
  <div style="font-size:1.5rem">{rag['emoji']}</div>
  <div style="color:#e2e8f0;font-size:0.82rem;font-weight:700">{rag['name']}</div>
  <div style="color:#94a3b8;font-size:0.7rem">{rag['complexity']} · {rag['speed']}</div>
</div>
""", unsafe_allow_html=True)

st.divider()

# Filter / Search
search = st.text_input("🔍 Search architecture by name or complexity:", placeholder="e.g. 'Hybrid' or 'Hard'")
filtered = [r for r in ENCYCLOPEDIA if not search or search.lower() in r['name'].lower()
            or search.lower() in r['complexity'].lower() or search.lower() in r['tagline'].lower()]

st.caption(f"Showing {len(filtered)}/{len(ENCYCLOPEDIA)} architectures")

# Detailed cards
for rag in filtered:
    with st.expander(f"{rag['emoji']} {rag['name']} — {rag['tagline']}   [{rag['complexity']} · {rag['speed']}]"):
        col1, col2 = st.columns([1, 1])

        with col1:
            # Visual pipeline diagram
            st.markdown("#### 🎨 Pipeline Visualization")
            diagram_html = get_rag_diagram(rag['name'])
            st.markdown(diagram_html, unsafe_allow_html=True)

            # Use when / avoid when
            st.markdown("#### 📋 When to Use")
            c1, c2 = st.columns(2)
            with c1:
                st.success(f"✅ **Use when:**\n{rag['use_when']}")
            with c2:
                st.error(f"❌ **Avoid when:**\n{rag['avoid_when']}")

        with col2:
            # Theory
            st.markdown(f"#### 📖 Theory  `{rag['introduced']}`")
            st.markdown(rag['theory'])

            # Code snippet
            st.markdown("#### 💻 Quick Code")
            st.code(rag['code'], language="python")

            # Interview Q&A
            with st.container():
                st.markdown("#### 🎓 Interview Q&A")
                st.markdown(f"**Q: {rag['interview_q']}**")
                st.info(f"**A:** {rag['interview_a']}")

st.divider()

# Quick comparison table
st.subheader("⚖️ Quick Comparison Table")

comparison_data = {
    "RAG Type": [r["emoji"] + " " + r["name"] for r in ENCYCLOPEDIA],
    "Complexity": [r["complexity"] for r in ENCYCLOPEDIA],
    "Speed": [r["speed"] for r in ENCYCLOPEDIA],
    "Best For": [r["use_when"][:50] + "..." for r in ENCYCLOPEDIA],
}

import pandas as pd
st.dataframe(pd.DataFrame(comparison_data), width='stretch', hide_index=True)

with st.sidebar:
    st.markdown("## 🗺️ Navigation")
    st.page_link("app.py", label="🏠 Home")
    st.page_link("pages/1_When_To_Use_RAG.py", label="1️⃣ When to Use RAG")
    st.page_link("pages/2_How_RAG_Works.py", label="2️⃣ How RAG Works")
    st.page_link("pages/3_Test_Any_RAG.py", label="3️⃣ Test Any RAG ⭐")
    st.page_link("pages/4_Compare_RAGs.py", label="4️⃣ Compare RAG Types")
    st.page_link("pages/5_RAG_Encyclopedia.py", label="5️⃣ Encyclopedia 📖")
    st.page_link("pages/6_Build_Your_Own.py", label="6️⃣ Build Your Own 🛠️")
