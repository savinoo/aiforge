# Chat Components

Professional chat interface components for AIForge with RAG integration, streaming support, and citation tracking.

## Components

### ChatMessage
Individual message bubble with support for user/assistant roles, streaming indicators, and inline citations.

**Props:**
- `role`: "user" | "assistant"
- `content`: string
- `sources`: Source[] (optional)
- `isStreaming`: boolean (optional)

### ChatMessages
Scrollable message container with empty state and auto-scroll behavior.

**Props:**
- `messages`: MessageProps[]

### ChatInput
Auto-resizing textarea with keyboard shortcuts (Enter to send, Shift+Enter for new line).

**Props:**
- `onSend`: (message: string) => void
- `isLoading`: boolean
- `disabled`: boolean
- `placeholder`: string

### ChatSidebar
Sidebar with document upload (drag & drop + file picker), document list with status indicators, and navigation.

**Props:**
- `documents`: UploadedDocument[]
- `onUpload`: (files: FileList) => void
- `onNewChat`: () => void
- `onRemoveDocument`: (id: string) => void
- `isCollapsed`: boolean
- `onToggleCollapse`: () => void

### ChatCitations
Expandable citation panel showing source chunks with metadata and similarity scores.

**Props:**
- `sources`: Source[]

## Features

- **Streaming Support**: Token-by-token streaming with blinking cursor
- **Citation Tracking**: Expandable source panels with relevance scores
- **Document Upload**: Drag & drop + file picker with status tracking
- **Responsive Design**: Mobile-first with collapsible sidebar
- **Dark Mode**: Full dark mode support via Tailwind
- **Animations**: Smooth fade-in, slide-in, and typing indicators

## Usage

```tsx
import { ChatMessages } from "@/components/chat/chat-messages"
import { ChatInput } from "@/components/chat/chat-input"
import { ChatSidebar } from "@/components/chat/chat-sidebar"

function ChatPage() {
  const [messages, setMessages] = useState([])

  const handleSend = async (message: string) => {
    // Add user message
    setMessages(prev => [...prev, { role: "user", content: message }])

    // Stream AI response
    const stream = api.rag.chat(message, { stream: true })
    // ... handle streaming
  }

  return (
    <div className="flex h-screen">
      <ChatSidebar {...sidebarProps} />
      <div className="flex-1 flex flex-col">
        <ChatMessages messages={messages} />
        <ChatInput onSend={handleSend} />
      </div>
    </div>
  )
}
```

## Demo Mode

The chat page includes a `DEMO_MODE` constant for testing without a backend:
- Simulates word-by-word streaming
- Mock document upload with status progression
- Hardcoded demo response with citations

Perfect for screenshots and demos.
