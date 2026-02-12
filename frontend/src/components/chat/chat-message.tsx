"use client"

import * as React from "react"
import { cn } from "@/lib/utils"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Bot, User } from "lucide-react"
import { ChatCitations } from "./chat-citations"

export interface Source {
  content: string
  metadata: Record<string, unknown>
  score?: number
}

export interface MessageProps {
  role: "user" | "assistant"
  content: string
  sources?: Source[]
  isStreaming?: boolean
  className?: string
}

export function ChatMessage({
  role,
  content,
  sources,
  isStreaming,
  className,
}: MessageProps) {
  const isUser = role === "user"

  return (
    <div
      className={cn(
        "group relative flex items-start gap-4 px-4 py-6",
        isUser ? "justify-end" : "justify-start",
        className
      )}
    >
      {!isUser && (
        <Avatar className="size-8 border">
          <AvatarFallback className="bg-primary text-primary-foreground">
            <Bot className="size-4" />
          </AvatarFallback>
        </Avatar>
      )}

      <div
        className={cn(
          "flex flex-col gap-2 max-w-[85%] sm:max-w-[75%]",
          isUser && "items-end"
        )}
      >
        <div
          className={cn(
            "rounded-2xl px-4 py-3 text-[15px] leading-relaxed",
            isUser
              ? "bg-primary text-primary-foreground rounded-tr-sm"
              : "bg-muted text-foreground rounded-tl-sm border shadow-sm"
          )}
        >
          <div className="whitespace-pre-wrap break-words">
            {content}
            {isStreaming && (
              <span className="inline-block w-1 h-4 ml-1 bg-current animate-pulse" />
            )}
          </div>
        </div>

        {!isUser && sources && sources.length > 0 && (
          <ChatCitations sources={sources} />
        )}
      </div>

      {isUser && (
        <Avatar className="size-8 border">
          <AvatarFallback className="bg-secondary">
            <User className="size-4" />
          </AvatarFallback>
        </Avatar>
      )}
    </div>
  )
}
