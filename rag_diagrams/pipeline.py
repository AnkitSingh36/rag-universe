"""
rag_diagrams/pipeline.py

Generates beautiful HTML pipeline diagrams for all RAG architectures.
Each diagram shows boxes, arrows, labels, and decision nodes.

Usage:
    from rag_diagrams.pipeline import get_rag_diagram
    html = get_rag_diagram("Naive RAG")
    st.markdown(html, unsafe_allow_html=True)
"""

from typing import List, Dict, Any

# ─────────────────────────────────────────────────────
# HTML builder helpers
# ─────────────────────────────────────────────────────

def _box(label: str, icon: str, color: str, desc: str = "", width: str = "130px",
         shape: str = "rect", bg: str = "transparent") -> str:
    """Render a single pipeline box."""
    border_radius = "50%" if shape == "circle" else "14px" if shape == "diamond-like" else "10px"
    return f"""
<div style="
  display:inline-flex;flex-direction:column;align-items:center;justify-content:center;
  width:{width};min-height:80px;padding:10px 6px;
  background:linear-gradient(135deg,{color}22,{color}11);
  border:2px solid {color};border-radius:{border_radius};
  text-align:center;position:relative;
">
  <span style="font-size:1.6rem">{icon}</span>
  <span style="color:#e2e8f0;font-size:0.78rem;font-weight:700;margin-top:4px;line-height:1.2">{label}</span>
  {f'<span style="color:#94a3b8;font-size:0.65rem;margin-top:3px">{desc}</span>' if desc else ''}
</div>"""

def _arrow(label: str = "", color: str = "#6366f1", vertical: bool = False) -> str:
    if vertical:
        return f"""
<div style="display:flex;flex-direction:column;align-items:center;padding:2px 0">
  <div style="width:2px;height:20px;background:{color}"></div>
  <div style="color:{color};font-size:1rem">▼</div>
  {f'<span style="color:#94a3b8;font-size:0.65rem">{label}</span>' if label else ''}
</div>"""
    return f"""
<div style="display:flex;align-items:center;padding:0 4px">
  <div style="height:2px;width:20px;background:{color}"></div>
  <div style="color:{color};font-size:1rem">▶</div>
  {f'<span style="color:#94a3b8;font-size:0.65rem;margin-left:3px">{label}</span>' if label else ''}
</div>"""

def _row(*items: str, gap: str = "4px") -> str:
    inner = "".join(items)
    return f'<div style="display:flex;flex-wrap:wrap;align-items:center;justify-content:center;gap:{gap};margin:6px 0">{inner}</div>'

def _col(*items: str) -> str:
    inner = "".join(items)
    return f'<div style="display:flex;flex-direction:column;align-items:center;gap:4px">{inner}</div>'

def _badge(text: str, color: str) -> str:
    return f'<span style="background:{color}22;color:{color};border:1px solid {color};border-radius:999px;padding:2px 10px;font-size:0.7rem;font-weight:600">{text}</span>'

def _decision(label: str, yes: str, no: str, color: str = "#f59e0b") -> str:
    """Decision diamond with yes/no branches."""
    return f"""
<div style="display:flex;flex-direction:column;align-items:center;gap:4px">
  <div style="
    width:100px;height:50px;
    background:linear-gradient(135deg,{color}22,{color}11);
    border:2px solid {color};
    clip-path:polygon(50% 0%,100% 50%,50% 100%,0% 50%);
    display:flex;align-items:center;justify-content:center;
    font-size:0.72rem;font-weight:700;color:{color};text-align:center;
    padding:5px;
  ">{label}</div>
  <div style="display:flex;gap:16px">
    {_badge(f"✅ {yes}", "#10b981")}
    {_badge(f"❌ {no}", "#ef4444")}
  </div>
</div>"""

def _loop_badge(text: str) -> str:
    return f'<div style="background:#6366f111;border:1px dashed #6366f1;border-radius:8px;padding:5px 12px;font-size:0.72rem;color:#6366f1;margin:4px 0">🔄 {text}</div>'

def _wrap(content: str, title: str, subtitle: str = "") -> str:
    return f"""
<div style="background:#0f172a;border:1px solid #1e293b;border-radius:16px;padding:20px;margin:8px 0">
  <div style="text-align:center;margin-bottom:12px">
    <strong style="color:#e2e8f0;font-size:1rem">{title}</strong>
    {f'<br><span style="color:#94a3b8;font-size:0.78rem">{subtitle}</span>' if subtitle else ''}
  </div>
  {content}
</div>"""

