# AIForge Backend

Production-ready FastAPI backend for AI-powered SaaS applications.

## Features

- **FastAPI** - Modern, fast web framework with automatic API documentation
- **Supabase** - Authentication, database, and real-time subscriptions
- **AI Integration** - OpenAI and Anthropic ready-to-use
- **Payment Processing** - LemonSqueezy integration
- **WhatsApp Business** - Messaging automation
- **Type Safety** - Full type hints with Pydantic validation
- **Production Ready** - Proper error handling, logging, and health checks

## Quick Start

### 1. Install Dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your actual credentials
```

Required environment variables:
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_ANON_KEY` - Supabase anonymous key
- `SUPABASE_SERVICE_ROLE_KEY` - Supabase service role key
- `SUPABASE_JWT_SECRET` - Supabase JWT secret
- `OPENAI_API_KEY` - OpenAI API key
- `ANTHROPIC_API_KEY` - Anthropic API key

### 3. Run the Server

```bash
# Development mode (with auto-reload)
python -m app.main

# Or using uvicorn directly
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

## Project Structure

```
backend/
├── app/
│   ├── api/v1/           # API endpoints
│   │   ├── auth.py       # Authentication endpoints
│   │   ├── health.py     # Health checks
│   │   └── router.py     # Main router
│   ├── core/             # Core functionality
│   │   ├── config.py     # Settings and configuration
│   │   └── deps.py       # Dependency injection
│   ├── db/               # Database clients
│   │   └── supabase.py   # Supabase client
│   ├── models/           # Database models (TODO)
│   ├── schemas/          # Pydantic schemas (TODO)
│   ├── services/         # Business logic
│   │   ├── rag/          # RAG services (TODO)
│   │   ├── agents/       # AI agent services (TODO)
│   │   └── whatsapp/     # WhatsApp integration (TODO)
│   └── main.py           # FastAPI application
├── tests/                # Test suite (TODO)
├── .env.example          # Environment template
└── requirements.txt      # Python dependencies
```

## API Endpoints

### Health Checks
- `GET /api/v1/health` - Basic health check
- `GET /api/v1/health/ready` - Readiness probe
- `GET /api/v1/health/live` - Liveness probe

### Authentication
- `POST /api/v1/auth/signup` - Create new user
- `POST /api/v1/auth/login` - Login user
- `POST /api/v1/auth/refresh` - Refresh access token
- `GET /api/v1/auth/me` - Get current user
- `POST /api/v1/auth/logout` - Logout user

## Development

### Running Tests

```bash
pytest
```

### Code Quality

The codebase follows these principles:
- Type hints everywhere
- Async/await for I/O operations
- Proper error handling with HTTPException
- Clean separation of concerns
- Production-ready logging

### Adding New Endpoints

1. Create a new router in `app/api/v1/`
2. Include it in `app/api/v1/router.py`
3. Add any new dependencies to `requirements.txt`

Example:

```python
# app/api/v1/my_feature.py
from fastapi import APIRouter
from app.core.deps import CurrentUser

router = APIRouter(prefix="/my-feature", tags=["My Feature"])

@router.get("/")
async def my_endpoint(current_user: CurrentUser):
    return {"message": "Hello from my feature!"}
```

```python
# app/api/v1/router.py
from app.api.v1 import my_feature

api_router.include_router(my_feature.router)
```

## Deployment

### Docker (Recommended)

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables in Production

Make sure to set:
- `ENVIRONMENT=production`
- `DEBUG=false`
- `SECRET_KEY` - Use a strong random key
- All API keys and credentials

### Health Check Endpoints

Use `/api/v1/health/ready` and `/api/v1/health/live` for:
- Kubernetes liveness/readiness probes
- Docker health checks
- Load balancer health checks

## Next Steps

1. **Implement RAG Service** - Add document ingestion and retrieval
2. **Build AI Agents** - Create agent orchestration with LangGraph
3. **WhatsApp Integration** - Set up webhook and messaging
4. **Payment Webhooks** - Handle LemonSqueezy events
5. **Add Tests** - Write comprehensive test coverage

## License

MIT
