"""
Retrieval service with citation tracking.
Handles semantic search and source attribution.
"""

import logging
from typing import List, Dict, Any

from app.services.rag.vectorstore import vectorstore
from app.services.rag.embeddings import embedding_service
from app.services.rag.config import rag_config

logger = logging.getLogger(__name__)


class RetrieverService:
    """Service for retrieving relevant chunks with citation support."""

    async def retrieve(
        self,
        query: str,
        tenant_id: str,
        top_k: int | None = None,
        document_ids: List[str] | None = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant chunks for a query.

        Args:
            query: User's search query
            tenant_id: User/tenant ID
            top_k: Number of chunks to retrieve
            document_ids: Optional filter by specific documents

        Returns:
            List of chunks with metadata and citations

        Raises:
            RuntimeError: If retrieval fails
        """
        try:
            # Generate query embedding
            query_embedding = await embedding_service.embed_text(query)

            # Perform similarity search
            chunks = await vectorstore.similarity_search(
                tenant_id=tenant_id,
                query_embedding=query_embedding,
                top_k=top_k,
                document_ids=document_ids,
            )

            # Enrich with citation information
            enriched_chunks = await self._add_citations(chunks, tenant_id)

            logger.info(
                f"Retrieved {len(enriched_chunks)} chunks for query: {query[:50]}..."
            )
            return enriched_chunks

        except Exception as e:
            logger.error(f"Retrieval failed: {str(e)}")
            raise RuntimeError(f"Failed to retrieve chunks: {str(e)}") from e

    async def _add_citations(
        self,
        chunks: List[Dict[str, Any]],
        tenant_id: str,
    ) -> List[Dict[str, Any]]:
        """
        Add citation information to chunks.

        Args:
            chunks: Raw chunks from vector search
            tenant_id: User/tenant ID

        Returns:
            Chunks with citation data
        """
        # Get unique document IDs
        doc_ids = list(set(chunk["document_id"] for chunk in chunks))

        # Fetch document metadata
        doc_metadata = {}
        for doc_id in doc_ids:
            doc = await vectorstore.get_document(doc_id, tenant_id)
            if doc:
                doc_metadata[doc_id] = doc

        # Enrich chunks
        enriched = []
        for chunk in chunks:
            doc_id = chunk["document_id"]
            doc = doc_metadata.get(doc_id, {})

            # Extract citation info
            chunk_metadata = chunk.get("metadata", {})
            citation = {
                "source": doc.get("name", "Unknown"),
                "page": chunk_metadata.get("page", chunk_metadata.get("chunk_index", "N/A")),
                "document_id": doc_id,
            }

            # Build enriched chunk
            enriched_chunk = {
                "content": chunk["content"],
                "similarity": chunk.get("similarity", 0.0),
                "citation": citation,
                "metadata": chunk_metadata,
            }

            enriched.append(enriched_chunk)

        return enriched

    async def hybrid_search(
        self,
        query: str,
        tenant_id: str,
        top_k: int | None = None,
        semantic_weight: float = 0.7,
    ) -> List[Dict[str, Any]]:
        """
        Hybrid search combining semantic and keyword-based retrieval.

        Args:
            query: User's search query
            tenant_id: User/tenant ID
            top_k: Number of results
            semantic_weight: Weight for semantic search (0-1)

        Returns:
            Ranked list of chunks
        """
        k = top_k or rag_config.top_k

        # Get semantic results
        semantic_results = await self.retrieve(
            query=query,
            tenant_id=tenant_id,
            top_k=k * 2,  # Get more for reranking
        )

        # Get keyword results (simple implementation)
        keyword_results = await self._keyword_search(
            query=query,
            tenant_id=tenant_id,
            top_k=k * 2,
        )

        # Merge and rerank
        merged = self._merge_results(
            semantic_results,
            keyword_results,
            semantic_weight,
        )

        return merged[:k]

    async def _keyword_search(
        self,
        query: str,
        tenant_id: str,
        top_k: int,
    ) -> List[Dict[str, Any]]:
        """
        Simple keyword-based search.

        This is a basic implementation. For production, consider using
        Postgres full-text search (tsvector) or Elasticsearch.

        Args:
            query: Search query
            tenant_id: User/tenant ID
            top_k: Number of results

        Returns:
            Matching chunks
        """
        # For now, return empty list
        # TODO: Implement full-text search using Postgres tsvector
        logger.warning("Keyword search not yet implemented, falling back to semantic only")
        return []

    def _merge_results(
        self,
        semantic_results: List[Dict[str, Any]],
        keyword_results: List[Dict[str, Any]],
        semantic_weight: float,
    ) -> List[Dict[str, Any]]:
        """
        Merge and rerank results from semantic and keyword search.

        Uses Reciprocal Rank Fusion (RRF) algorithm.

        Args:
            semantic_results: Results from semantic search
            keyword_results: Results from keyword search
            semantic_weight: Weight for semantic results

        Returns:
            Merged and ranked results
        """
        # Build rank maps
        semantic_ranks = {
            chunk["content"]: idx + 1
            for idx, chunk in enumerate(semantic_results)
        }
        keyword_ranks = {
            chunk["content"]: idx + 1
            for idx, chunk in enumerate(keyword_results)
        }

        # Combine unique chunks
        all_chunks = {chunk["content"]: chunk for chunk in semantic_results}
        all_chunks.update({chunk["content"]: chunk for chunk in keyword_results})

        # Calculate RRF scores
        k = 60  # RRF constant
        scored_chunks = []

        for content, chunk in all_chunks.items():
            semantic_rank = semantic_ranks.get(content, 1000)
            keyword_rank = keyword_ranks.get(content, 1000)

            # RRF score
            score = (
                semantic_weight / (k + semantic_rank) +
                (1 - semantic_weight) / (k + keyword_rank)
            )

            chunk["hybrid_score"] = score
            scored_chunks.append(chunk)

        # Sort by score
        scored_chunks.sort(key=lambda x: x["hybrid_score"], reverse=True)
        return scored_chunks

    async def get_context_for_query(
        self,
        query: str,
        tenant_id: str,
        max_chars: int | None = None,
    ) -> tuple[str, List[Dict[str, Any]]]:
        """
        Get formatted context string and source chunks for a query.

        Args:
            query: User query
            tenant_id: User/tenant ID
            max_chars: Maximum context length

        Returns:
            Tuple of (formatted context string, source chunks)
        """
        max_length = max_chars or rag_config.max_context_length

        # Retrieve relevant chunks
        chunks = await self.retrieve(query, tenant_id)

        # Build context string
        context_parts = []
        total_chars = 0
        included_chunks = []

        for chunk in chunks:
            chunk_text = chunk["content"]
            citation = chunk["citation"]

            # Format with citation
            formatted = (
                f"[Source: {citation['source']}, page {citation['page']}]\n"
                f"{chunk_text}\n"
            )

            # Check if adding this chunk exceeds limit
            if total_chars + len(formatted) > max_length:
                break

            context_parts.append(formatted)
            included_chunks.append(chunk)
            total_chars += len(formatted)

        context = "\n---\n\n".join(context_parts)
        return context, included_chunks


# Singleton instance
retriever = RetrieverService()