# ─────────────────────────────────────────────────────
# Individual RAG Diagrams
# ─────────────────────────────────────────────────────

def diagram_naive_rag() -> str:
    content = _row(
        _box("Your Docs", "📄", "#3B82F6", "PDF, text, notes"),
        _arrow(),
        _box("Chunker", "🔪", "#8B5CF6", "Split into ~300 char pieces"),
        _arrow(),
        _box("Embedder", "🔢", "#EC4899", "Text → 384 numbers"),
        _arrow(),
        _box("Vector DB", "🗄️", "#10B981", "Store all vectors (FAISS)"),
    )
    content += _row(
        _box("Query", "❓", "#F59E0B", "User's question"),
        _arrow(),
        _box("Embed Query", "🔢", "#EC4899", "Query → vector"),
        _arrow(),
        _box("Search", "🔍", "#6366F1", "Find closest vectors"),
        _arrow(),
        _box("Top-k Chunks", "📋", "#10B981", "Most relevant pieces"),
        _arrow(),
        _box("LLM", "🤖", "#F97316", "Read + answer"),
        _arrow(),
        _box("Answer", "💬", "#10B981", "Final response"),
    )
    return _wrap(content, "🔵 Naive RAG Pipeline", "Embed everything → find closest match → answer")

def diagram_hybrid_rag() -> str:
    content = _row(
        _box("Query", "❓", "#8B5CF6", "User question"),
        _arrow(),
        _col(
            _box("BM25 Search", "🔤", "#3B82F6", "Keyword match\n(exact words)", "120px"),
            _box("Vector Search", "🧠", "#8B5CF6", "Semantic match\n(meaning)", "120px"),
        ),
        _arrow(label="RRF Fusion"),
        _box("Merged Results", "🔀", "#EC4899", "Best of both"),
        _arrow(),
        _box("LLM", "🤖", "#F97316"),
        _arrow(),
        _box("Answer", "💬", "#10B981"),
    )
    content += f"""
<div style="text-align:center;margin-top:8px">
  <code style="color:#94a3b8;font-size:0.72rem">
    RRF Score = 1/(60+rank_bm25) + 1/(60+rank_vector)
  </code>
</div>"""
    return _wrap(content, "🟣 Hybrid RAG Pipeline", "BM25 (keywords) + Vector (meaning) → fused with RRF")

def diagram_conversational_rag() -> str:
    content = _row(
        _box("New Query", "❓", "#10B981"),
        _arrow(),
        _col(
            _box("Vector Search\n(docs)", "🔍", "#10B981", "Current knowledge"),
            _box("History Search\n(past turns)", "💬", "#6366F1", "Previous Q&A"),
        ),
        _arrow("merge"),
        _box("Combined\nContext", "📋", "#EC4899", "Docs + history"),
        _arrow(),
        _box("LLM", "🤖", "#F97316"),
        _arrow(),
        _box("Answer", "💬", "#10B981"),
    )
    content += _row(
        _badge("💾 Store turn in memory", "#6366f1"),
        _badge("🔄 Used in next query", "#10b981"),
    )
    return _wrap(content, "🟢 Conversational RAG Pipeline", "Remembers conversation history for follow-up questions")

def diagram_rerank_rag() -> str:
    content = _row(
        _box("Query", "❓", "#F59E0B"),
        _arrow(),
        _box("Stage 1\nVector Search", "🔍", "#3B82F6", "Fast: top 20 chunks", "120px"),
        _arrow("20 candidates"),
        _box("Stage 2\nReranker", "⚖️", "#F59E0B", "Precise cross-encoder\nscoring", "120px"),
        _arrow("top 3"),
        _box("LLM", "🤖", "#F97316"),
        _arrow(),
        _box("Answer", "💬", "#10B981"),
    )
    content += _row(
        _badge("Stage 1: Fast (BiEncoder)", "#3B82F6"),
        _badge("Stage 2: Accurate (CrossEncoder)", "#F59E0B"),
    )
    return _wrap(content, "🔶 Rerank RAG Pipeline", "Two stages: fast rough retrieval → precise reranking")

