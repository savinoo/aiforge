# RAG Quick Start Guide

Get your RAG system running in 5 minutes.

## Prerequisites

- Python 3.12+
- Supabase account (free tier works)
- OpenAI API key

## Step 1: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

## Step 2: Set Up Supabase

### 2.1 Run Migration

1. Go to your [Supabase Dashboard](https://app.supabase.com)
2. Navigate to **SQL Editor**
3. Copy the contents of `migrations/001_setup_rag.sql`
4. Paste and **Run** the SQL

This creates:
- `documents` table
- `document_chunks` table with pgvector
- Indexes for performance
- Row Level Security policies
- Helper functions

### 2.2 Verify Setup

Run this query to verify:

```sql
-- Should return both tables
SELECT table_name
FROM information_schema.tables
WHERE table_name IN ('documents', 'document_chunks');

-- Should return 'vector'
SELECT extname FROM pg_extension WHERE extname = 'vector';
```

## Step 3: Configure Environment

Create `.env` in the `backend/` directory:

```bash
# Application
SECRET_KEY=your-secret-key-min-32-chars
ENVIRONMENT=development

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_JWT_SECRET=your-jwt-secret

# OpenAI
OPENAI_API_KEY=sk-...

# Anthropic (optional)
ANTHROPIC_API_KEY=sk-ant-...

# Other required vars (use placeholder values for now)
LEMONSQUEEZY_API_KEY=placeholder
LEMONSQUEEZY_STORE_ID=placeholder
LEMONSQUEEZY_WEBHOOK_SECRET=placeholder
WHATSAPP_PHONE_NUMBER_ID=placeholder
WHATSAPP_ACCESS_TOKEN=placeholder
WHATSAPP_VERIFY_TOKEN=placeholder
WHATSAPP_BUSINESS_ACCOUNT_ID=placeholder
```

**Find your Supabase keys:**
1. Supabase Dashboard → Settings → API
2. Copy `URL`, `anon key`, and `service_role key`
3. For JWT secret: Settings → API → JWT Settings → JWT Secret

## Step 4: Start the Server

```bash
uvicorn app.main:app --reload --port 8000
```

Server will start at: http://localhost:8000

Check health: http://localhost:8000/health

## Step 5: Test the RAG System

### 5.1 Create a User

```bash
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123",
    "full_name": "Test User"
  }'
```

Save the `access_token` from the response.

### 5.2 Upload a Document

Create a test file `test.txt`:
```
AIForge is a Python AI SaaS boilerplate.
It includes RAG, LangGraph agents, and WhatsApp integration.
Pricing starts at $49/month for the starter plan.
```

Upload it:
```bash
curl -X POST http://localhost:8000/api/v1/rag/ingest \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@test.txt"
```

Response:
```json
{
  "document_id": "uuid-here",
  "name": "test.txt",
  "chunks_created": 1,
  "message": "Successfully ingested test.txt"
}
```

### 5.3 Search Documents

```bash
curl -X POST http://localhost:8000/api/v1/rag/search \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "pricing",
    "top_k": 3
  }'
```

Response:
```json
[
  {
    "content": "Pricing starts at $49/month for the starter plan.",
    "source": "test.txt",
    "page": 1,
    "similarity": 0.89
  }
]
```

### 5.4 Chat with RAG

```bash
curl -X POST http://localhost:8000/api/v1/rag/chat \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the pricing?",
    "stream": false,
    "model": "gpt-4o-mini"
  }'
```

Response:
```json
{
  "content": "According to the documentation, pricing starts at $49/month for the starter plan. [Source: test.txt, page 1]",
  "sources": [
    {
      "source": "test.txt",
      "page": 1,
      "similarity": 0.89
    }
  ],
  "model": "gpt-4o-mini",
  "provider": "openai"
}
```

### 5.5 Chat with Streaming

```bash
curl -N -X POST http://localhost:8000/api/v1/rag/chat \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What features does AIForge include?",
    "stream": true
  }'
```

Output (Server-Sent Events):
```
data: {"type":"sources","sources":[{"source":"test.txt","page":1,"similarity":0.92}]}

data: {"type":"content","content":"According to "}

data: {"type":"content","content":"the document, "}

data: {"type":"content","content":"AIForge includes..."}

data: {"type":"done"}
```

## Step 6: Test with Python

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"
TOKEN = "your_access_token"

# Upload document
with open("test.txt", "rb") as f:
    response = requests.post(
        f"{BASE_URL}/rag/ingest",
        headers={"Authorization": f"Bearer {TOKEN}"},
        files={"file": f},
    )
    print(response.json())

# Chat
response = requests.post(
    f"{BASE_URL}/rag/chat",
    headers={"Authorization": f"Bearer {TOKEN}"},
    json={
        "message": "What is AIForge?",
        "stream": False,
    },
)
print(response.json()["content"])
```

## Step 7: Explore the API

Open the interactive API docs:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

All RAG endpoints are under the **RAG** tag.

## Common Issues

### "Failed to create document"
- Check Supabase connection (URL and keys)
- Verify migration was run successfully
- Check RLS policies are enabled

### "Embedding generation failed"
- Verify OpenAI API key is valid
- Check API quota/limits
- Ensure you have credits

### "Similarity search failed"
- Ensure `match_document_chunks` function exists
- Verify pgvector extension is enabled
- Check indexes are created

### "Invalid authentication credentials"
- Ensure you're passing the correct JWT token
- Token format: `Authorization: Bearer <token>`
- Check SUPABASE_JWT_SECRET is correct

## Next Steps

1. **Production Setup**
   - Use environment-specific configs
   - Set up Redis for embedding cache
   - Configure proper logging
   - Add rate limiting

2. **Frontend Integration**
   - See `examples/rag_usage_example.py` for code samples
   - Build a chat UI with streaming support
   - Add file upload component
   - Show source citations in responses

3. **Advanced Features**
   - Multi-document conversations
   - Custom prompt templates
   - Hybrid search (semantic + keyword)
   - Document versioning

4. **Monitoring**
   - Track ingestion performance
   - Monitor search latency
   - Log LLM usage and costs
   - Set up alerts for errors

## Resources

- **Full Documentation**: `app/services/rag/README.md`
- **Code Examples**: `examples/rag_usage_example.py`
- **Tests**: `tests/test_rag_integration.py`
- **API Reference**: http://localhost:8000/docs

## Support

If you encounter issues:
1. Check logs: `uvicorn` output shows detailed errors
2. Verify database setup: Run test queries in Supabase
3. Test OpenAI connection: Try embedding a simple text
4. Review the README for troubleshooting tips

---

**You're all set!** 🎉

Your RAG system is now running. Start uploading documents and chatting with your knowledge base.
