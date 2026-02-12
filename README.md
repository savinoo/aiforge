<div align="center">

# AIForge

### Ship your AI SaaS in days, not months.

The first production-ready **Python AI boilerplate** with RAG, AI agents, WhatsApp integration, and multi-tenant architecture.

[Get Started](#quick-start) &bull; [Features](#features) &bull; [Architecture](#architecture) &bull; [Pricing](https://aiforge.dev) &bull; [Docs](#documentation)

![Python](https://img.shields.io/badge/Python-3.12+-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-16-black?logo=next.js&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-Auth+DB+Vectors-3FCF8E?logo=supabase&logoColor=white)
![License](https://img.shields.io/badge/License-Commercial-orange)

</div>

---

## Why AIForge?

**ShipFast** proved developers will pay for boilerplates. But it's Next.js only.
**SaaS Pegasus** is Python/Django, but has zero AI infrastructure.

**Nobody has built a Python boilerplate with production-ready AI features.** Until now.

AIForge gives you everything you need to launch an AI-powered SaaS product:

- A complete **RAG pipeline** (upload docs, chat with citations)
- An **AI agent framework** (LangGraph with tool-use)
- **WhatsApp Business API** integration
- **Auth, billing, multi-tenancy** — all wired up

Stop spending weeks on infrastructure. Start shipping your product.

---

## Features

### RAG Pipeline
- Multi-format document ingestion (PDF, DOCX, TXT, CSV, Markdown, HTML, URLs)
- Smart chunking with configurable strategies
- OpenAI embeddings with batching and caching
- pgvector similarity search with multi-tenant isolation
- **Streaming responses with inline citation tracking**
- Conversation memory and context management

### AI Agent Framework
- LangGraph-based agent orchestration
- Multi-provider support (OpenAI, Anthropic, Ollama)
- Custom tool registration
- Stateful conversations with session management
- Event streaming via Server-Sent Events (SSE)

### WhatsApp Integration
- WhatsApp Business Cloud API (via Meta)
- Webhook verification and message handling
- Media support (images, audio, documents)
- Session management per phone number
- Template message support

### SaaS Infrastructure
- **Auth:** Supabase Auth with JWT verification
- **Database:** Supabase PostgreSQL + pgvector
- **Billing:** LemonSqueezy integration (one-time + subscriptions)
- **Multi-tenancy:** Row Level Security (RLS) — data isolation by default
- **API:** FastAPI with automatic OpenAPI docs
- **Frontend:** Next.js 16 + TypeScript + Tailwind CSS + shadcn/ui
- **Deploy:** Docker + one-click deploy (Railway, Render, Vercel)

---

## Architecture

```
aiforge/
├── backend/                    # FastAPI backend (Python 3.12+)
│   ├── app/
│   │   ├── api/v1/             # REST API endpoints
│   │   │   ├── auth.py         # Authentication (signup, login, refresh)
│   │   │   ├── rag.py          # RAG pipeline (ingest, chat, search)
│   │   │   ├── billing.py      # LemonSqueezy billing
│   │   │   └── health.py       # Health checks
│   │   ├── core/               # Config, security, dependencies
│   │   ├── services/
│   │   │   ├── rag/            # RAG: ingestion, chunking, embeddings, retrieval, chat
│   │   │   ├── agents/         # LangGraph agent framework
│   │   │   ├── billing/        # LemonSqueezy integration
│   │   │   └── whatsapp/       # WhatsApp Business API
│   │   └── db/                 # Database clients
│   ├── migrations/             # SQL migrations
│   └── tests/
├── frontend/                   # Next.js 16 + shadcn/ui
│   ├── src/app/                # App router pages
│   │   ├── page.tsx            # Landing page
│   │   ├── chat/               # Chat interface with streaming
│   │   └── pricing/            # Pricing page
│   ├── src/components/         # React components
│   └── src/lib/                # API client, utilities
├── docker-compose.yml          # Full stack local development
└── .env.example                # Environment variables template
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | FastAPI, Python 3.12+, Pydantic v2 |
| **Frontend** | Next.js 16, React 19, TypeScript, Tailwind CSS v4, shadcn/ui |
| **Auth** | Supabase Auth (JWT) |
| **Database** | Supabase PostgreSQL + pgvector |
| **RAG** | LangChain, OpenAI Embeddings, pgvector |
| **Agents** | LangGraph |
| **Payments** | LemonSqueezy (Merchant of Record) |
| **WhatsApp** | WhatsApp Cloud API (Meta) |
| **AI Models** | OpenAI, Anthropic, Ollama (multi-provider) |
| **Deploy** | Docker, Railway/Render (backend), Vercel (frontend) |

---

## Quick Start

### Prerequisites
- Python 3.12+
- Node.js 20+
- A Supabase project ([create one free](https://supabase.com))
- An OpenAI API key

### 1. Clone and configure

```bash
git clone https://github.com/savinoo/aiforge.git
cd aiforge
cp .env.example .env
# Fill in your Supabase and OpenAI credentials
```

### 2. Start the backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 3. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

### 4. Or use Docker

```bash
docker-compose up --build
```

Open [http://localhost:3000](http://localhost:3000) and start building.

---

## Documentation

- [RAG Pipeline Guide](backend/QUICKSTART_RAG.md) — How to ingest documents and chat
- [RAG Implementation Details](backend/RAG_IMPLEMENTATION_SUMMARY.md) — Architecture deep dive
- [Setup Guide](backend/SETUP_GUIDE.md) — Detailed setup instructions
- [API Reference](http://localhost:8000/docs) — Auto-generated OpenAPI docs (when running)

---

## Pricing

| | Starter | Pro | Enterprise |
|---|---------|-----|-----------|
| **Price** | $99 | **$199** | $299 |
| FastAPI + Next.js boilerplate | ✅ | ✅ | ✅ |
| Supabase auth & DB | ✅ | ✅ | ✅ |
| Basic RAG pipeline | ✅ | ✅ | ✅ |
| Full RAG with citations | | ✅ | ✅ |
| AI agent framework | | ✅ | ✅ |
| WhatsApp integration | | ✅ | ✅ |
| Multi-tenancy | | ✅ | ✅ |
| Priority support | | | ✅ |
| Custom integrations | | | ✅ |
| Lifetime updates | | | ✅ |
| 1-on-1 onboarding call | | | ✅ |

All plans are **one-time purchases**. No subscriptions. No recurring fees.

---

## Roadmap

- [x] FastAPI backend skeleton with auth
- [x] Next.js frontend with landing page
- [x] Production RAG pipeline with streaming and citations
- [x] LemonSqueezy billing integration
- [x] Chat interface with streaming
- [ ] LangGraph agent framework
- [ ] WhatsApp Business API integration
- [ ] Admin dashboard
- [ ] One-click deploy templates
- [ ] Documentation site

---

## Built by

**Lucas Savino** — AI/Agentic Engineer

Building AIForge in public. Follow the journey:
- [LinkedIn](https://linkedin.com/in/lucas-savino)
- [GitHub](https://github.com/savinoo)

---

<div align="center">

**Stop building infrastructure. Start shipping AI products.**

[Get AIForge →](https://aiforge.dev)

</div>
