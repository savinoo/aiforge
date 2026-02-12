"use client"

import * as React from "react"
import { ChatSidebar, type UploadedDocument } from "@/components/chat/chat-sidebar"
import { ChatMessages } from "@/components/chat/chat-messages"
import { ChatInput } from "@/components/chat/chat-input"
import { type MessageProps } from "@/components/chat/chat-message"
import { Button } from "@/components/ui/button"
import { ChevronDown, Menu } from "lucide-react"
import { api } from "@/lib/api"

// DEMO MODE: Set to true to simulate backend without API calls
const DEMO_MODE = true

// Demo response for mock streaming
const DEMO_RESPONSE = {
  answer: `AIForge is a production-ready Python AI SaaS boilerplate designed to help developers ship AI-powered products in days, not months. Here's what makes it powerful:

**Core Features:**
- **RAG Pipeline**: Complete document ingestion, chunking, and retrieval with citation tracking using pgvector and LangChain
- **Agent Framework**: LangGraph-based modular agent system with tool calling and multi-step reasoning
- **WhatsApp Integration**: Full WhatsApp Business API integration for AI-powered messaging
- **Multi-tenant Architecture**: Built-in tenant isolation with Supabase Row Level Security

**Tech Stack:**
- Backend: FastAPI (Python 3.12+)
- Frontend: Next.js 15 + TypeScript + shadcn/ui
- Database: Supabase (PostgreSQL + pgvector)
- AI: OpenAI, Anthropic, Ollama support

The boilerplate is perfect for building AI SaaS products like chatbots, document analysis tools, or AI-powered customer support systems.`,
  sources: [
    {
      content:
        "AIForge provides a complete RAG (Retrieval-Augmented Generation) pipeline with PDF, Markdown, and text ingestion capabilities. The system uses smart chunking strategies and pgvector for efficient similarity search.",
      metadata: {
        document: "features.md",
        section: "RAG Pipeline",
      },
      score: 0.92,
    },
    {
      content:
        "The LangGraph agent framework enables modular agent systems with custom tool registration, stateful conversations, and event streaming. Supports multiple LLM providers including OpenAI, Anthropic, and local models via Ollama.",
      metadata: {
        document: "architecture.md",
        section: "Agent Framework",
      },
      score: 0.88,
    },
    {
      content:
        "Built with multi-tenancy in mind, AIForge uses Supabase Row Level Security to ensure complete data isolation between tenants. Every query and operation is automatically scoped to the authenticated user's organization.",
      metadata: {
        document: "security.md",
        section: "Multi-tenant Architecture",
      },
      score: 0.85,
    },
  ],
}

