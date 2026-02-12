"""
RAG-specific configuration.
Defines chunking strategies, embedding models, and prompt templates.
"""

from typing import List
from pydantic import BaseModel, Field


class RAGConfig(BaseModel):
    """RAG system configuration."""

    # Chunking configuration
    chunk_size: int = Field(
        default=1000,
        description="Maximum size of each text chunk in characters",
        ge=100,
        le=4000,
    )
    chunk_overlap: int = Field(
        default=200,
        description="Overlap between consecutive chunks in characters",
        ge=0,
        le=1000,
    )

    # Embedding configuration
    embedding_model: str = Field(
        default="text-embedding-3-small",
        description="OpenAI embedding model to use",
    )
    embedding_dimensions: int = Field(
        default=1536,
        description="Dimensions of the embedding vector",
    )
    embedding_batch_size: int = Field(
        default=100,
        description="Number of texts to embed in a single batch",
    )

    # Retrieval configuration
    top_k: int = Field(
        default=5,
        description="Number of chunks to retrieve for each query",
        ge=1,
        le=20,
    )
    similarity_threshold: float = Field(
        default=0.7,
        description="Minimum cosine similarity for relevant chunks",
        ge=0.0,
        le=1.0,
    )

    # Chat configuration
    max_context_length: int = Field(
        default=4000,
        description="Maximum context length in characters for LLM",
    )
    stream_chunk_size: int = Field(
        default=50,
        description="Characters per chunk when streaming responses",
    )

    # Supported file types
    supported_file_types: List[str] = Field(
        default=[
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # .docx
            "text/plain",
            "text/csv",
            "text/markdown",
            "text/html",
        ],
        description="MIME types of supported document formats",
    )

    supported_extensions: List[str] = Field(
        default=[".pdf", ".docx", ".txt", ".csv", ".md", ".html"],
        description="File extensions that can be ingested",
    )

    # File size limits
    max_file_size_mb: int = Field(
        default=10,
        description="Maximum file size in MB",
    )

    # URL ingestion
    url_timeout_seconds: int = Field(
        default=30,
        description="Timeout for URL requests",
    )


# Global RAG configuration instance
rag_config = RAGConfig()
