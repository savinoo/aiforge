import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Check, Zap } from "lucide-react";
import Link from "next/link";

const pricingTiers = [
  {
    id: "starter",
    name: "Starter",
    price: 99,
    description: "Perfect for solo developers getting started",
    features: [
      "FastAPI + Next.js boilerplate",
      "Supabase auth & DB",
      "Basic RAG pipeline",
      "Email support",
      "6 months updates",
    ],
    highlighted: false,
  },
  {
    id: "pro",
    name: "Pro",
    price: 199,
    description: "For serious builders shipping production apps",
    features: [
      "Everything in Starter",
      "Full RAG with citations",
      "AI agent framework",
      "WhatsApp integration",
      "Multi-tenancy",
      "1 year updates",
      "Discord community",
    ],
    highlighted: true,
  },
  {
    id: "enterprise",
    name: "Enterprise",
    price: 299,
    description: "For teams and agencies building at scale",
    features: [
      "Everything in Pro",
      "Priority support",
      "Custom integrations",
      "Lifetime updates",
      "1-on-1 onboarding call",
      "Source code license",
    ],
    highlighted: false,
  },
];

export default function PricingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-muted">
      {/* Navigation */}
      <nav className="border-b">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <Link href="/" className="flex items-center space-x-2">
            <Zap className="h-6 w-6" />
            <span className="text-xl font-bold">AIForge</span>
          </Link>
          <div className="flex items-center space-x-4">
            <Button variant="ghost" asChild>
              <Link href="/">Home</Link>
            </Button>
            <Button variant="ghost">Documentation</Button>
            <Button variant="ghost">GitHub</Button>
            <Button>Get Started</Button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-16 text-center">
        <div className="mx-auto max-w-3xl space-y-4">
          <h1 className="text-4xl font-bold tracking-tight sm:text-5xl">
            Simple, transparent pricing
          </h1>
          <p className="text-xl text-muted-foreground">
            One-time purchase. Lifetime access. No recurring fees.
            <br />
            Choose the tier that fits your needs.
          </p>
        </div>
      </section>

      {/* Pricing Cards */}
      <section className="container mx-auto px-4 pb-24">
        <div className="grid gap-8 md:grid-cols-3 max-w-6xl mx-auto">
          {pricingTiers.map((tier) => (
            <Card
              key={tier.id}
              className={`relative flex flex-col ${
                tier.highlighted
                  ? "border-primary border-2 shadow-xl scale-105"
                  : "border-2"
              }`}
            >
              {tier.highlighted && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                  <span className="bg-primary text-primary-foreground text-sm font-semibold px-3 py-1 rounded-full">
                    Most Popular
                  </span>
                </div>
              )}

              <CardHeader className="text-center pb-8 pt-6">
                <CardTitle className="text-2xl font-bold">{tier.name}</CardTitle>
                <CardDescription className="text-base mt-2">
                  {tier.description}
                </CardDescription>
                <div className="mt-4">
                  <span className="text-4xl font-bold">${tier.price}</span>
                  <span className="text-muted-foreground ml-2">one-time</span>
                </div>
              </CardHeader>

              <CardContent className="flex-grow">
                <ul className="space-y-3">
                  {tier.features.map((feature, index) => (
                    <li key={index} className="flex items-start">
                      <Check className="h-5 w-5 text-primary mr-3 mt-0.5 flex-shrink-0" />
                      <span className="text-sm">{feature}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>

              <CardFooter className="pt-6">
                <Button
                  className="w-full"
                  size="lg"
                  variant={tier.highlighted ? "default" : "outline"}
                >
                  Get {tier.name}
                </Button>
              </CardFooter>
            </Card>
          ))}
        </div>

        {/* FAQ Section */}
        <div className="mt-24 max-w-3xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">
            Frequently Asked Questions
          </h2>
          <div className="space-y-6">
            <div>
              <h3 className="font-semibold text-lg mb-2">
                What do I get when I purchase?
              </h3>
              <p className="text-muted-foreground">
                You get immediate access to the complete AIForge codebase, including
                all features for your chosen tier. You'll receive a license key and
                download link via email.
              </p>
            </div>
            <div>
              <h3 className="font-semibold text-lg mb-2">
                Are there any recurring fees?
              </h3>
              <p className="text-muted-foreground">
                No! This is a one-time purchase. You pay once and own the code forever.
                Updates are included for the duration specified in your tier.
              </p>
            </div>
            <div>
              <h3 className="font-semibold text-lg mb-2">
                Can I use this for client projects?
              </h3>
              <p className="text-muted-foreground">
                Yes! All tiers include a license to build unlimited projects for yourself
                or your clients. Enterprise tier includes a source code license for
                redistribution.
              </p>
            </div>
            <div>
              <h3 className="font-semibold text-lg mb-2">
                Do you offer refunds?
              </h3>
              <p className="text-muted-foreground">
                Yes, we offer a 14-day money-back guarantee. If AIForge isn't right for
                you, just email us for a full refund.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t">
        <div className="container mx-auto px-4 py-8 text-center text-sm text-muted-foreground">
          <p>Built with FastAPI, Next.js 15, Supabase, and shadcn/ui</p>
        </div>
      </footer>
    </div>
  );
}
