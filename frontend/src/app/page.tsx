import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Zap, MessageSquare, Database } from "lucide-react";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-muted">
      {/* Navigation */}
      <nav className="border-b">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Zap className="h-6 w-6" />
            <span className="text-xl font-bold">AIForge</span>
          </div>
          <div className="flex items-center space-x-4">
            <Button variant="ghost">Documentation</Button>
            <Button variant="ghost">GitHub</Button>
            <Button>Get Started</Button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-24 text-center">
        <div className="mx-auto max-w-3xl space-y-8">
          <h1 className="text-5xl font-bold tracking-tight sm:text-6xl">
            Ship your AI SaaS in{" "}
            <span className="text-primary">days, not months</span>
          </h1>
          <p className="text-xl text-muted-foreground">
            Production-ready Python boilerplate with RAG, AI agents, WhatsApp integration,
            and multi-tenant architecture. Built with FastAPI, Next.js, and Supabase.
          </p>
          <div className="flex items-center justify-center gap-4">
            <Button size="lg" className="text-lg px-8">
              Get Started
            </Button>
            <Button size="lg" variant="outline" className="text-lg px-8">
              View Demo
            </Button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="container mx-auto px-4 py-16">
        <div className="grid gap-8 md:grid-cols-3">
          {/* Feature 1: RAG Pipeline */}
          <Card className="border-2 hover:border-primary transition-colors">
            <CardHeader>
              <Database className="h-12 w-12 mb-4 text-primary" />
              <CardTitle>Production RAG Pipeline</CardTitle>
              <CardDescription>
                Complete ingestion, chunking, and retrieval with citation tracking.
                Built on pgvector and LangChain.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>• PDF, Markdown, and text ingestion</li>
                <li>• Smart chunking strategies</li>
                <li>• Streaming responses with sources</li>
                <li>• Multi-tenant isolation</li>
              </ul>
            </CardContent>
          </Card>

          {/* Feature 2: Agent Framework */}
          <Card className="border-2 hover:border-primary transition-colors">
            <CardHeader>
              <Zap className="h-12 w-12 mb-4 text-primary" />
              <CardTitle>LangGraph Agent Framework</CardTitle>
              <CardDescription>
                Modular agent system with tool calling, state management,
                and multi-step reasoning.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>• OpenAI, Anthropic, Ollama support</li>
                <li>• Custom tool registration</li>
                <li>• Stateful conversations</li>
                <li>• Event streaming</li>
              </ul>
            </CardContent>
          </Card>

          {/* Feature 3: WhatsApp Integration */}
          <Card className="border-2 hover:border-primary transition-colors">
            <CardHeader>
              <MessageSquare className="h-12 w-12 mb-4 text-primary" />
              <CardTitle>WhatsApp Integration</CardTitle>
              <CardDescription>
                Connect your AI to WhatsApp Business API. Handle messages,
                media, and webhooks out of the box.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>• Message sending & receiving</li>
                <li>• Media handling (images, audio)</li>
                <li>• Webhook verification</li>
                <li>• Session management</li>
              </ul>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t mt-24">
        <div className="container mx-auto px-4 py-8 text-center text-sm text-muted-foreground">
          <p>Built with FastAPI, Next.js 15, Supabase, and shadcn/ui</p>
        </div>
      </footer>
    </div>
  );
}
