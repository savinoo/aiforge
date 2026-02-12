"""
RAG (Retrieval-Augmented Generation) services.

Public API for document ingestion, chunking, embedding, and RAG chat.
"""

from app.services.rag.config import rag_config, RAGConfig
from app.services.rag.ingestion import ingestion_service, DocumentIngestionService
from app.services.rag.chunking import chunking_service, ChunkingService
from app.services.rag.embeddings import embedding_service, EmbeddingService
from app.services.rag.vectorstore import vectorstore, VectorStoreService
from app.services.rag.retriever import retriever, RetrieverService
from app.services.rag.chat import rag_chat, RAGChatService
from app.services.rag.prompts import (
    build_rag_prompt,
    get_prompt_by_style,
    DEFAULT_SYSTEM_PROMPT,
)

__all__ = [
    # Configuration
    "rag_config",
    "RAGConfig",
    # Services (instances)
    "ingestion_service",
    "chunking_service",
    "embedding_service",
    "vectorstore",
    "retriever",
    "rag_chat",
    # Service classes
    "DocumentIngestionService",
    "ChunkingService",
    "EmbeddingService",
    "VectorStoreService",
    "RetrieverService",
    "RAGChatService",
    # Prompts
    "build_rag_prompt",
    "get_prompt_by_style",
    "DEFAULT_SYSTEM_PROMPT",
]
