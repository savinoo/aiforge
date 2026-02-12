"""
Integration tests for RAG service.
Demonstrates complete workflow from ingestion to chat.
"""

import pytest
import asyncio
from pathlib import Path

from app.services.rag import (
    ingestion_service,
    chunking_service,
    embedding_service,
    vectorstore,
    retriever,
    rag_chat,
)


@pytest.fixture
def sample_text():
    """Sample text for testing."""
    return """
    AIForge is a Python AI SaaS boilerplate designed for developers building
    AI-powered products. It includes features like RAG (Retrieval-Augmented
    Generation), LangGraph agents, and WhatsApp integration.

    The RAG system supports multiple document formats including PDF, DOCX, TXT,
    CSV, Markdown, and HTML. It uses OpenAI embeddings and Supabase pgvector
    for efficient semantic search.

    Pricing starts at $49/month for the starter plan, which includes 100,000
    tokens per month and up to 10 team members. Enterprise plans are available
    with custom pricing.
    """


@pytest.fixture
def tenant_id():
    """Test tenant ID."""
    return "550e8400-e29b-41d4-a716-446655440000"


@pytest.mark.asyncio
async def test_complete_rag_workflow(sample_text, tenant_id):
    """
    Test the complete RAG workflow:
    1. Create chunks
    2. Generate embeddings
    3. Store in vectorstore
    4. Search for relevant content
    5. Generate RAG response
    """
    # Step 1: Create chunks
    chunks = await chunking_service.chunk_text(
        text=sample_text,
        metadata={"source": "test_document.txt"},
    )

    assert len(chunks) > 0
    assert all("content" in chunk for chunk in chunks)
    print(f"✓ Created {len(chunks)} chunks")

    # Step 2: Generate embeddings
    texts = [chunk["content"] for chunk in chunks]
    embeddings = await embedding_service.embed_batch(texts)

    assert len(embeddings) == len(chunks)
    assert all(len(emb) == 1536 for emb in embeddings)
    print(f"✓ Generated {len(embeddings)} embeddings")

    # Step 3: Store in vectorstore (mock - would need DB connection)
    # In real test, you'd use:
    # doc_id = await vectorstore.create_document(...)
    # await vectorstore.store_chunks(...)
    print("✓ Would store in vectorstore (skipped in unit test)")

    # Step 4: Test similarity search (mock)
    # In real test:
    # results = await retriever.retrieve(query="pricing", tenant_id=tenant_id)
    # assert len(results) > 0
    print("✓ Would perform similarity search (skipped in unit test)")

    # Step 5: Test chat (mock)
    # In real test:
    # response = await rag_chat.chat(message="What is the pricing?", ...)
    print("✓ Would generate chat response (skipped in unit test)")


@pytest.mark.asyncio
async def test_chunking_service(sample_text):
    """Test text chunking."""
    chunks = await chunking_service.chunk_text(
        text=sample_text,
        metadata={"test": "value"},
    )

    # Verify chunks
    assert len(chunks) > 0
    for chunk in chunks:
        assert "content" in chunk
        assert "metadata" in chunk
        assert chunk["metadata"]["test"] == "value"
        assert "chunk_index" in chunk["metadata"]

    print(f"✓ Chunking: {len(chunks)} chunks created")


@pytest.mark.asyncio
async def test_embedding_service():
    """Test embedding generation."""
    text = "This is a test sentence for embedding."

    # Single embedding
    embedding = await embedding_service.embed_text(text)
    assert len(embedding) == 1536
    assert all(isinstance(x, float) for x in embedding)

    # Batch embeddings
    texts = [
        "First sentence.",
        "Second sentence.",
        "Third sentence.",
    ]
    embeddings = await embedding_service.embed_batch(texts)
    assert len(embeddings) == 3
    assert all(len(emb) == 1536 for emb in embeddings)

    # Test caching
    cache_size_before = embedding_service.get_cache_size()
    await embedding_service.embed_text(text)  # Should hit cache
    cache_size_after = embedding_service.get_cache_size()
    assert cache_size_after == cache_size_before  # No new cache entry

    print("✓ Embedding: Single and batch generation working")


