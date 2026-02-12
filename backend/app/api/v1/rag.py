"""
RAG API endpoints.
Handles document ingestion, search, and conversational chat with citations.
"""

import logging
from typing import List, Dict, Any
from uuid import UUID

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
    status,
    Depends,
)
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, HttpUrl

from app.core.deps import CurrentUser, DatabaseDep
from app.services.rag import (
    ingestion_service,
    chunking_service,
    embedding_service,
    vectorstore,
    retriever,
    rag_chat,
    rag_config,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rag", tags=["RAG"])


# Request/Response Models
class IngestURLRequest(BaseModel):
    """Request to ingest content from a URL."""
    url: HttpUrl = Field(..., description="URL to ingest")
    name: str | None = Field(None, description="Optional custom name for the document")


class IngestResponse(BaseModel):
    """Response after document ingestion."""
    document_id: str = Field(..., description="UUID of the ingested document")
    name: str = Field(..., description="Document name")
    chunks_created: int = Field(..., description="Number of chunks created")
    message: str = Field(..., description="Success message")


class ChatMessage(BaseModel):
    """Chat message."""
    role: str = Field(..., description="Message role (user/assistant)")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Request for RAG chat."""
    message: str = Field(..., description="User's message", min_length=1)
    conversation_history: List[ChatMessage] | None = Field(
        None,
        description="Previous conversation messages",
    )
    document_ids: List[str] | None = Field(
        None,
        description="Optional filter for specific documents",
    )
    model: str = Field(
        default="gpt-4o-mini",
        description="LLM model to use",
    )
    provider: str = Field(
        default="openai",
        description="LLM provider (openai/anthropic)",
    )
    stream: bool = Field(
        default=True,
        description="Stream the response",
    )
    prompt_style: str = Field(
        default="default",
        description="Prompt style (default/concise/detailed/conversational)",
    )


class SearchRequest(BaseModel):
    """Request for semantic search."""
    query: str = Field(..., description="Search query", min_length=1)
    top_k: int = Field(default=5, description="Number of results", ge=1, le=20)
    document_ids: List[str] | None = Field(
        None,
        description="Optional filter for specific documents",
    )


class SearchResult(BaseModel):
    """Search result with citation."""
    content: str = Field(..., description="Chunk content")
    source: str = Field(..., description="Document name")
    page: str | int = Field(..., description="Page or chunk number")
    similarity: float = Field(..., description="Similarity score")


class DocumentListItem(BaseModel):
    """Document list item."""
    id: str = Field(..., description="Document UUID")
    name: str = Field(..., description="Document name")
    source: str = Field(..., description="Document source")
    created_at: str = Field(..., description="Creation timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Document metadata")


class DocumentListResponse(BaseModel):
    """Response for document list."""
    documents: List[DocumentListItem] = Field(..., description="List of documents")
    total: int = Field(..., description="Total number of documents")
    page: int = Field(..., description="Current page")
    page_size: int = Field(..., description="Items per page")


# Endpoints
@router.post(
    "/ingest",
    status_code=status.HTTP_201_CREATED,
    response_model=IngestResponse,
    summary="Ingest Document",
    description="Upload and ingest a document for RAG",
)
async def ingest_document(
    file: UploadFile = File(..., description="Document file to ingest"),
    current_user: CurrentUser = Depends(),
) -> IngestResponse:
    """
    Ingest a document file.

    Supports: PDF, DOCX, TXT, CSV, Markdown, HTML

    Args:
        file: Uploaded file
        current_user: Authenticated user

    Returns:
        Ingestion result with document ID and chunk count

    Raises:
        HTTPException: If ingestion fails
    """
    tenant_id = current_user["id"]

    try:
        # Validate file type
        filename = file.filename or "unknown"
        mime_type = file.content_type

        # Read file content
        file_content = await file.read()

        # Ingest document
        logger.info(f"Ingesting document {filename} for tenant {tenant_id}")
        documents = await ingestion_service.ingest_file(
            file_content=file_content,
            filename=filename,
            mime_type=mime_type,
        )

        # Chunk documents
        chunks = await chunking_service.chunk_documents(documents)

        # Generate embeddings
        texts = [chunk["content"] for chunk in chunks]
        embeddings = await embedding_service.embed_batch(texts)

        # Create document record
        doc_id = await vectorstore.create_document(
            tenant_id=tenant_id,
            name=filename,
            source=filename,
            metadata={
                "original_filename": filename,
                "mime_type": mime_type,
                "page_count": len(documents),
            },
        )

        # Store chunks with embeddings
        await vectorstore.store_chunks(
            document_id=doc_id,
            tenant_id=tenant_id,
            chunks=chunks,
            embeddings=embeddings,
        )

        logger.info(
            f"Successfully ingested {filename}: {len(chunks)} chunks created"
        )

        return IngestResponse(
            document_id=doc_id,
            name=filename,
            chunks_created=len(chunks),
            message=f"Successfully ingested {filename}",
        )

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Ingestion failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest document: {str(e)}",
        )


@router.post(
    "/ingest-url",
    status_code=status.HTTP_201_CREATED,
    response_model=IngestResponse,
    summary="Ingest URL",
    description="Ingest content from a URL",
)
async def ingest_url(
    request: IngestURLRequest,
    current_user: CurrentUser = Depends(),
) -> IngestResponse:
    """
    Ingest content from a URL.

    Args:
        request: URL ingestion request
        current_user: Authenticated user

    Returns:
        Ingestion result

    Raises:
        HTTPException: If ingestion fails
    """
    tenant_id = current_user["id"]
    url = str(request.url)

    try:
        # Ingest URL
        logger.info(f"Ingesting URL {url} for tenant {tenant_id}")
        documents = await ingestion_service.ingest_url(url)

        # Chunk documents
        chunks = await chunking_service.chunk_documents(documents)

        # Generate embeddings
        texts = [chunk["content"] for chunk in chunks]
        embeddings = await embedding_service.embed_batch(texts)

        # Create document record
        doc_name = request.name or url
        doc_id = await vectorstore.create_document(
            tenant_id=tenant_id,
            name=doc_name,
            source=url,
            metadata={
                "url": url,
                "source_type": "url",
            },
        )

        # Store chunks
        await vectorstore.store_chunks(
            document_id=doc_id,
            tenant_id=tenant_id,
            chunks=chunks,
            embeddings=embeddings,
        )

        logger.info(f"Successfully ingested URL {url}: {len(chunks)} chunks")

        return IngestResponse(
            document_id=doc_id,
            name=doc_name,
            chunks_created=len(chunks),
            message=f"Successfully ingested content from {url}",
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"URL ingestion failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest URL: {str(e)}",
        )


@router.post(
    "/chat",
    summary="RAG Chat",
    description="Chat with RAG context (streaming SSE response)",
)
async def chat(
    request: ChatRequest,
    current_user: CurrentUser = Depends(),
):
    """
    Chat with RAG context.

    Streams the response as Server-Sent Events (SSE).

    Args:
        request: Chat request
        current_user: Authenticated user

    Returns:
        Streaming response with content and citations

    Raises:
        HTTPException: If chat fails
    """
    tenant_id = current_user["id"]

    try:
        # Convert conversation history
        history = None
        if request.conversation_history:
            history = [
                {"role": msg.role, "content": msg.content}
                for msg in request.conversation_history
            ]

        # Start chat
        logger.info(f"Starting RAG chat for tenant {tenant_id}")
        response = await rag_chat.chat(
            message=request.message,
            tenant_id=tenant_id,
            conversation_history=history,
            document_ids=request.document_ids,
            model=request.model,
            provider=request.provider,
            stream=request.stream,
            prompt_style=request.prompt_style,
        )

        # Return streaming response
        if request.stream:
            return StreamingResponse(
                response,
                media_type="text/event-stream",
            )
        else:
            return response

    except Exception as e:
        logger.error(f"Chat failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat failed: {str(e)}",
        )


@router.post(
    "/search",
    response_model=List[SearchResult],
    summary="Semantic Search",
    description="Search for relevant document chunks",
)
async def search(
    request: SearchRequest,
    current_user: CurrentUser = Depends(),
) -> List[SearchResult]:
    """
    Perform semantic search on ingested documents.

    Args:
        request: Search request
        current_user: Authenticated user

    Returns:
        List of matching chunks with citations

    Raises:
        HTTPException: If search fails
    """
    tenant_id = current_user["id"]

    try:
        # Retrieve relevant chunks
        chunks = await retriever.retrieve(
            query=request.query,
            tenant_id=tenant_id,
            top_k=request.top_k,
            document_ids=request.document_ids,
        )

        # Format results
        results = [
            SearchResult(
                content=chunk["content"],
                source=chunk["citation"]["source"],
                page=chunk["citation"]["page"],
                similarity=chunk["similarity"],
            )
            for chunk in chunks
        ]

        return results

    except Exception as e:
        logger.error(f"Search failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}",
        )


@router.get(
    "/documents",
    response_model=DocumentListResponse,
    summary="List Documents",
    description="List all ingested documents for current user",
)
async def list_documents(
    page: int = 1,
    page_size: int = 20,
    current_user: CurrentUser = Depends(),
) -> DocumentListResponse:
    """
    List all documents for the current user.

    Args:
        page: Page number (1-indexed)
        page_size: Items per page
        current_user: Authenticated user

    Returns:
        Paginated list of documents

    Raises:
        HTTPException: If listing fails
    """
    tenant_id = current_user["id"]

    try:
        # Validate pagination
        if page < 1:
            raise ValueError("Page must be >= 1")
        if page_size < 1 or page_size > 100:
            raise ValueError("Page size must be between 1 and 100")

        offset = (page - 1) * page_size

        # Get documents
        documents, total = await vectorstore.list_documents(
            tenant_id=tenant_id,
            limit=page_size,
            offset=offset,
        )

        # Format response
        doc_items = [
            DocumentListItem(
                id=doc["id"],
                name=doc["name"],
                source=doc.get("source", ""),
                created_at=doc.get("created_at", ""),
                metadata=doc.get("metadata", {}),
            )
            for doc in documents
        ]

        return DocumentListResponse(
            documents=doc_items,
            total=total,
            page=page,
            page_size=page_size,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Failed to list documents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list documents: {str(e)}",
        )


@router.delete(
    "/documents/{document_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete Document",
    description="Delete a document and all its chunks",
)
async def delete_document(
    document_id: str,
    current_user: CurrentUser = Depends(),
) -> Dict[str, str]:
    """
    Delete a document and all its associated chunks.

    Args:
        document_id: Document UUID
        current_user: Authenticated user

    Returns:
        Success message

    Raises:
        HTTPException: If deletion fails or document not found
    """
    tenant_id = current_user["id"]

    try:
        # Delete document
        success = await vectorstore.delete_document(
            document_id=document_id,
            tenant_id=tenant_id,
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found or access denied",
            )

        return {"message": f"Document {document_id} deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document: {str(e)}",
        )


@router.get(
    "/config",
    summary="Get RAG Configuration",
    description="Get current RAG system configuration",
)
async def get_config(
    current_user: CurrentUser = Depends(),
) -> Dict[str, Any]:
    """
    Get RAG configuration.

    Args:
        current_user: Authenticated user

    Returns:
        RAG configuration
    """
    return {
        "chunk_size": rag_config.chunk_size,
        "chunk_overlap": rag_config.chunk_overlap,
        "embedding_model": rag_config.embedding_model,
        "top_k": rag_config.top_k,
        "similarity_threshold": rag_config.similarity_threshold,
        "max_file_size_mb": rag_config.max_file_size_mb,
        "supported_extensions": rag_config.supported_extensions,
    }
