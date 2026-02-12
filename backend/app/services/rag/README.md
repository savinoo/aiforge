# RAG Service Documentation

## Overview

The RAG (Retrieval-Augmented Generation) service is the core differentiator of AIForge. It provides production-quality document ingestion, semantic search, and conversational chat with automatic citation tracking.

## Architecture

```
rag/
├── config.py         # Configuration (chunk size, models, etc.)
├── prompts.py        # Prompt templates with citation support
├── ingestion.py      # Document loading (PDF, DOCX, TXT, CSV, MD, HTML, URLs)
├── chunking.py       # Text splitting with metadata preservation
├── embeddings.py     # OpenAI embeddings with caching
├── vectorstore.py    # Supabase pgvector operations
├── retriever.py      # Similarity search with citations
└── chat.py           # RAG chat with streaming (OpenAI & Anthropic)
```

## Setup

### 1. Database Setup

Run this SQL in your Supabase SQL Editor:

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

-- Row Level Security
alter table documents enable row level security;
alter table document_chunks enable row level security;

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

### 2. Similarity Search Function

This optimized function enables fast vector search:

```sql
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
```

### 3. Environment Variables

Add to your `.env`:

```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...  # Optional, for Claude models
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJ...
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

## API Endpoints

### POST /api/v1/rag/ingest

Upload and ingest a document.

**Request:**
- Multipart file upload
- Supported formats: PDF, DOCX, TXT, CSV, MD, HTML
- Max file size: 10MB (configurable)

**Response:**
```json
{
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "myfile.pdf",
  "chunks_created": 42,
  "message": "Successfully ingested myfile.pdf"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/rag/ingest \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@document.pdf"
```

### POST /api/v1/rag/ingest-url

Ingest content from a URL.

**Request:**
```json
{
  "url": "https://example.com/article",
  "name": "Example Article"  // optional
}
```

### POST /api/v1/rag/chat

Chat with RAG context (streaming).

**Request:**
```json
{
  "message": "What does the document say about pricing?",
  "conversation_history": [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi! How can I help?"}
  ],
  "document_ids": ["uuid1", "uuid2"],  // optional filter
  "model": "gpt-4o-mini",
  "provider": "openai",  // or "anthropic"
  "stream": true,
  "prompt_style": "default"  // default/concise/detailed/conversational
}
```

**Response (SSE stream):**
```
data: {"type": "sources", "sources": [{"source": "doc.pdf", "page": 5, "similarity": 0.89}]}

data: {"type": "content", "content": "According to "}

data: {"type": "content", "content": "the document"}

data: {"type": "done"}
```

### POST /api/v1/rag/search

Semantic search without chat.

**Request:**
```json
{
  "query": "pricing information",
  "top_k": 5,
  "document_ids": ["uuid1"]  // optional
}
```

**Response:**
```json
[
  {
    "content": "The pricing starts at $49/month...",
    "source": "pricing.pdf",
    "page": 3,
    "similarity": 0.92
  }
]
```

### GET /api/v1/rag/documents

List all documents for current user.

**Query params:**
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)

**Response:**
```json
{
  "documents": [
    {
      "id": "uuid",
      "name": "document.pdf",
      "source": "document.pdf",
      "created_at": "2024-01-15T10:30:00Z",
      "metadata": {"page_count": 10}
    }
  ],
  "total": 42,
  "page": 1,
  "page_size": 20
}
```

### DELETE /api/v1/rag/documents/{document_id}

Delete a document and all its chunks.

**Response:**
```json
{
  "message": "Document {document_id} deleted successfully"
}
```

### GET /api/v1/rag/config

Get current RAG configuration.

## Usage Examples

### Python Client

```python
import httpx

BASE_URL = "http://localhost:8000/api/v1/rag"
TOKEN = "your_jwt_token"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

# Upload document
with open("document.pdf", "rb") as f:
    response = httpx.post(
        f"{BASE_URL}/ingest",
        files={"file": f},
        headers=HEADERS,
    )
    doc_id = response.json()["document_id"]

# Chat with streaming
with httpx.stream(
    "POST",
    f"{BASE_URL}/chat",
    json={
        "message": "Summarize the key points",
        "stream": True,
    },
    headers=HEADERS,
) as response:
    for line in response.iter_lines():
        if line.startswith("data: "):
            data = json.loads(line[6:])
            if data["type"] == "content":
                print(data["content"], end="")
```

### JavaScript/TypeScript

```typescript
// Upload document
const formData = new FormData();
formData.append('file', file);

const uploadResponse = await fetch('/api/v1/rag/ingest', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` },
  body: formData,
});

const { document_id } = await uploadResponse.json();

// Chat with streaming
const response = await fetch('/api/v1/rag/chat', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    message: 'What are the main topics?',
    stream: true,
  }),
});

const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;

  const text = decoder.decode(value);
  const lines = text.split('\n');

  for (const line of lines) {
    if (line.startsWith('data: ')) {
      const data = JSON.parse(line.slice(6));
      if (data.type === 'content') {
        console.log(data.content);
      }
    }
  }
}
```

## Configuration

Edit `config.py` to customize:

```python
rag_config = RAGConfig(
    chunk_size=1000,          # Characters per chunk
    chunk_overlap=200,        # Overlap between chunks
    embedding_model="text-embedding-3-small",
    top_k=5,                  # Results per query
    similarity_threshold=0.7, # Minimum similarity
    max_file_size_mb=10,      # Max upload size
)
```

## Prompt Styles

Choose from 4 pre-configured styles:

- **default**: Balanced, cite sources, acknowledge limitations
- **concise**: Brief answers, always cited
- **detailed**: Thorough explanations with examples
- **conversational**: Friendly, approachable tone

Or provide custom instructions:

```json
{
  "message": "Explain this topic",
  "custom_instructions": "Answer in Portuguese. Focus on practical examples."
}
```

## Multi-tenancy

All operations are automatically scoped by `tenant_id` (user ID):
- Users can only see/search their own documents
- Row Level Security enforced at database level
- No manual filtering needed in application code

## Performance Tips

1. **Batch uploads**: Ingest multiple documents before chatting
2. **Document filters**: Use `document_ids` to limit search scope
3. **Embedding cache**: Repeated queries are cached automatically
4. **Chunk size**: Smaller chunks = more precise but more API calls
5. **Top_k**: Start with 5, increase if answers lack context

## Monitoring

Key metrics to track:
- Ingestion time per document
- Embedding generation time
- Search latency (should be <200ms)
- LLM response time
- Cache hit rate

## Troubleshooting

### "Failed to create document"
- Check Supabase connection
- Verify user is authenticated
- Confirm tables and RLS policies exist

### "Similarity search failed"
- Ensure `match_document_chunks` function is created
- Check pgvector extension is enabled
- Verify index is created

### "Embedding generation failed"
- Validate OpenAI API key
- Check API quota/limits
- Ensure text isn't too long (8k tokens max)

### Slow performance
- Add database indexes if missing
- Increase pgvector IVFFlat lists for large datasets
- Use connection pooling for Supabase

## Roadmap

Future enhancements:
- [ ] Multi-modal support (images, tables)
- [ ] Advanced chunking strategies (semantic, hierarchical)
- [ ] Hybrid search (semantic + keyword)
- [ ] Citation confidence scores
- [ ] Document versioning
- [ ] Collaborative filtering for relevance
- [ ] Custom embedding models (local, fine-tuned)
- [ ] Real-time ingestion via webhooks

## License

Part of AIForge - Production-ready AI SaaS boilerplate.