def diagram_contextual_rag() -> str:
    content = _row(
        _box("Query", "❓", "#EAB308"),
        _arrow(),
        _box("Retrieve\nChunks", "🔍", "#3B82F6", "Top-k full chunks"),
        _arrow(),
        _box("Compress\nEach Chunk", "✂️", "#EAB308", "Remove irrelevant\nsentences", "130px"),
        _arrow(),
        _box("Focused\nContext", "🎯", "#10B981", "Only relevant parts"),
        _arrow(),
        _box("LLM", "🤖", "#F97316"),
        _arrow(),
        _box("Answer", "💬", "#10B981"),
    )
    content += _row(
        _badge("Before: 300 chars/chunk", "#EF4444"),
        _badge("After: ~60 chars/chunk", "#10B981"),
        _badge("Token savings: ~80%", "#6366F1"),
    )
    return _wrap(content, "🟡 Contextual Compression RAG Pipeline", "Removes irrelevant sentences after retrieval — saves tokens")

def diagram_self_reflective_rag() -> str:
    content = _row(
        _box("Query", "❓", "#6366F1"),
        _arrow(),
        _decision("Need RAG?", "Retrieve", "Answer directly", "#6366F1"),
        _arrow(),
        _box("Retrieve", "🔍", "#3B82F6"),
    )
    content += _row(
        _arrow(vertical=True),
    )
    content += _row(
        _decision("Relevant?", "Proceed", "Re-retrieve", "#8B5CF6"),
    )
    content += _loop_badge("Query expansion → retry up to 2 times if docs not relevant")
    content += _row(
        _arrow(),
        _box("LLM", "🤖", "#F97316"),
        _arrow(),
        _decision("Grounded?", "Return", "Flag uncertainty", "#EC4899"),
    )
    return _wrap(content, "🔮 Self-Reflective RAG Pipeline", "SELF-RAG: Reflects on retrieval & answer quality at each step")

def diagram_corrective_rag() -> str:
    content = _row(
        _box("Query", "❓", "#10B981"),
        _arrow(),
        _box("Retrieve", "🔍", "#3B82F6"),
        _arrow(),
        _box("Evaluate\nRelevance", "🔬", "#F59E0B", "Score 0–1"),
    )
    content += _row(
        _col(
            _badge("✅ CORRECT (>0.55)", "#10B981"),
            _badge("⚠️ AMBIGUOUS (0.3-0.55)", "#F59E0B"),
            _badge("❌ INCORRECT (<0.3)", "#EF4444"),
        ),
    )
    content += _row(
        _col(
            _box("Confident\nAnswer", "✅", "#10B981", "Full answer"),
            _box("Partial\nAnswer", "⚠️", "#F59E0B", "With uncertainty flag"),
            _box("Low-confidence\nAnswer", "❌", "#EF4444", "Warn user"),
        ),
    )
    return _wrap(content, "✅ Corrective RAG (CRAG) Pipeline", "Evaluates doc relevance → corrects answer confidence accordingly")

def diagram_adaptive_rag() -> str:
    content = _row(
        _box("Query", "❓", "#EC4899"),
        _arrow(),
        _box("Classifier", "🤔", "#EC4899", "Analyze complexity"),
    )
    content += _row(
        _col(
            _badge("Short + factual", "#3B82F6"),
            _box("Naive RAG", "🔵", "#3B82F6", "Fast, simple"),
        ),
        _col(
            _badge("Has names/codes", "#8B5CF6"),
            _box("Hybrid RAG", "🟣", "#8B5CF6", "Keywords+Meaning"),
        ),
        _col(
            _badge("Complex/multi-concept", "#F59E0B"),
            _box("Rerank RAG", "🔶", "#F59E0B", "Accurate, slow"),
        ),
    )
    content += _row(
        _arrow(), _box("Answer", "💬", "#10B981"),
    )
    return _wrap(content, "🔀 Adaptive RAG Pipeline", "Routes each query to the right RAG type based on complexity")