export default function ChatPage() {
  const [messages, setMessages] = React.useState<MessageProps[]>([])
  const [isLoading, setIsLoading] = React.useState(false)
  const [documents, setDocuments] = React.useState<UploadedDocument[]>([])
  const [isSidebarCollapsed, setIsSidebarCollapsed] = React.useState(false)

  const handleSendMessage = async (message: string) => {
    // Add user message
    const userMessage: MessageProps = {
      role: "user",
      content: message,
    }
    setMessages((prev) => [...prev, userMessage])
    setIsLoading(true)

    if (DEMO_MODE) {
      // Demo mode: simulate streaming
      await simulateStreaming(message)
    } else {
      // Real API call
      try {
        const stream = api.rag.chat(message, { stream: true }) as AsyncGenerator<
          any,
          void,
          unknown
        >

        let fullResponse = ""
        let sources: any[] = []

        // Add empty assistant message for streaming
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: "",
            isStreaming: true,
          },
        ])

        for await (const chunk of stream) {
          if (typeof chunk === "string") {
            fullResponse += chunk
          } else if (chunk.token) {
            fullResponse += chunk.token
          } else if (chunk.sources) {
            sources = chunk.sources
          }

          // Update the last message with streaming content
          setMessages((prev) => {
            const newMessages = [...prev]
            const lastMessage = newMessages[newMessages.length - 1]
            if (lastMessage.role === "assistant") {
              lastMessage.content = fullResponse
              lastMessage.sources = sources.length > 0 ? sources : undefined
            }
            return newMessages
          })
        }

        // Finalize message (remove streaming indicator)
        setMessages((prev) => {
          const newMessages = [...prev]
          const lastMessage = newMessages[newMessages.length - 1]
          if (lastMessage.role === "assistant") {
            lastMessage.isStreaming = false
          }
          return newMessages
        })
      } catch (error) {
        console.error("Chat error:", error)
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: "Sorry, I encountered an error. Please try again.",
          },
        ])
      }
    }

    setIsLoading(false)
  }

  const simulateStreaming = async (userMessage: string) => {
    // Add empty assistant message
    setMessages((prev) => [
      ...prev,
      {
        role: "assistant",
        content: "",
        isStreaming: true,
      },
    ])

    // Simulate word-by-word streaming
    const words = DEMO_RESPONSE.answer.split(" ")
    let currentContent = ""

    for (let i = 0; i < words.length; i++) {
      currentContent += (i > 0 ? " " : "") + words[i]

      await new Promise((resolve) => setTimeout(resolve, 30)) // 30ms delay per word

      setMessages((prev) => {
        const newMessages = [...prev]
        const lastMessage = newMessages[newMessages.length - 1]
        if (lastMessage.role === "assistant") {
          lastMessage.content = currentContent
        }
        return newMessages
      })
    }

    // Add sources after streaming completes
    setMessages((prev) => {
      const newMessages = [...prev]
      const lastMessage = newMessages[newMessages.length - 1]
      if (lastMessage.role === "assistant") {
        lastMessage.isStreaming = false
        lastMessage.sources = DEMO_RESPONSE.sources
      }
      return newMessages
    })
  }

  const handleUpload = async (files: FileList) => {
    const newDocuments: UploadedDocument[] = Array.from(files).map((file) => ({
      id: Math.random().toString(36).substr(2, 9),
      name: file.name,
      status: "uploading",
      size: formatFileSize(file.size),
    }))

    setDocuments((prev) => [...prev, ...newDocuments])

    if (DEMO_MODE) {
      // Demo mode: simulate upload
      for (const doc of newDocuments) {
        await new Promise((resolve) => setTimeout(resolve, 1000))
        setDocuments((prev) =>
          prev.map((d) =>
            d.id === doc.id ? { ...d, status: "processing" as const } : d
          )
        )
        await new Promise((resolve) => setTimeout(resolve, 1500))
        setDocuments((prev) =>
          prev.map((d) => (d.id === doc.id ? { ...d, status: "ready" as const } : d))
        )
      }
    } else {
      // Real API upload
      for (let i = 0; i < files.length; i++) {
        const doc = newDocuments[i]
        try {
          await api.rag.ingest({ file: files[i] })
          setDocuments((prev) =>
            prev.map((d) => (d.id === doc.id ? { ...d, status: "ready" as const } : d))
          )
        } catch (error) {
          console.error("Upload error:", error)
          setDocuments((prev) =>
            prev.map((d) => (d.id === doc.id ? { ...d, status: "error" as const } : d))
          )
        }
      }
    }
  }

  const handleRemoveDocument = (id: string) => {
    setDocuments((prev) => prev.filter((d) => d.id !== id))
  }

  const handleNewChat = () => {
    setMessages([])
  }

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      {/* Mobile sidebar toggle */}
      {isSidebarCollapsed && (
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setIsSidebarCollapsed(false)}
          className="lg:hidden fixed top-4 left-4 z-50 size-10 shadow-lg"
        >
          <Menu className="size-5" />
        </Button>
      )}

      {/* Sidebar */}
      <div
        className={`${
          isSidebarCollapsed ? "hidden lg:flex" : "flex"
        } flex-shrink-0 fixed lg:static inset-y-0 left-0 z-40 lg:z-0 shadow-lg lg:shadow-none`}
      >
        <ChatSidebar
          documents={documents}
          onUpload={handleUpload}
          onNewChat={handleNewChat}
          onRemoveDocument={handleRemoveDocument}
          isCollapsed={false}
          onToggleCollapse={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
        />
      </div>

      {/* Overlay for mobile when sidebar is open */}
      {!isSidebarCollapsed && (
        <div
          className="lg:hidden fixed inset-0 bg-background/80 backdrop-blur-sm z-30"
          onClick={() => setIsSidebarCollapsed(true)}
        />
      )}

      {/* Main chat area */}
      <div className="flex-1 flex flex-col h-full min-w-0">
        {/* Header */}
        <div className="border-b bg-card px-4 sm:px-6 py-3 sm:py-4 flex items-center justify-between">
          <div>
            <h1 className="text-base sm:text-lg font-semibold">AIForge Chat</h1>
            <p className="text-xs text-muted-foreground hidden sm:block">
              Powered by RAG + GPT-4o
            </p>
          </div>
          <Button variant="outline" size="sm" className="gap-2 hidden sm:flex">
            GPT-4o
            <ChevronDown className="size-3" />
          </Button>
        </div>

        {/* Messages */}
        <ChatMessages messages={messages} />

        {/* Input */}
        <div className="border-t bg-card p-3 sm:p-4">
          <div className="max-w-4xl mx-auto">
            <ChatInput
              onSend={handleSendMessage}
              isLoading={isLoading}
              placeholder="Ask me anything about your documents..."
            />
          </div>
        </div>
      </div>
    </div>
  )
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return bytes + " B"
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB"
  return (bytes / (1024 * 1024)).toFixed(1) + " MB"
}
