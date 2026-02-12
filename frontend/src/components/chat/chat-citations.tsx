"use client"

import * as React from "react"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent } from "@/components/ui/card"
import { FileText, ChevronDown, ChevronUp } from "lucide-react"
import { cn } from "@/lib/utils"
import type { Source } from "./chat-message"

interface ChatCitationsProps {
  sources: Source[]
}

export function ChatCitations({ sources }: ChatCitationsProps) {
  const [isExpanded, setIsExpanded] = React.useState(false)

  if (!sources || sources.length === 0) return null

  return (
    <div className="w-full">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex items-center gap-2 text-xs text-muted-foreground hover:text-foreground transition-colors"
      >
        <FileText className="size-3" />
        <span>{sources.length} source{sources.length !== 1 ? "s" : ""}</span>
        {isExpanded ? (
          <ChevronUp className="size-3" />
        ) : (
          <ChevronDown className="size-3" />
        )}
      </button>

      {isExpanded && (
        <div className="mt-2 space-y-2 animate-in fade-in slide-in-from-top-2 duration-200">
          {sources.map((source, idx) => (
            <Card key={idx} className="border-l-4 border-l-primary">
              <CardContent className="p-3">
                <div className="flex items-start justify-between gap-2 mb-2">
                  <Badge variant="outline" className="text-xs">
                    [{idx + 1}]
                  </Badge>
                  {source.score !== undefined && (
                    <span className="text-xs text-muted-foreground">
                      {(source.score * 100).toFixed(0)}% match
                    </span>
                  )}
                </div>
                <p className="text-xs text-muted-foreground leading-relaxed line-clamp-3">
                  {source.content}
                </p>
                {source.metadata && Object.keys(source.metadata).length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-1">
                    {Object.entries(source.metadata).map(([key, value]) => {
                      if (key === "document_id" || key === "chunk_index") return null
                      return (
                        <Badge key={key} variant="secondary" className="text-[10px] px-1.5 py-0">
                          {String(value)}
                        </Badge>
                      )
                    })}
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
