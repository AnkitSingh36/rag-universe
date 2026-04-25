# 🌌 RAG Universe

> **The complete guide to Retrieval-Augmented Generation.**
> Theory · Visualization · 9 Runnable RAG Types · Build Your Own

---

## 🤔 What Is RAG? (Plain English)

**Without RAG:** AI answers from memory (may be outdated or hallucinated).  
**With RAG:** AI reads YOUR documents first, then answers from verified source.

```
RAG = Open Book Exam for AI
No RAG = Closed Book Exam (AI guesses from memory)
```

---

## 🚀 Setup in 5 Minutes

```bash
git clone https://github.com/YOUR_USERNAME/rag-universe.git
cd rag-universe
pip install -r requirements.txt
streamlit run app.py
```

Open `http://localhost:8501`. No API key needed. Works fully offline.

---

## 🗺️ Project Structure

```
rag-universe/
│
├── app.py                          ← 🏠 Home page (start here)
│
├── pages/
│   ├── 1_When_To_Use_RAG.py       ← 1️⃣ Should you use RAG? (quiz + 9 scenarios)
│   ├── 2_How_RAG_Works.py         ← 2️⃣ Step-by-step visual explainer
│   ├── 3_Test_Any_RAG.py          ← ⭐ Test any of 9 RAG types live
│   ├── 4_Compare_RAGs.py          ← 4️⃣ Side-by-side comparison
│   ├── 5_RAG_Encyclopedia.py      ← 📖 All 11 architectures: theory + diagram
│   └── 6_Build_Your_Own.py        ← 🛠️ Template + guide to add your own
│
├── rag_core/
│   ├── base.py                    ← Document & RAGResult data models
│   ├── utils.py                   ← Chunker, embedder, demo LLM
│   ├── naive_rag.py               ← 🔵 Pure vector search
│   ├── hybrid_rag.py              ← 🟣 BM25 + Vector + RRF
│   ├── conversational_rag.py      ← 🟢 Multi-turn memory
│   ├── rerank_rag.py              ← 🔶 Two-stage precision
│   ├── contextual_rag.py          ← 🟡 Token compression
│   ├── self_reflective_rag.py     ← 🔮 SELF-RAG (reflects on quality)
│   ├── corrective_rag.py          ← ✅ CRAG (fact-checking)
│   ├── adaptive_rag.py            ← 🔀 Smart query routing
│   └── multihop_rag.py            ← 🔗 Multi-step retrieval
│
├── rag_diagrams/
│   └── pipeline.py                ← Visual HTML pipelines for all 11 RAG types
│
├── data/
│   └── sample_data.py             ← 5 sample topics (Space, Animals, India, Tech, Sports)
│
└── requirements.txt
```

---

## 🧪 How to Test Each RAG Type

### Test 1 — Naive RAG (baseline)
1. Open app → **⭐ Test Any RAG**
2. Topic: `🚀 Space Exploration`
3. RAG: **Naive RAG**
4. Ask: `"Who first walked on the Moon?"`
5. ✅ Look for: yellow query-word highlights in retrieved chunks, relevance score bars

### Test 2 — Hybrid RAG (keyword + semantic)
1. Topic: `💻 Technology & AI`
2. RAG: **Hybrid RAG**
3. Ask: `"What is RAG?"`
4. ✅ Look for: chunks labeled `hybrid (both)` — found by BOTH BM25 and vector

### Test 3 — Conversational RAG (multi-turn)
1. Topic: `🐘 Animals & Wildlife`
2. RAG: **Conversational RAG**
3. Ask question 1 → Run, then ask `"How much do they eat?"` → Run
4. ✅ Look for: "Conversation Memory" section showing stored turns

### Test 4 — Rerank RAG (two-stage precision)
1. RAG: **Rerank RAG**
2. Same topic + question as Test 1
3. ✅ Look for: chunks labeled `reranked (from top-20)` and higher scores vs Naive

### Test 5 — Self-Reflective RAG (self-checking)
1. RAG: **Self-Reflective RAG**
2. Ask something NOT in the document
3. ✅ Look for: reflection steps → query expansion → low-confidence flag

### Test 6 — Corrective RAG (confidence grading)
1. RAG: **Corrective RAG**
2. Ask something partially covered in the document
3. ✅ Look for: CORRECT / AMBIGUOUS / INCORRECT classification in answer

### Test 7 — Adaptive RAG (auto-routing)
Run 3 questions with different complexity:
```
Short:   "What year?" → routes to Naive RAG
Code:    "What is ISRO?" → routes to Hybrid RAG
Complex: "Compare and contrast..." → routes to Rerank RAG
```
✅ Look for: `[Adaptive routing: Used X RAG]` at start of each answer

### Test 8 — Multi-Hop RAG (chained reasoning)
1. Topic: `⚽ Sports & Games`
2. RAG: **Multi-Hop RAG**
3. Ask: `"Who has the most centuries and how many?"`
4. ✅ Look for: "Hop 2 Retrieve (via 'Sachin')" or similar entity extraction

### Test 9 — Compare All Types
1. Go to **4️⃣ Compare RAG Types**
2. Select 3-5 RAG types
3. Ask any question
4. ✅ Look for: latency chart, score chart, side-by-side answers, chunk comparison

### Test 10 — Your Own Text
1. **⭐ Test Any RAG** → Paste Your Own
2. Paste any Wikipedia article or your own notes
3. Ask questions about it
4. ✅ Any RAG type will work on your custom text

---

## 📖 The 11 RAG Architectures (Quick Reference)

