"use client"

import * as React from "react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card } from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"
import {
  Zap,
  Plus,
  Upload,
  FileText,
  CheckCircle2,
  Loader2,
  X,
  Home,
  Menu,
} from "lucide-react"
import { cn } from "@/lib/utils"
import Link from "next/link"

export interface UploadedDocument {
  id: string
  name: string
  status: "uploading" | "processing" | "ready" | "error"
  size?: string
}

interface ChatSidebarProps {
  documents: UploadedDocument[]
  onUpload: (files: FileList) => void
  onNewChat: () => void
  onRemoveDocument?: (id: string) => void
  isCollapsed?: boolean
  onToggleCollapse?: () => void
}

export function ChatSidebar({
  documents,
  onUpload,
  onNewChat,
  onRemoveDocument,
  isCollapsed = false,
  onToggleCollapse,
}: ChatSidebarProps) {
  const fileInputRef = React.useRef<HTMLInputElement>(null)
  const [isDragging, setIsDragging] = React.useState(false)

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = () => {
    setIsDragging(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    if (e.dataTransfer.files.length > 0) {
      onUpload(e.dataTransfer.files)
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      onUpload(e.target.files)
    }
  }

  if (isCollapsed) {
    return (
      <div className="w-16 border-r bg-card flex flex-col items-center py-4 gap-4">
        <Button
          variant="ghost"
          size="icon"
          onClick={onToggleCollapse}
          className="size-10"
        >
          <Menu className="size-5" />
        </Button>
        <Button variant="ghost" size="icon" onClick={onNewChat} className="size-10">
          <Plus className="size-5" />
        </Button>
        <Link href="/">
          <Button variant="ghost" size="icon" className="size-10">
            <Home className="size-5" />
          </Button>
        </Link>
      </div>
    )
  }

  return (
    <div className="w-80 border-r bg-card flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
          <Zap className="size-5 text-primary" />
          <span className="font-semibold text-lg">AIForge</span>
        </Link>
        {onToggleCollapse && (
          <Button
            variant="ghost"
            size="icon-sm"
            onClick={onToggleCollapse}
            className="lg:hidden"
          >
            <X className="size-4" />
          </Button>
        )}
      </div>

      {/* New Chat Button */}
      <div className="p-4">
        <Button onClick={onNewChat} className="w-full justify-start gap-2" size="lg">
          <Plus className="size-4" />
          New Chat
        </Button>
      </div>

      {/* Upload Area */}
      <div className="px-4 pb-4">
        <Card
          className={cn(
            "border-2 border-dashed transition-colors cursor-pointer hover:border-primary",
            isDragging && "border-primary bg-primary/5"
          )}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <div className="p-6 flex flex-col items-center justify-center text-center gap-2">
            <Upload className="size-8 text-muted-foreground" />
            <div>
              <p className="text-sm font-medium">Upload documents</p>
              <p className="text-xs text-muted-foreground">
                Drag & drop or click to browse
              </p>
            </div>
          </div>
        </Card>
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf,.txt,.md,.doc,.docx"
          onChange={handleFileSelect}
          className="hidden"
        />
      </div>

      {/* Documents List */}
      <div className="flex-1 overflow-hidden flex flex-col px-4">
        <h3 className="text-xs font-semibold text-muted-foreground mb-2 px-1">
          Documents ({documents.length})
        </h3>
        <ScrollArea className="flex-1">
          <div className="space-y-2 pr-2">
            {documents.map((doc) => (
              <DocumentItem
                key={doc.id}
                document={doc}
                onRemove={onRemoveDocument}
              />
            ))}
          </div>
        </ScrollArea>
      </div>

      {/* Footer */}
      <div className="p-4 border-t">
        <Link href="/">
          <Button variant="ghost" className="w-full justify-start gap-2" size="sm">
            <Home className="size-4" />
            Back to Home
          </Button>
        </Link>
      </div>
    </div>
  )
}

function DocumentItem({
  document,
  onRemove,
}: {
  document: UploadedDocument
  onRemove?: (id: string) => void
}) {
  const statusIcons = {
    uploading: <Loader2 className="size-3 animate-spin" />,
    processing: <Loader2 className="size-3 animate-spin" />,
    ready: <CheckCircle2 className="size-3 text-green-500" />,
    error: <X className="size-3 text-destructive" />,
  }

  const statusLabels = {
    uploading: "Uploading",
    processing: "Processing",
    ready: "Ready",
    error: "Error",
  }

  return (
    <div className="group flex items-start gap-2 p-2 rounded-lg hover:bg-accent transition-colors">
      <FileText className="size-4 text-muted-foreground mt-0.5 shrink-0" />
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium truncate">{document.name}</p>
        <div className="flex items-center gap-2 mt-1">
          <Badge
            variant={document.status === "error" ? "destructive" : "secondary"}
            className="text-[10px] px-1.5 py-0 flex items-center gap-1"
          >
            {statusIcons[document.status]}
            {statusLabels[document.status]}
          </Badge>
          {document.size && (
            <span className="text-[10px] text-muted-foreground">{document.size}</span>
          )}
        </div>
      </div>
      {onRemove && document.status !== "uploading" && (
        <Button
          variant="ghost"
          size="icon-xs"
          onClick={() => onRemove(document.id)}
          className="opacity-0 group-hover:opacity-100 transition-opacity"
        >
          <X className="size-3" />
        </Button>
      )}
    </div>
  )
}
