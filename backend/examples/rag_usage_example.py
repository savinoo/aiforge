"""
RAG Service Usage Example
Demonstrates how to use the RAG service programmatically.
"""

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


async def example_document_ingestion():
    """Example: Ingest a document and store it."""
    print("\n" + "=" * 60)
    print("EXAMPLE 1: Document Ingestion")
    print("=" * 60 + "\n")

    # Sample document content
    document_text = """
    AIForge Product Documentation

    ## Overview
    AIForge is a production-ready Python AI SaaS boilerplate that includes:
    - RAG (Retrieval-Augmented Generation)
    - LangGraph agents for complex workflows
    - WhatsApp Business API integration
    - Multi-tenant architecture with Supabase
    - Payment processing with LemonSqueezy

    ## Pricing
    Our pricing is simple and transparent:
    - Starter: $49/month (100k tokens, 10 team members)
    - Pro: $149/month (500k tokens, unlimited team)
    - Enterprise: Custom pricing with dedicated support

    ## Features
    The RAG system supports:
    - PDF, DOCX, TXT, CSV, Markdown, and HTML files
    - URL ingestion for web content
    - Automatic citation tracking
    - Multi-language support
    - Streaming responses
    """

    tenant_id = "550e8400-e29b-41d4-a716-446655440000"  # Example UUID

    # Step 1: Chunk the document
    print("📄 Step 1: Chunking document...")
    chunks = await chunking_service.chunk_text(
        text=document_text,
        metadata={"source": "aiforge_docs.md", "version": "1.0"},
    )
    print(f"   ✓ Created {len(chunks)} chunks")

    # Step 2: Generate embeddings
    print("\n🔢 Step 2: Generating embeddings...")
    texts = [chunk["content"] for chunk in chunks]
    embeddings = await embedding_service.embed_batch(texts)
    print(f"   ✓ Generated {len(embeddings)} embeddings")

    # Step 3: Store in vectorstore (requires DB connection)
    print("\n💾 Step 3: Storing in vectorstore...")
    print("   ⚠️  Skipped (requires Supabase connection)")
    print("   Code would be:")
    print("   doc_id = await vectorstore.create_document(")
    print("       tenant_id=tenant_id,")
    print("       name='aiforge_docs.md',")
    print("       source='documentation',")
    print("   )")
    print("   await vectorstore.store_chunks(")
    print("       document_id=doc_id,")
    print("       tenant_id=tenant_id,")
    print("       chunks=chunks,")
    print("       embeddings=embeddings,")
    print("   )")

    return chunks, embeddings


async def example_semantic_search():
    """Example: Perform semantic search."""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Semantic Search")
    print("=" * 60 + "\n")

    tenant_id = "550e8400-e29b-41d4-a716-446655440000"
    query = "What are the pricing tiers?"

    print(f"🔍 Query: '{query}'")
    print("\n💾 Searching vectorstore...")
    print("   ⚠️  Skipped (requires Supabase connection)")
    print("   Code would be:")
    print("   results = await retriever.retrieve(")
    print(f"       query='{query}',")
    print(f"       tenant_id='{tenant_id}',")
    print("       top_k=3,")
    print("   )")
    print("\n   Expected results:")
    print("   [")
    print("     {")
    print("       'content': 'Our pricing is simple: Starter $49/month...',")
    print("       'citation': {'source': 'aiforge_docs.md', 'page': 2},")
    print("       'similarity': 0.92")
    print("     },")
    print("     ...")
    print("   ]")


async def example_rag_chat():
    """Example: RAG-powered chat."""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: RAG Chat")
    print("=" * 60 + "\n")

    tenant_id = "550e8400-e29b-41d4-a716-446655440000"
    message = "What features does AIForge include?"

    print(f"💬 User: {message}")
    print("\n🤖 Assistant (streaming):")
    print("   ⚠️  Skipped (requires Supabase + OpenAI)")
    print("   Code would be:")
    print("   response_stream = await rag_chat.chat(")
    print(f"       message='{message}',")
    print(f"       tenant_id='{tenant_id}',")
    print("       model='gpt-4o-mini',")
    print("       provider='openai',")
    print("       stream=True,")
    print("   )")
    print("\n   async for chunk in response_stream:")
    print("       data = json.loads(chunk.replace('data: ', ''))")
    print("       if data['type'] == 'content':")
    print("           print(data['content'], end='')")
    print("\n   Expected response:")
    print("   'According to the documentation, AIForge includes:")
    print("   - RAG (Retrieval-Augmented Generation)")
    print("   - LangGraph agents for complex workflows")
    print("   - WhatsApp Business API integration")
    print("   [Source: aiforge_docs.md, page 1]'")


async def example_url_ingestion():
    """Example: Ingest content from a URL."""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: URL Ingestion")
    print("=" * 60 + "\n")

    url = "https://example.com/blog/ai-trends-2024"

    print(f"🌐 Ingesting URL: {url}")
    print("\n   ⚠️  Skipped (would make HTTP request)")
    print("   Code would be:")
    print("   documents = await ingestion_service.ingest_url(url)")
    print("   chunks = await chunking_service.chunk_documents(documents)")
    print("   embeddings = await embedding_service.embed_batch(texts)")
    print("   # ... then store in vectorstore")