| # | Type | Core Idea | Best For | Complexity |
|---|------|-----------|----------|-----------|
| 1 | 🔵 **Naive RAG** | Embed → vector search → answer | Learning, simple QA | ⭐ Simple |
| 2 | 🟣 **Hybrid RAG** | BM25 + Vector + RRF fusion | Mixed keyword/semantic | ⭐⭐ Medium |
| 3 | 🟢 **Conversational RAG** | Stores & retrieves chat history | Multi-turn chatbots | ⭐⭐ Medium |
| 4 | 🔶 **Rerank RAG** | Fast retrieve → precise rerank | Legal, medical, finance | ⭐⭐ Medium |
| 5 | 🟡 **Contextual RAG** | Compresses chunks to relevant sentences | Long docs, token savings | ⭐⭐ Medium |
| 6 | 🔮 **Self-Reflective RAG** | Evaluates retrieval & answer quality | High-reliability systems | ⭐⭐⭐ Hard |
| 7 | ✅ **Corrective RAG** | Grades retrieval CORRECT/AMBIGUOUS/INCORRECT | Compliance, safety | ⭐⭐⭐ Hard |
| 8 | 🔀 **Adaptive RAG** | Routes query to best RAG type | Mixed-workload production | ⭐⭐⭐ Hard |
| 9 | 🔗 **Multi-Hop RAG** | Chains multiple retrievals via entity extraction | Complex multi-step questions | ⭐⭐⭐ Hard |
| 10 | 🕸️ **Graph RAG** | Knowledge graph traversal | Relationship-heavy data | ⭐⭐⭐ Hard |
| 11 | 🤖 **Agentic RAG** | Agent plans its own retrieval actions | Research automation | ⭐⭐⭐ Hard |

*Types 1-9 are fully implemented and runnable. Types 10-11 are documented in the Encyclopedia with diagrams and code.*

---

## 🛠️ Add Your Own RAG Type (30 Minutes)

See the full guide on **Page 6** in the app. Here's the one-slide summary:

### Step 1: Create `rag_core/my_rag.py`
```python
from .base import BaseRAG, Document, RAGResult
from .utils import chunk_text, embed_texts, demo_generate

class MyRAG(BaseRAG):
    name = "My RAG"
    description = "What it does"
    emoji = "🆕"
    color = "#FF6B6B"

    def add_documents(self, texts, source="doc"):
        # chunk → embed → index
        ...

    def retrieve(self, query, top_k=3):
        # return List[Document]
        ...

    def ask(self, query, top_k=3, use_ollama=False):
        # return RAGResult
        ...
```

### Step 2: Add to `rag_core/__init__.py`
```python
from .my_rag import MyRAG
ALL_RAG_TYPES["🆕 My RAG"] = MyRAG
```

### Step 3: Add diagram to `rag_diagrams/pipeline.py`
```python
def diagram_my_rag():
    content = _row(_box("Query","❓","#FF6B6B"), _arrow(), _box("Answer","💬","#10B981"))
    return _wrap(content, "🆕 My RAG", "Subtitle")
DIAGRAM_MAP["My RAG"] = diagram_my_rag
```

Done! Your RAG appears in all app pages automatically.

---

## ❓ FAQ

**Q: Do I need API keys?**  
A: No. Everything works offline with demo mode. Optionally install [Ollama](https://ollama.ai) for richer answers.

**Q: What is "demo mode"?**  
A: Without an LLM, we extract the most relevant sentence from retrieved chunks. This is extractive QA — it shows exactly what retrieval found, which is the educational part!

**Q: How are scores calculated?**  
A: Scores are L2 distance → similarity: `1 / (1 + l2_distance)`. Score near 1.0 = very relevant. Score near 0.0 = not relevant.

**Q: Can I use my own documents?**  
A: Yes! On Page 3, choose "Paste your own text" and add any text. PDFs can be converted to text first with: `pdfplumber`, `PyMuPDF`, or `pdf2txt`.

**Q: Why does my question get low scores?**  
A: The answer isn't in your documents. RAG can only answer from what you give it.

**Q: What's the difference between Corrective RAG and Self-Reflective RAG?**  
A: CRAG evaluates retrieval quality and grades the final answer confidence. SELF-RAG evaluates at every step: before retrieval, during, and after — it can also decide NOT to retrieve.

---

## 📚 Key Concepts Glossary

| Term | Plain English |
|------|--------------|
| **Embedding** | Text → list of 384 numbers (meaning fingerprint) |
| **Chunk** | Small piece of a document (~300 characters) |
| **FAISS** | Fast vector search library (Facebook AI) |
| **BM25** | Keyword search algorithm (counts word frequency) |
| **RRF** | Reciprocal Rank Fusion — merges two ranked lists |
| **Cross-encoder** | Model that scores query+document together (accurate but slow) |
| **Bi-encoder** | Embeds query and doc separately (fast but less accurate) |
| **Hallucination** | AI confidently stating something false |
| **Top-k** | Retrieve the k most relevant chunks |
| **LLM** | Large Language Model (GPT, Claude, Mistral...) |
| **RAG** | Retrieve first, then generate answer from retrieved text |

---

## ⚡ Optional: Richer Answers with Ollama

```bash
# Install Ollama (free, runs on your machine)
# Visit: https://ollama.ai

# Download Mistral 7B (4GB, one-time)
ollama pull mistral

# Start Ollama service
ollama serve

# In the app: enable "Use Ollama LLM" toggle in sidebar
```

---

## ⭐ If This Helped You

Star the repo! It helps other developers find this resource.

---

*Built for developers who want to actually understand RAG — not just copy-paste tutorials.*
