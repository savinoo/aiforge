# CLAUDE.md — AIForge

## What is this
AIForge is a Python AI SaaS boilerplate — the first production-ready starter kit for developers building AI-powered products. It's also the foundation for our own products (chatbot service for Brazilian SMBs, fiscal RAG micro-SaaS for accountants).

## Architecture

```
aiforge/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/v1/       # API routes (REST endpoints)
│   │   ├── core/         # Config, security, dependencies
│   │   ├── models/       # SQLAlchemy/Supabase models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/
│   │   │   ├── rag/      # RAG pipeline (ingestion, chunking, search, chat)
│   │   │   ├── agents/   # LangGraph agent framework
│   │   │   └── whatsapp/ # WhatsApp Business API integration
│   │   └── db/           # Database setup, migrations
│   └── tests/
├── frontend/             # Next.js 15 + shadcn/ui
├── docs/                 # Documentation
├── docker-compose.yml    # Local development
└── .env.example          # Environment variables template
```

## Tech Stack
- **Backend:** FastAPI (Python 3.12+)
- **Frontend:** Next.js 15, TypeScript, Tailwind CSS, shadcn/ui
- **Auth:** Supabase Auth
- **Database:** Supabase (PostgreSQL + pgvector)
- **Payments:** LemonSqueezy (primary), Stripe (secondary)
- **RAG:** LangChain + pgvector
- **Agents:** LangGraph
- **WhatsApp:** 360dialog / WhatsApp Cloud API
- **AI Models:** OpenAI, Anthropic, Ollama (multi-provider)
- **Deploy:** Docker + Railway/Render (backend) + Vercel (frontend)

## Key Commands
```bash
# Backend
cd backend && pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend && npm install && npm run dev

# Docker (full stack)
docker-compose up --build

# Tests
cd backend && pytest
```

## Environment Variables
Copy `.env.example` to `.env` and fill in:
- SUPABASE_URL, SUPABASE_KEY, SUPABASE_SERVICE_KEY
- OPENAI_API_KEY
- ANTHROPIC_API_KEY (optional)
- LEMONSQUEEZY_API_KEY, LEMONSQUEEZY_WEBHOOK_SECRET
- WHATSAPP_TOKEN, WHATSAPP_PHONE_NUMBER_ID (optional, for WhatsApp integration)

## Design Principles
1. **Multi-tenant by default** — Row Level Security via Supabase
2. **Multi-model** — Abstract LLM provider, swap via config
3. **Streaming first** — All AI responses stream by default
4. **Citation tracking** — RAG always returns sources
5. **Modular** — Each service (RAG, agents, WhatsApp) works independently
6. **Deploy in minutes** — One-click deploy templates for Railway/Render/Vercel