async def example_conversation_history():
    """Example: Multi-turn conversation with history."""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Conversation with History")
    print("=" * 60 + "\n")

    tenant_id = "550e8400-e29b-41d4-a716-446655440000"

    # Previous conversation
    history = [
        {"role": "user", "content": "What is AIForge?"},
        {"role": "assistant", "content": "AIForge is a Python AI SaaS boilerplate..."},
        {"role": "user", "content": "What pricing plans are available?"},
        {"role": "assistant", "content": "We offer three plans: Starter ($49), Pro ($149)..."},
    ]

    # New message
    message = "Which plan would you recommend for a small team?"

    print("📜 Conversation history:")
    for msg in history:
        role_emoji = "👤" if msg["role"] == "user" else "🤖"
        print(f"   {role_emoji} {msg['role']}: {msg['content'][:50]}...")

    print(f"\n💬 New message: {message}")
    print("\n   ⚠️  Skipped (requires DB + API)")
    print("   Code would be:")
    print("   response = await rag_chat.chat(")
    print(f"       message='{message}',")
    print(f"       tenant_id='{tenant_id}',")
    print("       conversation_history=history,")
    print("       model='gpt-4o-mini',")
    print("       stream=True,")
    print("   )")


async def example_custom_prompt_style():
    """Example: Using different prompt styles."""
    print("\n" + "=" * 60)
    print("EXAMPLE 6: Custom Prompt Styles")
    print("=" * 60 + "\n")

    from app.services.rag.prompts import get_prompt_by_style

    styles = {
        "default": "Balanced, cite sources, acknowledge limitations",
        "concise": "Brief answers, always cited",
        "detailed": "Thorough explanations with examples",
        "conversational": "Friendly, approachable tone",
    }

    print("Available prompt styles:\n")
    for style, description in styles.items():
        print(f"  • {style:15} - {description}")
        prompt = get_prompt_by_style(style)
        preview = prompt[:100].replace("\n", " ")
        print(f"    Preview: {preview}...\n")

    print("💡 Usage in chat:")
    print("   await rag_chat.chat(")
    print("       message='Explain RAG',")
    print("       prompt_style='conversational',  # Choose your style")
    print("       ...,")
    print("   )")


async def example_document_management():
    """Example: Manage documents (list, delete)."""
    print("\n" + "=" * 60)
    print("EXAMPLE 7: Document Management")
    print("=" * 60 + "\n")

    tenant_id = "550e8400-e29b-41d4-a716-446655440000"

    print("📚 List all documents:")
    print("   Code:")
    print("   documents, total = await vectorstore.list_documents(")
    print(f"       tenant_id='{tenant_id}',")
    print("       limit=20,")
    print("       offset=0,")
    print("   )")
    print("\n   Expected result:")
    print("   documents = [")
    print("     {'id': 'uuid1', 'name': 'doc1.pdf', 'created_at': '...'},")
    print("     {'id': 'uuid2', 'name': 'doc2.txt', 'created_at': '...'},")
    print("   ]")
    print("   total = 2")

    print("\n🗑️  Delete a document:")
    print("   Code:")
    print("   success = await vectorstore.delete_document(")
    print("       document_id='uuid1',")
    print(f"       tenant_id='{tenant_id}',")
    print("   )")
    print("   # Cascades to delete all chunks automatically")


def example_configuration():
    """Example: Configure RAG settings."""
    print("\n" + "=" * 60)
    print("EXAMPLE 8: Configuration")
    print("=" * 60 + "\n")

    from app.services.rag.config import rag_config, RAGConfig

    print("📋 Current configuration:")
    print(f"   Chunk size:          {rag_config.chunk_size} characters")
    print(f"   Chunk overlap:       {rag_config.chunk_overlap} characters")
    print(f"   Embedding model:     {rag_config.embedding_model}")
    print(f"   Top K results:       {rag_config.top_k}")
    print(f"   Similarity threshold: {rag_config.similarity_threshold}")
    print(f"   Max file size:       {rag_config.max_file_size_mb} MB")

    print("\n⚙️  Customize configuration:")
    print("   # Edit app/services/rag/config.py")
    print("   rag_config = RAGConfig(")
    print("       chunk_size=1500,      # Larger chunks")
    print("       top_k=10,             # More results")
    print("       similarity_threshold=0.8,  # Stricter matching")
    print("   )")

    print("\n📁 Supported file types:")
    for ext in rag_config.supported_extensions:
        print(f"   • {ext}")


async def main():
    """Run all examples."""
    print("\n" + "🚀" * 30)
    print("RAG SERVICE USAGE EXAMPLES")
    print("🚀" * 30)

    # Run examples
    await example_document_ingestion()
    await example_semantic_search()
    await example_rag_chat()
    await example_url_ingestion()
    await example_conversation_history()
    await example_custom_prompt_style()
    await example_document_management()
    example_configuration()

    print("\n" + "=" * 60)
    print("✅ All examples completed!")
    print("=" * 60)
    print("\n💡 Tips:")
    print("   • See tests/test_rag_integration.py for unit tests")
    print("   • See app/services/rag/README.md for full documentation")
    print("   • Run migrations/001_setup_rag.sql in Supabase first")
    print("   • Set OPENAI_API_KEY and SUPABASE_URL in .env")
    print("\n📚 Next steps:")
    print("   1. Set up Supabase database (run migration)")
    print("   2. Configure environment variables")
    print("   3. Start the FastAPI server: uvicorn app.main:app --reload")
    print("   4. Test endpoints with curl or Postman")
    print("   5. Integrate with your frontend\n")


if __name__ == "__main__":
    asyncio.run(main())