def diagram_multihop_rag() -> str:
    content = _row(
        _box("Complex\nQuery", "❓", "#F97316", "Multi-part question"),
        _arrow(),
        _box("Decompose", "✂️", "#EC4899", "Split into\nsub-questions"),
    )
    content += _row(
        _box("Hop 1\nRetrieve", "🔍", "#3B82F6", "Answer sub-Q1"),
        _arrow("extract entities"),
        _box("Entity\nExtraction", "🏷️", "#8B5CF6", "Find key terms\nfrom results"),
        _arrow("use entity"),
        _box("Hop 2\nRetrieve", "🔍", "#F97316", "Answer sub-Q2\nusing entities"),
    )
    content += _row(
        _arrow("combine all"),
        _box("Synthesize", "🧩", "#EC4899", "Merge both\nhop results"),
        _arrow(),
        _box("LLM", "🤖", "#F97316"),
        _arrow(),
        _box("Answer", "💬", "#10B981"),
    )
    return _wrap(content, "🔗 Multi-Hop RAG Pipeline", "Chains multiple retrievals: Hop1 → extract → Hop2 → synthesize")

def diagram_graph_rag() -> str:
    content = _row(
        _box("Documents", "📄", "#8B5CF6"),
        _arrow("extract entities"),
        _box("Knowledge\nGraph", "🕸️", "#EC4899", "Nodes=entities\nEdges=relations", "120px"),
    )
    content += _row(
        _box("Query", "❓", "#8B5CF6"),
        _arrow("entity link"),
        _box("Graph\nTraversal", "🔀", "#8B5CF6", "Navigate\nrelationships"),
        _arrow(),
        _box("Subgraph\nContext", "📊", "#3B82F6", "Relevant\nnodes+edges"),
        _arrow(),
        _box("LLM", "🤖", "#F97316"),
        _arrow(),
        _box("Answer", "💬", "#10B981"),
    )
    content += _row(
        _badge("Entity: Einstein", "#8B5CF6"),
        _badge("→ born_in: Germany", "#EC4899"),
        _badge("→ published: Relativity", "#3B82F6"),
    )
    return _wrap(content, "🕸️ Graph RAG Pipeline", "Builds a knowledge graph — follows relationships between entities")

def diagram_agentic_rag() -> str:
    content = _row(
        _box("Query", "❓", "#F97316"),
        _arrow(),
        _box("Agent", "🤖", "#F97316", "Plans actions"),
    )
    content += _loop_badge("Agent Loop — runs until confident or max iterations reached")
    content += _row(
        _col(
            _badge("Action 1: Retrieve", "#3B82F6"),
            _badge("Action 2: Search web", "#8B5CF6"),
            _badge("Action 3: Calculate", "#EC4899"),
            _badge("Action 4: Ask user", "#F59E0B"),
        ),
    )
    content += _row(
        _arrow(),
        _decision("Sufficient?", "Return Answer", "Plan next action", "#F97316"),
    )
    return _wrap(content, "🤖 Agentic RAG Pipeline", "Agent plans its own retrieval actions, loops until answer is sufficient")

# ─────────────────────────────────────────────────────
# Main dispatch function
# ─────────────────────────────────────────────────────

DIAGRAM_MAP = {
    "Naive RAG": diagram_naive_rag,
    "Hybrid RAG": diagram_hybrid_rag,
    "Conversational RAG": diagram_conversational_rag,
    "Rerank RAG": diagram_rerank_rag,
    "Contextual RAG": diagram_contextual_rag,
    "Self-Reflective RAG": diagram_self_reflective_rag,
    "Corrective RAG": diagram_corrective_rag,
    "Adaptive RAG": diagram_adaptive_rag,
    "Multi-Hop RAG": diagram_multihop_rag,
    "Graph RAG": diagram_graph_rag,
    "Agentic RAG": diagram_agentic_rag,
}

def get_rag_diagram(rag_name: str) -> str:
    """
    Get the HTML pipeline diagram for a given RAG type.
    rag_name should match keys in DIAGRAM_MAP (without emoji prefix).
    """
    # Strip emoji prefix if present
    clean = rag_name.replace("🔵 ", "").replace("🟣 ", "").replace("🟢 ", "") \
                    .replace("🔶 ", "").replace("🟡 ", "").replace("🔮 ", "") \
                    .replace("✅ ", "").replace("🔀 ", "").replace("🔗 ", "") \
                    .replace("🕸️ ", "").replace("🤖 ", "")
    fn = DIAGRAM_MAP.get(clean)
    if fn:
        return fn()
    return f'<div style="color:#94a3b8;padding:1rem">No diagram for: {rag_name}</div>'

def get_all_rag_names() -> list:
    return list(DIAGRAM_MAP.keys())
