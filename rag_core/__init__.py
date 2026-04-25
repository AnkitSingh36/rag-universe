from .naive_rag import NaiveRAG
from .hybrid_rag import HybridRAG
from .conversational_rag import ConversationalRAG
from .rerank_rag import RerankRAG
from .contextual_rag import ContextualRAG
from .self_reflective_rag import SelfReflectiveRAG
from .corrective_rag import CorrectiveRAG
from .adaptive_rag import AdaptiveRAG
from .multihop_rag import MultiHopRAG
from .base import Document, RAGResult
from .utils import get_embedder, check_ollama_running

# All RAG types available in the app
ALL_RAG_TYPES = {
    "🔵 Naive RAG":            NaiveRAG,
    "🟣 Hybrid RAG":           HybridRAG,
    "🟢 Conversational RAG":   ConversationalRAG,
    "🔶 Rerank RAG":           RerankRAG,
    "🟡 Contextual RAG":       ContextualRAG,
    "🔮 Self-Reflective RAG":  SelfReflectiveRAG,
    "✅ Corrective RAG":       CorrectiveRAG,
    "🔀 Adaptive RAG":         AdaptiveRAG,
    "🔗 Multi-Hop RAG":        MultiHopRAG,
}

# Map name → class for descriptions
RAG_META = {
    "🔵 Naive RAG":            {"color": "#3B82F6", "complexity": "⭐ Simple",     "speed": "⚡⚡⚡"},
    "🟣 Hybrid RAG":           {"color": "#8B5CF6", "complexity": "⭐⭐ Medium",    "speed": "⚡⚡"},
    "🟢 Conversational RAG":   {"color": "#10B981", "complexity": "⭐⭐ Medium",    "speed": "⚡⚡"},
    "🔶 Rerank RAG":           {"color": "#F59E0B", "complexity": "⭐⭐ Medium",    "speed": "⚡"},
    "🟡 Contextual RAG":       {"color": "#EAB308", "complexity": "⭐⭐ Medium",    "speed": "⚡⚡"},
    "🔮 Self-Reflective RAG":  {"color": "#6366F1", "complexity": "⭐⭐⭐ Hard",    "speed": "⚡"},
    "✅ Corrective RAG":       {"color": "#10B981", "complexity": "⭐⭐⭐ Hard",    "speed": "⚡"},
    "🔀 Adaptive RAG":         {"color": "#EC4899", "complexity": "⭐⭐⭐ Hard",    "speed": "⚡⚡"},
    "🔗 Multi-Hop RAG":        {"color": "#F97316", "complexity": "⭐⭐⭐ Hard",    "speed": "⚡"},
}

__all__ = [
    "NaiveRAG", "HybridRAG", "ConversationalRAG", "RerankRAG",
    "ContextualRAG", "SelfReflectiveRAG", "CorrectiveRAG",
    "AdaptiveRAG", "MultiHopRAG",
    "Document", "RAGResult",
    "ALL_RAG_TYPES", "RAG_META",
    "get_embedder", "check_ollama_running",
]
