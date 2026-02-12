"""
Vector store operations using Supabase pgvector.
Handles storing and retrieving embeddings with multi-tenant support.

SQL Schema:
-----------
Run this in Supabase SQL Editor to set up the required tables:

```sql
-- Enable pgvector extension
create extension if not exists vector;

-- Documents table
create table documents (
    id uuid default gen_random_uuid() primary key,
    tenant_id uuid not null,
    name text not null,
    source text,
    metadata jsonb default '{}',
    created_at timestamptz default now()
);

-- Document chunks with embeddings
create table document_chunks (
    id uuid default gen_random_uuid() primary key,
    document_id uuid references documents(id) on delete cascade,
    tenant_id uuid not null,
    content text not null,
    metadata jsonb default '{}',
    embedding vector(1536),
    created_at timestamptz default now()
);

-- Indexes for performance
create index on document_chunks using ivfflat (embedding vector_cosine_ops) with (lists = 100);
create index on document_chunks (tenant_id);
create index on document_chunks (document_id);
create index on documents (tenant_id);

-- Row Level Security (RLS)
alter table documents enable row level security;
alter table document_chunks enable row level security;

-- RLS policies (users can only access their own data)
create policy "Users can view their own documents"
    on documents for select
    using (auth.uid() = tenant_id);

create policy "Users can insert their own documents"
    on documents for insert
    with check (auth.uid() = tenant_id);

create policy "Users can delete their own documents"
    on documents for delete
    using (auth.uid() = tenant_id);

create policy "Users can view their own chunks"
    on document_chunks for select
    using (auth.uid() = tenant_id);

create policy "Users can insert their own chunks"
    on document_chunks for insert
    with check (auth.uid() = tenant_id);

create policy "Users can delete their own chunks"
    on document_chunks for delete
    using (auth.uid() = tenant_id);
```
"""

import logging
from typing import List, Dict, Any, Tuple
from uuid import UUID, uuid4

from supabase import Client

from app.db.supabase import get_supabase_service
from app.services.rag.config import rag_config

logger = logging.getLogger(__name__)


