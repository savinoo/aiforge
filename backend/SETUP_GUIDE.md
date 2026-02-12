# AIForge Backend - Complete Setup Guide

This guide will walk you through setting up the AIForge backend from scratch.

## Prerequisites

- Python 3.12 or higher
- pip (Python package manager)
- A Supabase account (free tier works)
- OpenAI API key (for AI features)
- Anthropic API key (optional, for Claude)

## Quick Start (5 minutes)

### Option 1: Automatic Setup

```bash
cd backend
chmod +x setup.sh
./setup.sh
```

This will:
1. Create a virtual environment
2. Install all dependencies
3. Create `.env` from template

### Option 2: Manual Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
```

## Configuration

### 1. Supabase Setup

1. Go to [supabase.com](https://supabase.com) and create a new project
2. Once created, go to Project Settings → API
3. Copy the following values to your `.env`:
   - `SUPABASE_URL` - Project URL
   - `SUPABASE_ANON_KEY` - anon/public key
   - `SUPABASE_SERVICE_ROLE_KEY` - service_role key (⚠️ Keep this secret!)
4. Go to Project Settings → API → JWT Settings
   - Copy `JWT Secret` to `SUPABASE_JWT_SECRET`

### 2. OpenAI Setup

1. Go to [platform.openai.com](https://platform.openai.com)
2. Create an API key
3. Add to `.env` as `OPENAI_API_KEY`

### 3. Anthropic Setup (Optional)

1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Create an API key
3. Add to `.env` as `ANTHROPIC_API_KEY`

### 4. LemonSqueezy Setup (Optional - for payments)

1. Go to [lemonsqueezy.com](https://lemonsqueezy.com)
2. Get your API key from Settings → API
3. Add these to `.env`:
   - `LEMONSQUEEZY_API_KEY`
   - `LEMONSQUEEZY_STORE_ID`
   - `LEMONSQUEEZY_WEBHOOK_SECRET`

### 5. WhatsApp Setup (Optional - for messaging)

1. Set up WhatsApp Business API (via Meta or 360dialog)
2. Get your credentials:
   - `WHATSAPP_PHONE_NUMBER_ID`
   - `WHATSAPP_ACCESS_TOKEN`
   - `WHATSAPP_VERIFY_TOKEN`
   - `WHATSAPP_BUSINESS_ACCOUNT_ID`

## Running the Application

### Development Mode

```bash
# Activate virtual environment
source venv/bin/activate

# Run with auto-reload
python -m app.main

# Or using uvicorn directly
uvicorn app.main:app --reload
```

Server will start at `http://localhost:8000`

### Using Make Commands

```bash
make dev          # Run development server
make test         # Run tests
make format       # Format code
make lint         # Lint code
```

### Using Docker

```bash
# Build and run with docker-compose
docker-compose up --build

# Or build manually
docker build -t aiforge-backend .
docker run -p 8000:8000 --env-file .env aiforge-backend
```

## Testing Your Setup

### 1. Check if server is running

Open browser and go to:
- `http://localhost:8000` - Should show API info
- `http://localhost:8000/docs` - Interactive API documentation

### 2. Test health endpoints

```bash
curl http://localhost:8000/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "app_name": "AIForge",
  "environment": "development",
  "timestamp": "2024-02-12T10:30:00",
  "version": "1.0.0"
}
```

### 3. Test authentication

#### Sign Up
```bash
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePassword123",
    "full_name": "Test User"
  }'
```

#### Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePassword123"
  }'
```

Save the `access_token` from the response.

#### Get Current User
```bash
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_health.py

# Run with verbose output
pytest -v
```

## Project Structure

```
backend/
├── app/
│   ├── api/v1/              # API endpoints
│   │   ├── auth.py          # Authentication (signup, login, me)
│   │   ├── health.py        # Health checks
│   │   └── router.py        # Main router
│   ├── core/                # Core functionality
│   │   ├── config.py        # Settings (env vars)
│   │   └── deps.py          # Dependencies (auth, db)
│   ├── db/                  # Database
│   │   └── supabase.py      # Supabase client
│   ├── models/              # Database models (TODO)
│   ├── schemas/             # Pydantic schemas (TODO)
│   ├── services/            # Business logic
│   │   ├── rag/             # RAG services (TODO)
│   │   ├── agents/          # AI agents (TODO)
│   │   └── whatsapp/        # WhatsApp integration (TODO)
│   └── main.py              # FastAPI app
├── tests/                   # Test suite
├── .env.example             # Environment template
├── requirements.txt         # Python dependencies
├── Dockerfile               # Docker image
├── docker-compose.yml       # Local development
├── Makefile                 # Common commands
└── README.md                # Documentation
```

## Next Steps

### 1. Build RAG Service
Create document ingestion and retrieval:
- `/app/services/rag/ingestion.py` - Upload and process documents
- `/app/services/rag/retrieval.py` - Semantic search
- `/app/services/rag/chat.py` - Chat with citations

### 2. Build AI Agents
Create LangGraph agents:
- `/app/services/agents/base.py` - Base agent class
- `/app/services/agents/orchestrator.py` - Multi-agent orchestration
- Create API endpoints in `/app/api/v1/agents.py`

### 3. WhatsApp Integration
Set up messaging automation:
- `/app/services/whatsapp/client.py` - WhatsApp client
- `/app/services/whatsapp/webhook.py` - Handle incoming messages
- Create API endpoints in `/app/api/v1/whatsapp.py`

### 4. Payment Processing
Handle subscriptions and payments:
- `/app/services/payments/lemonsqueezy.py` - LemonSqueezy integration
- `/app/api/v1/payments.py` - Payment endpoints and webhooks

## Troubleshooting

### "Module not found" errors
```bash
# Make sure you're in the virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Port 8000 already in use
```bash
# Find and kill the process
lsof -ti:8000 | xargs kill -9

# Or use a different port
uvicorn app.main:app --reload --port 8001
```

### Supabase connection errors
- Check that `SUPABASE_URL` starts with `https://`
- Verify your API keys are correct
- Make sure your Supabase project is not paused

### Import errors
Make sure you're running commands from the `backend/` directory:
```bash
cd /path/to/aiforge/backend
python -m app.main
```

## Production Deployment

### Environment Variables
Set these in production:
```bash
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=generate-a-strong-random-key-here
```

### Deploy to Railway
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Deploy
railway up
```

### Deploy to Render
1. Connect your GitHub repo to Render
2. Create a new Web Service
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables

## Support

For issues and questions:
- Check the [README.md](README.md)
- Review API docs at `/docs` when running
- Open an issue on GitHub (if this becomes open source)

## License

MIT
