"""
Text chunking service.
Splits documents into smaller chunks for embedding and retrieval.
"""

import logging
from typing import List, Dict, Any

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from app.services.rag.config import rag_config

logger = logging.getLogger(__name__)


class ChunkingService:
    """Service for splitting documents into chunks for embedding."""

    def __init__(
        self,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
    ):
        """
        Initialize chunking service.

        Args:
            chunk_size: Size of each chunk (defaults to config)
            chunk_overlap: Overlap between chunks (defaults to config)
        """
        self.chunk_size = chunk_size or rag_config.chunk_size
        self.chunk_overlap = chunk_overlap or rag_config.chunk_overlap

        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=[
                "\n\n",  # Paragraph breaks
                "\n",    # Line breaks
                ". ",    # Sentences
                " ",     # Words
                "",      # Characters
            ],
        )

    async def chunk_documents(
        self,
        documents: List[Document],
    ) -> List[Dict[str, Any]]:
        """
        Split documents into chunks with metadata preservation.

        Args:
            documents: List of Document objects to chunk

        Returns:
            List of chunk dictionaries with content and metadata
        """
        all_chunks = []

        for doc_idx, document in enumerate(documents):
            # Split document into chunks
            chunks = self.text_splitter.split_text(document.page_content)

            # Create chunk objects with metadata
            for chunk_idx, chunk_text in enumerate(chunks):
                chunk_metadata = {
                    **document.metadata,  # Preserve original metadata
                    "chunk_index": chunk_idx,
                    "total_chunks": len(chunks),
                    "doc_index": doc_idx,
                    "chunk_size": len(chunk_text),
                }

                chunk_dict = {
                    "content": chunk_text,
                    "metadata": chunk_metadata,
                }

                all_chunks.append(chunk_dict)

        logger.info(
            f"Chunked {len(documents)} documents into {len(all_chunks)} chunks"
        )
        return all_chunks

    async def chunk_text(
        self,
        text: str,
        metadata: Dict[str, Any] | None = None,
    ) -> List[Dict[str, Any]]:
        """
        Chunk a single text string.

        Args:
            text: Text to chunk
            metadata: Optional metadata to attach to chunks

        Returns:
            List of chunk dictionaries
        """
        chunks = self.text_splitter.split_text(text)
        base_metadata = metadata or {}

        chunk_list = []
        for idx, chunk_text in enumerate(chunks):
            chunk_metadata = {
                **base_metadata,
                "chunk_index": idx,
                "total_chunks": len(chunks),
                "chunk_size": len(chunk_text),
            }

            chunk_list.append({
                "content": chunk_text,
                "metadata": chunk_metadata,
            })

        return chunk_list

    def get_optimal_chunk_size(self, text: str) -> int:
        """
        Calculate optimal chunk size based on text characteristics.

        This is a heuristic that can be expanded for different document types.

        Args:
            text: Text to analyze

        Returns:
            Recommended chunk size
        """
        text_length = len(text)

        # For very short texts, use smaller chunks
        if text_length < 1000:
            return 500

        # For medium texts, use default
        if text_length < 10000:
            return self.chunk_size

        # For long documents, use larger chunks
        return min(self.chunk_size * 2, 2000)

    def preview_chunks(
        self,
        text: str,
        num_chunks: int = 3,
    ) -> List[str]:
        """
        Preview how text will be chunked (useful for debugging).

        Args:
            text: Text to chunk
            num_chunks: Number of chunks to preview

        Returns:
            List of preview chunks
        """
        chunks = self.text_splitter.split_text(text)
        return chunks[:num_chunks]


# Singleton instance
chunking_service = ChunkingService()
