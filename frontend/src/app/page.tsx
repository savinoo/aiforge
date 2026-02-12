import Link from "next/link";
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
            <Link href="/chat">
              <Button>Get Started</Button>
            </Link>
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
            <Link href="/chat">
              <Button size="lg" className="text-lg px-8">
                Get Started
              </Button>
            </Link>
            <Link href="/chat">
              <Button size="lg" variant="outline" className="text-lg px-8">
                View Demo
              </Button>
            </Link>
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

      {/* Pricing Section */}
      <section className="container mx-auto px-4 py-16 mt-8">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl mb-4">
            Simple, transparent pricing
          </h2>
          <p className="text-lg text-muted-foreground">
            One-time purchase. Lifetime access. No recurring fees.
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-3 max-w-5xl mx-auto">
          {/* Starter */}
          <Card className="border-2">
            <CardHeader className="text-center">
              <CardTitle className="text-xl">Starter</CardTitle>
              <CardDescription>For solo developers</CardDescription>
              <div className="mt-4">
                <span className="text-3xl font-bold">$99</span>
                <span className="text-muted-foreground text-sm ml-1">one-time</span>
              </div>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm">
                <li className="flex items-start">
                  <span className="text-primary mr-2">✓</span>
                  <span>Complete boilerplate</span>
                </li>
                <li className="flex items-start">
                  <span className="text-primary mr-2">✓</span>
                  <span>Basic RAG pipeline</span>
                </li>
                <li className="flex items-start">
                  <span className="text-primary mr-2">✓</span>
                  <span>6 months updates</span>
                </li>
              </ul>
            </CardContent>
          </Card>

          {/* Pro - Highlighted */}
          <Card className="border-primary border-2 shadow-lg relative">
            <div className="absolute -top-3 left-1/2 -translate-x-1/2">
              <span className="bg-primary text-primary-foreground text-xs font-semibold px-3 py-1 rounded-full">
                Most Popular
              </span>
            </div>
            <CardHeader className="text-center pt-6">
              <CardTitle className="text-xl">Pro</CardTitle>
              <CardDescription>For serious builders</CardDescription>
              <div className="mt-4">
                <span className="text-3xl font-bold">$199</span>
                <span className="text-muted-foreground text-sm ml-1">one-time</span>
              </div>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm">
                <li className="flex items-start">
                  <span className="text-primary mr-2">✓</span>
                  <span>Everything in Starter</span>
                </li>
                <li className="flex items-start">
                  <span className="text-primary mr-2">✓</span>
                  <span>AI agents + WhatsApp</span>
                </li>
                <li className="flex items-start">
                  <span className="text-primary mr-2">✓</span>
                  <span>1 year updates</span>
                </li>
              </ul>
            </CardContent>
          </Card>

          {/* Enterprise */}
          <Card className="border-2">
            <CardHeader className="text-center">
              <CardTitle className="text-xl">Enterprise</CardTitle>
              <CardDescription>For teams & agencies</CardDescription>
              <div className="mt-4">
                <span className="text-3xl font-bold">$299</span>
                <span className="text-muted-foreground text-sm ml-1">one-time</span>
              </div>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm">
                <li className="flex items-start">
                  <span className="text-primary mr-2">✓</span>
                  <span>Everything in Pro</span>
                </li>
                <li className="flex items-start">
                  <span className="text-primary mr-2">✓</span>
                  <span>Priority support</span>
                </li>
                <li className="flex items-start">
                  <span className="text-primary mr-2">✓</span>
                  <span>Lifetime updates</span>
                </li>
              </ul>
            </CardContent>
          </Card>
        </div>

        <div className="text-center mt-8">
          <Button size="lg" variant="outline" asChild>
            <Link href="/pricing">View Full Pricing</Link>
          </Button>
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