class VectorStoreService:
    """Service for vector storage and similarity search using Supabase pgvector."""

    def __init__(self):
        """Initialize vector store service."""
        self.client: Client = get_supabase_service()

    async def create_document(
        self,
        tenant_id: str,
        name: str,
        source: str,
        metadata: Dict[str, Any] | None = None,
    ) -> str:
        """
        Create a document record.

        Args:
            tenant_id: User/tenant ID
            name: Document name
            source: Document source (file path, URL, etc.)
            metadata: Additional metadata

        Returns:
            Document UUID

        Raises:
            RuntimeError: If document creation fails
        """
        try:
            document_data = {
                "id": str(uuid4()),
                "tenant_id": tenant_id,
                "name": name,
                "source": source,
                "metadata": metadata or {},
            }

            response = self.client.table("documents").insert(document_data).execute()

            if not response.data:
                raise RuntimeError("Failed to create document")

            doc_id = response.data[0]["id"]
            logger.info(f"Created document {doc_id} for tenant {tenant_id}")
            return doc_id

        except Exception as e:
            logger.error(f"Failed to create document: {str(e)}")
            raise RuntimeError(f"Document creation failed: {str(e)}") from e

    async def store_chunks(
        self,
        document_id: str,
        tenant_id: str,
        chunks: List[Dict[str, Any]],
        embeddings: List[List[float]],
    ) -> List[str]:
        """
        Store document chunks with embeddings.

        Args:
            document_id: Parent document UUID
            tenant_id: User/tenant ID
            chunks: List of chunk dictionaries (content + metadata)
            embeddings: List of embedding vectors

        Returns:
            List of created chunk UUIDs

        Raises:
            ValueError: If chunks and embeddings don't match
            RuntimeError: If storage fails
        """
        if len(chunks) != len(embeddings):
            raise ValueError(
                f"Chunks ({len(chunks)}) and embeddings ({len(embeddings)}) count mismatch"
            )

        try:
            # Prepare chunk records
            chunk_records = []
            for chunk, embedding in zip(chunks, embeddings):
                chunk_record = {
                    "id": str(uuid4()),
                    "document_id": document_id,
                    "tenant_id": tenant_id,
                    "content": chunk["content"],
                    "metadata": chunk.get("metadata", {}),
                    "embedding": embedding,
                }
                chunk_records.append(chunk_record)

            # Batch insert chunks
            response = self.client.table("document_chunks").insert(chunk_records).execute()

            if not response.data:
                raise RuntimeError("Failed to store chunks")

            chunk_ids = [record["id"] for record in response.data]
            logger.info(
                f"Stored {len(chunk_ids)} chunks for document {document_id}"
            )
            return chunk_ids

        except Exception as e:
            logger.error(f"Failed to store chunks: {str(e)}")
            raise RuntimeError(f"Chunk storage failed: {str(e)}") from e

    async def similarity_search(
        self,
        tenant_id: str,
        query_embedding: List[float],
        top_k: int | None = None,
        document_ids: List[str] | None = None,
    ) -> List[Dict[str, Any]]:
        """
        Perform similarity search for relevant chunks.

        Args:
            tenant_id: User/tenant ID (for multi-tenancy)
            query_embedding: Query vector
            top_k: Number of results to return
            document_ids: Optional filter by specific documents

        Returns:
            List of matching chunks with similarity scores

        Raises:
            RuntimeError: If search fails
        """
        k = top_k or rag_config.top_k

        try:
            # Build the RPC call for similarity search
            # Note: This requires a custom Postgres function (see below)
            rpc_params = {
                "query_embedding": query_embedding,
                "match_threshold": rag_config.similarity_threshold,
                "match_count": k,
                "filter_tenant_id": tenant_id,
            }

            if document_ids:
                rpc_params["filter_document_ids"] = document_ids

            # Call the similarity search function
            response = self.client.rpc(
                "match_document_chunks",
                rpc_params,
            ).execute()

            results = response.data or []

            logger.info(
                f"Similarity search for tenant {tenant_id}: {len(results)} results"
            )
            return results

        except Exception as e:
            logger.error(f"Similarity search failed: {str(e)}")
            # Fall back to manual search if RPC not available
            return await self._manual_similarity_search(
                tenant_id,
                query_embedding,
                k,
                document_ids,
            )

    async def _manual_similarity_search(
        self,
        tenant_id: str,
        query_embedding: List[float],
        top_k: int,
        document_ids: List[str] | None = None,
    ) -> List[Dict[str, Any]]:
        """
        Fallback manual similarity search using cosine distance.

        This is less efficient than the RPC method but works without custom functions.
        """
        try:
            # Fetch all chunks for tenant
            query = self.client.table("document_chunks").select("*").eq("tenant_id", tenant_id)

            if document_ids:
                query = query.in_("document_id", document_ids)

            response = query.execute()
            chunks = response.data or []

            # Calculate cosine similarity for each chunk
            import numpy as np

            query_vec = np.array(query_embedding)
            results = []

            for chunk in chunks:
                if chunk.get("embedding"):
                    chunk_vec = np.array(chunk["embedding"])
                    # Cosine similarity
                    similarity = np.dot(query_vec, chunk_vec) / (
                        np.linalg.norm(query_vec) * np.linalg.norm(chunk_vec)
                    )

                    if similarity >= rag_config.similarity_threshold:
                        results.append({
                            **chunk,
                            "similarity": float(similarity),
                        })

            # Sort by similarity and return top_k
            results.sort(key=lambda x: x["similarity"], reverse=True)
            return results[:top_k]

        except Exception as e:
            logger.error(f"Manual similarity search failed: {str(e)}")
            raise RuntimeError(f"Search failed: {str(e)}") from e

    async def delete_document(
        self,
        document_id: str,
        tenant_id: str,
    ) -> bool:
        """
        Delete a document and all its chunks.

        Args:
            document_id: Document UUID
            tenant_id: User/tenant ID (for verification)

        Returns:
            True if deleted successfully

        Raises:
            RuntimeError: If deletion fails
        """
        try:
            # Delete document (chunks cascade via foreign key)
            response = (
                self.client.table("documents")
                .delete()
                .eq("id", document_id)
                .eq("tenant_id", tenant_id)
                .execute()
            )

            if not response.data:
                logger.warning(f"Document {document_id} not found or access denied")
                return False

            logger.info(f"Deleted document {document_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete document: {str(e)}")
            raise RuntimeError(f"Deletion failed: {str(e)}") from e

    async def list_documents(
        self,
        tenant_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        List all documents for a tenant.

        Args:
            tenant_id: User/tenant ID
            limit: Maximum documents to return
            offset: Pagination offset

        Returns:
            Tuple of (documents list, total count)

        Raises:
            RuntimeError: If query fails
        """
        try:
            # Get documents
            response = (
                self.client.table("documents")
                .select("*")
                .eq("tenant_id", tenant_id)
                .order("created_at", desc=True)
                .range(offset, offset + limit - 1)
                .execute()
            )

            documents = response.data or []

            # Get total count
            count_response = (
                self.client.table("documents")
                .select("id", count="exact")
                .eq("tenant_id", tenant_id)
                .execute()
            )

            total = count_response.count or 0

            logger.info(f"Listed {len(documents)} documents for tenant {tenant_id}")
            return documents, total

        except Exception as e:
            logger.error(f"Failed to list documents: {str(e)}")
            raise RuntimeError(f"Document listing failed: {str(e)}") from e

    async def get_document(
        self,
        document_id: str,
        tenant_id: str,
    ) -> Dict[str, Any] | None:
        """
        Get a specific document by ID.

        Args:
            document_id: Document UUID
            tenant_id: User/tenant ID

        Returns:
            Document data or None if not found
        """
        try:
            response = (
                self.client.table("documents")
                .select("*")
                .eq("id", document_id)
                .eq("tenant_id", tenant_id)
                .limit(1)
                .execute()
            )

            return response.data[0] if response.data else None

        except Exception as e:
            logger.error(f"Failed to get document: {str(e)}")
            return None


# Singleton instance
vectorstore = VectorStoreService()


# SQL function for efficient similarity search
# Run this in Supabase SQL Editor:
"""
create or replace function match_document_chunks(
    query_embedding vector(1536),
    match_threshold float,
    match_count int,
    filter_tenant_id uuid,
    filter_document_ids uuid[] default null
)
returns table (
    id uuid,
    document_id uuid,
    tenant_id uuid,
    content text,
    metadata jsonb,
    similarity float
)
language sql stable
as $$
    select
        document_chunks.id,
        document_chunks.document_id,
        document_chunks.tenant_id,
        document_chunks.content,
        document_chunks.metadata,
        1 - (document_chunks.embedding <=> query_embedding) as similarity
    from document_chunks
    where
        document_chunks.tenant_id = filter_tenant_id
        and (filter_document_ids is null or document_chunks.document_id = any(filter_document_ids))
        and 1 - (document_chunks.embedding <=> query_embedding) > match_threshold
    order by similarity desc
    limit match_count;
$$;
"""
