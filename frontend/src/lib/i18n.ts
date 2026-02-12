export type Locale = "en" | "pt"

export const translations = {
  en: {
    nav: {
      docs: "Documentation",
      github: "GitHub",
      getStarted: "Get Started",
    },
    hero: {
      title: "Ship your AI SaaS in",
      titleHighlight: "days, not months",
      description:
        "Production-ready Python boilerplate with RAG, AI agents, WhatsApp integration, and multi-tenant architecture. Built with FastAPI, Next.js, and Supabase.",
      cta: "Get Started",
      demo: "View Demo",
    },
    features: {
      rag: {
        title: "Production RAG Pipeline",
        description:
          "Complete ingestion, chunking, and retrieval with citation tracking. Built on pgvector and LangChain.",
        items: [
          "PDF, Markdown, and text ingestion",
          "Smart chunking strategies",
          "Streaming responses with sources",
          "Multi-tenant isolation",
        ],
      },
      agents: {
        title: "LangGraph Agent Framework",
        description:
          "Modular agent system with tool calling, state management, and multi-step reasoning.",
        items: [
          "OpenAI, Anthropic, Ollama support",
          "Custom tool registration",
          "Stateful conversations",
          "Event streaming",
        ],
      },
      whatsapp: {
        title: "WhatsApp Integration",
        description:
          "Connect your AI to WhatsApp Business API. Handle messages, media, and webhooks out of the box.",
        items: [
          "Message sending & receiving",
          "Media handling (images, audio)",
          "Webhook verification",
          "Session management",
        ],
      },
    },
    pricing: {
      title: "Simple, transparent pricing",
      subtitle: "One-time purchase. Lifetime access. No recurring fees.",
      oneTime: "one-time",
      mostPopular: "Most Popular",
      viewFull: "View Full Pricing",
      starter: {
        name: "Starter",
        description: "For solo developers",
        features: ["Complete boilerplate", "Basic RAG pipeline", "6 months updates"],
      },
      pro: {
        name: "Pro",
        description: "For serious builders",
        features: ["Everything in Starter", "AI agents + WhatsApp", "1 year updates"],
      },
      enterprise: {
        name: "Enterprise",
        description: "For teams & agencies",
        features: ["Everything in Pro", "Priority support", "Lifetime updates"],
      },
    },
    footer: "Built with FastAPI, Next.js 15, Supabase, and shadcn/ui",
  },
  pt: {
    nav: {
      docs: "Documentacao",
      github: "GitHub",
      getStarted: "Comecar",
    },
    hero: {
      title: "Lance seu SaaS com IA em",
      titleHighlight: "dias, nao meses",
      description:
        "Boilerplate Python pronto para producao com RAG, agentes IA, integracao WhatsApp e arquitetura multi-tenant. Feito com FastAPI, Next.js e Supabase.",
      cta: "Comecar Agora",
      demo: "Ver Demo",
    },
    features: {
      rag: {
        title: "Pipeline RAG Completo",
        description:
          "Ingestao, chunking e busca completos com rastreamento de citacoes. Construido com pgvector e LangChain.",
        items: [
          "Ingestao de PDF, Markdown e texto",
          "Estrategias inteligentes de chunking",
          "Respostas em streaming com fontes",
          "Isolamento multi-tenant",
        ],
      },
      agents: {
        title: "Framework de Agentes LangGraph",
        description:
          "Sistema modular de agentes com chamada de ferramentas, gerenciamento de estado e raciocinio multi-etapas.",
        items: [
          "Suporte OpenAI, Anthropic, Ollama",
          "Registro de ferramentas customizadas",
          "Conversas com estado",
          "Streaming de eventos",
        ],
      },
      whatsapp: {
        title: "Integracao WhatsApp",
        description:
          "Conecte sua IA ao WhatsApp Business API. Mensagens, midia e webhooks prontos para uso.",
        items: [
          "Envio e recebimento de mensagens",
          "Tratamento de midia (imagens, audio)",
          "Verificacao de webhooks",
          "Gerenciamento de sessoes",
        ],
      },
    },
    pricing: {
      title: "Precos simples e transparentes",
      subtitle: "Pagamento unico. Acesso vitalicio. Sem mensalidades.",
      oneTime: "pagamento unico",
      mostPopular: "Mais Popular",
      viewFull: "Ver Precos Completos",
      starter: {
        name: "Starter",
        description: "Para devs solo",
        features: ["Boilerplate completo", "Pipeline RAG basico", "6 meses de updates"],
      },
      pro: {
        name: "Pro",
        description: "Para builders serios",
        features: ["Tudo do Starter", "Agentes IA + WhatsApp", "1 ano de updates"],
      },
      enterprise: {
        name: "Enterprise",
        description: "Para times e agencias",
        features: ["Tudo do Pro", "Suporte prioritario", "Updates vitalicio"],
      },
    },
    footer: "Feito com FastAPI, Next.js 15, Supabase e shadcn/ui",
  },
} as const

export function getTranslations(locale: Locale) {
  return translations[locale]
}