@pytest.mark.asyncio
async def test_ingestion_text_file():
    """Test text file ingestion."""
    content = b"This is a test text file.\nWith multiple lines.\nFor testing."
    filename = "test.txt"

    documents = await ingestion_service.ingest_file(
        file_content=content,
        filename=filename,
    )

    assert len(documents) > 0
    assert documents[0].metadata["source"] == filename
    assert "test text file" in documents[0].page_content.lower()

    print(f"✓ Ingestion: Text file processed into {len(documents)} document(s)")


@pytest.mark.asyncio
async def test_chunk_size_validation():
    """Test chunk size configuration."""
    # Test with custom chunk size
    service = chunking_service.__class__(chunk_size=100, chunk_overlap=20)

    text = "A" * 500  # 500 characters
    chunks = await service.chunk_text(text)

    # Should create multiple chunks
    assert len(chunks) > 1

    # Each chunk should be roughly the configured size
    for chunk in chunks:
        assert len(chunk["content"]) <= 120  # Allow for overlap

    print(f"✓ Chunking: Custom size working ({len(chunks)} chunks from 500 chars)")


def test_prompt_building():
    """Test prompt building with context."""
    from app.services.rag.prompts import build_rag_prompt

    query = "What is the pricing?"
    context_chunks = [
        {
            "content": "Pricing starts at $49/month.",
            "source": "pricing.pdf",
            "page": 1,
        },
        {
            "content": "Enterprise plans available.",
            "source": "pricing.pdf",
            "page": 2,
        },
    ]

    prompt = build_rag_prompt(query, context_chunks)

    # Verify prompt contains key elements
    assert "pricing" in prompt.lower()
    assert "$49/month" in prompt
    assert "pricing.pdf" in prompt
    assert "cite" in prompt.lower()  # Should mention citations

    print("✓ Prompts: Context and citations included correctly")


def test_config_validation():
    """Test RAG configuration."""
    from app.services.rag.config import rag_config

    # Verify default config
    assert rag_config.chunk_size > 0
    assert rag_config.chunk_overlap < rag_config.chunk_size
    assert rag_config.embedding_model == "text-embedding-3-small"
    assert rag_config.top_k > 0

    # Verify supported file types
    assert ".pdf" in rag_config.supported_extensions
    assert ".txt" in rag_config.supported_extensions

    print("✓ Config: All settings validated")


def test_prompt_styles():
    """Test different prompt styles."""
    from app.services.rag.prompts import get_prompt_by_style

    styles = ["default", "concise", "detailed", "conversational"]

    for style in styles:
        prompt = get_prompt_by_style(style)
        assert len(prompt) > 0
        assert "cite" in prompt.lower() or "source" in prompt.lower()

    # Test invalid style defaults to "default"
    prompt = get_prompt_by_style("invalid_style")
    assert len(prompt) > 0

    print("✓ Prompts: All styles available")


if __name__ == "__main__":
    """Run tests directly."""
    print("Running RAG Integration Tests\n" + "=" * 50 + "\n")

    # Run sync tests
    test_prompt_building()
    test_config_validation()
    test_prompt_styles()

    # Run async tests
    async def run_async_tests():
        sample = """
        AIForge is a Python AI SaaS boilerplate designed for developers building
        AI-powered products. It includes features like RAG (Retrieval-Augmented
        Generation), LangGraph agents, and WhatsApp integration.
        """
        tenant = "550e8400-e29b-41d4-a716-446655440000"

        await test_chunking_service(sample)
        await test_embedding_service()
        await test_ingestion_text_file()
        await test_chunk_size_validation()
        await test_complete_rag_workflow(sample, tenant)

    asyncio.run(run_async_tests())

    print("\n" + "=" * 50)
    print("✅ All tests passed!")
