"use client"

import * as React from "react"
import { ScrollArea } from "@/components/ui/scroll-area"
import { ChatMessage, type MessageProps } from "./chat-message"
import { Zap } from "lucide-react"

interface ChatMessagesProps {
  messages: MessageProps[]
}

export function ChatMessages({ messages }: ChatMessagesProps) {
  const scrollRef = React.useRef<HTMLDivElement>(null)

  React.useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages])

  if (messages.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-center px-4">
        <div className="mb-6 p-6 rounded-full bg-primary/10">
          <Zap className="size-12 text-primary" />
        </div>
        <h2 className="text-2xl font-semibold mb-2">Welcome to AIForge</h2>
        <p className="text-muted-foreground mb-8 max-w-md">
          Start a conversation or upload documents to get started with RAG-powered chat
        </p>
        <div className="grid gap-3 w-full max-w-2xl">
          <SuggestedQuestion>
            What can AIForge help me build?
          </SuggestedQuestion>
          <SuggestedQuestion>
            How does the RAG pipeline work?
          </SuggestedQuestion>
          <SuggestedQuestion>
            Tell me about the agent framework
          </SuggestedQuestion>
        </div>
      </div>
    )
  }

  return (
    <ScrollArea ref={scrollRef} className="flex-1 overflow-y-auto">
      <div className="flex flex-col">
        {messages.map((message, idx) => (
          <ChatMessage key={idx} {...message} />
        ))}
      </div>
    </ScrollArea>
  )
}

function SuggestedQuestion({ children }: { children: React.ReactNode }) {
  return (
    <button className="px-4 py-3 text-sm text-left border rounded-xl hover:bg-accent hover:border-primary transition-colors">
      {children}
    </button>
  )
}
