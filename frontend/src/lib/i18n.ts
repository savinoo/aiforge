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
      docs: "Documentação",
      github: "GitHub",
      getStarted: "Começar",
    },
    hero: {
      title: "Lance seu SaaS com IA em",
      titleHighlight: "dias, não meses",
      description:
        "Boilerplate Python pronto para produção com RAG, agentes IA, integração WhatsApp e arquitetura multi-tenant. Feito com FastAPI, Next.js e Supabase.",
      cta: "Começar Agora",
      demo: "Ver Demo",
    },
    features: {
      rag: {
        title: "Pipeline RAG Completo",
        description:
          "Ingestão, chunking e busca completos com rastreamento de citações. Construído com pgvector e LangChain.",
        items: [
          "Ingestão de PDF, Markdown e texto",
          "Estratégias inteligentes de chunking",
          "Respostas em streaming com fontes",
          "Isolamento multi-tenant",
        ],
      },
      agents: {
        title: "Framework de Agentes LangGraph",
        description:
          "Sistema modular de agentes com chamada de ferramentas, gerenciamento de estado e raciocínio multi-etapas.",
        items: [
          "Suporte OpenAI, Anthropic, Ollama",
          "Registro de ferramentas customizadas",
          "Conversas com estado",
          "Streaming de eventos",
        ],
      },
      whatsapp: {
        title: "Integração WhatsApp",
        description:
          "Conecte sua IA ao WhatsApp Business API. Mensagens, mídia e webhooks prontos para uso.",
        items: [
          "Envio e recebimento de mensagens",
          "Tratamento de mídia (imagens, áudio)",
          "Verificação de webhooks",
          "Gerenciamento de sessões",
        ],
      },
    },
    pricing: {
      title: "Preços simples e transparentes",
      subtitle: "Pagamento único. Acesso vitalício. Sem mensalidades.",
      oneTime: "pagamento único",
      mostPopular: "Mais Popular",
      viewFull: "Ver Preços Completos",
      starter: {
        name: "Starter",
        description: "Para devs solo",
        features: ["Boilerplate completo", "Pipeline RAG básico", "6 meses de updates"],
      },
      pro: {
        name: "Pro",
        description: "Para builders sérios",
        features: ["Tudo do Starter", "Agentes IA + WhatsApp", "1 ano de updates"],
      },
      enterprise: {
        name: "Enterprise",
        description: "Para times e agências",
        features: ["Tudo do Pro", "Suporte prioritário", "Updates vitalício"],
      },
    },
    footer: "Feito com FastAPI, Next.js 15, Supabase e shadcn/ui",
  },
} as const

export function getTranslations(locale: Locale) {
  return translations[locale]
}
