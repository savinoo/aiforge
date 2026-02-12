"use client"

import * as React from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Zap, MessageSquare, Database, Globe } from "lucide-react"
import { type Locale, getTranslations } from "@/lib/i18n"

export default function Home() {
  const [locale, setLocale] = React.useState<Locale>("en")
  const t = getTranslations(locale)

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
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setLocale(locale === "en" ? "pt" : "en")}
              className="gap-1.5 font-medium"
            >
              <Globe className="h-4 w-4" />
              {locale === "en" ? "PT" : "EN"}
            </Button>
            <Button variant="ghost" className="hidden sm:inline-flex">{t.nav.docs}</Button>
            <Button variant="ghost" className="hidden sm:inline-flex">{t.nav.github}</Button>
            <Link href="/chat">
              <Button>{t.nav.getStarted}</Button>
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-24 text-center">
        <div className="mx-auto max-w-3xl space-y-8">
          <h1 className="text-5xl font-bold tracking-tight sm:text-6xl">
            {t.hero.title}{" "}
            <span className="text-primary">{t.hero.titleHighlight}</span>
          </h1>
          <p className="text-xl text-muted-foreground">
            {t.hero.description}
          </p>
          <div className="flex items-center justify-center gap-4">
            <Link href="/chat">
              <Button size="lg" className="text-lg px-8">
                {t.hero.cta}
              </Button>
            </Link>
            <Link href="/chat">
              <Button size="lg" variant="outline" className="text-lg px-8">
                {t.hero.demo}
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
              <CardTitle>{t.features.rag.title}</CardTitle>
              <CardDescription>{t.features.rag.description}</CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm text-muted-foreground">
                {t.features.rag.items.map((item) => (
                  <li key={item}>• {item}</li>
                ))}
              </ul>
            </CardContent>
          </Card>

          {/* Feature 2: Agent Framework */}
          <Card className="border-2 hover:border-primary transition-colors">
            <CardHeader>
              <Zap className="h-12 w-12 mb-4 text-primary" />
              <CardTitle>{t.features.agents.title}</CardTitle>
              <CardDescription>{t.features.agents.description}</CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm text-muted-foreground">
                {t.features.agents.items.map((item) => (
                  <li key={item}>• {item}</li>
                ))}
              </ul>
            </CardContent>
          </Card>

          {/* Feature 3: WhatsApp Integration */}
          <Card className="border-2 hover:border-primary transition-colors">
            <CardHeader>
              <MessageSquare className="h-12 w-12 mb-4 text-primary" />
              <CardTitle>{t.features.whatsapp.title}</CardTitle>
              <CardDescription>{t.features.whatsapp.description}</CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm text-muted-foreground">
                {t.features.whatsapp.items.map((item) => (
                  <li key={item}>• {item}</li>
                ))}
              </ul>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Pricing Section */}
      <section className="container mx-auto px-4 py-16 mt-8">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl mb-4">
            {t.pricing.title}
          </h2>
          <p className="text-lg text-muted-foreground">
            {t.pricing.subtitle}
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-3 max-w-5xl mx-auto">
          {/* Starter */}
          <Card className="border-2">
            <CardHeader className="text-center">
              <CardTitle className="text-xl">{t.pricing.starter.name}</CardTitle>
              <CardDescription>{t.pricing.starter.description}</CardDescription>
              <div className="mt-4">
                <span className="text-3xl font-bold">$99</span>
                <span className="text-muted-foreground text-sm ml-1">{t.pricing.oneTime}</span>
              </div>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm">
                {t.pricing.starter.features.map((f) => (
                  <li key={f} className="flex items-start">
                    <span className="text-primary mr-2">✓</span>
                    <span>{f}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>

          {/* Pro - Highlighted */}
          <Card className="border-primary border-2 shadow-lg relative">
            <div className="absolute -top-3 left-1/2 -translate-x-1/2">
              <span className="bg-primary text-primary-foreground text-xs font-semibold px-3 py-1 rounded-full">
                {t.pricing.mostPopular}
              </span>
            </div>
            <CardHeader className="text-center pt-6">
              <CardTitle className="text-xl">{t.pricing.pro.name}</CardTitle>
              <CardDescription>{t.pricing.pro.description}</CardDescription>
              <div className="mt-4">
                <span className="text-3xl font-bold">$199</span>
                <span className="text-muted-foreground text-sm ml-1">{t.pricing.oneTime}</span>
              </div>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm">
                {t.pricing.pro.features.map((f) => (
                  <li key={f} className="flex items-start">
                    <span className="text-primary mr-2">✓</span>
                    <span>{f}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>

          {/* Enterprise */}
          <Card className="border-2">
            <CardHeader className="text-center">
              <CardTitle className="text-xl">{t.pricing.enterprise.name}</CardTitle>
              <CardDescription>{t.pricing.enterprise.description}</CardDescription>
              <div className="mt-4">
                <span className="text-3xl font-bold">$299</span>
                <span className="text-muted-foreground text-sm ml-1">{t.pricing.oneTime}</span>
              </div>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm">
                {t.pricing.enterprise.features.map((f) => (
                  <li key={f} className="flex items-start">
                    <span className="text-primary mr-2">✓</span>
                    <span>{f}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        </div>

        <div className="text-center mt-8">
          <Button size="lg" variant="outline" asChild>
            <Link href="/pricing">{t.pricing.viewFull}</Link>
          </Button>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t mt-24">
        <div className="container mx-auto px-4 py-8 text-center text-sm text-muted-foreground">
          <p>{t.footer}</p>
        </div>
      </footer>
    </div>
  )
}
