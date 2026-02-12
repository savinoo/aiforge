# AIForge Chat Interface

Professional chat interface built for AIForge with RAG integration, streaming, and citations.

## Features

### ✨ Core Capabilities
- **Real-time Streaming**: Token-by-token AI responses with typing indicators
- **RAG Integration**: Document upload with chunking and vector search
- **Citation Tracking**: Expandable source panels with relevance scores
- **Multi-document Support**: Upload multiple PDFs, Markdown, TXT files
- **Conversation Management**: New chat button to start fresh conversations

### 🎨 UI/UX
- **Modern Design**: Clean, ChatGPT-inspired interface
- **Dark Mode**: Full dark mode support
- **Responsive**: Mobile-first design with collapsible sidebar
- **Smooth Animations**: Fade-in, slide-in, typing indicators
- **Empty State**: Welcoming hero with suggested questions
- **Status Indicators**: Upload progress, processing states

### 📱 Mobile Support
- Collapsible sidebar with overlay
- Touch-friendly controls
- Optimized layouts for small screens

### 🔧 Demo Mode
Set `DEMO_MODE = true` in `/app/chat/page.tsx` for:
- Simulated streaming (no backend required)
- Mock document uploads
- Hardcoded citations and sources

Perfect for screenshots and demos.

## Components

### UI Components (src/components/ui/)
- `avatar.tsx` - User/AI avatars
- `badge.tsx` - Citation badges, status indicators
- `textarea.tsx` - Auto-resizing input with keyboard shortcuts
- `scroll-area.tsx` - Styled scrollable container

### Chat Components (src/components/chat/)
- `chat-message.tsx` - Message bubble with citations
- `chat-messages.tsx` - Scrollable message list with empty state
- `chat-input.tsx` - Input area with Enter/Shift+Enter support
- `chat-sidebar.tsx` - Document upload and navigation
- `chat-citations.tsx` - Expandable source panel

## Usage

### Development
```bash
cd frontend
npm run dev
```

Navigate to `http://localhost:3000/chat`

### Demo Mode (for screenshots)
1. Open `src/app/chat/page.tsx`
2. Ensure `DEMO_MODE = true` (already set)
3. Start dev server
4. Upload mock documents, send messages
5. Everything works without backend!

### Production (with backend)
1. Set `DEMO_MODE = false`
2. Ensure FastAPI backend is running on `localhost:8000`
3. Upload real documents
4. Chat with RAG-powered AI

## API Integration

The chat page uses the existing `api.rag.chat()` client with streaming:

```typescript
const stream = api.rag.chat(message, { stream: true })

for await (const chunk of stream) {
  // Handle streaming tokens
  if (chunk.token) {
    fullResponse += chunk.token
  }
  // Handle sources when stream completes
  if (chunk.sources) {
    sources = chunk.sources
  }
}
```

## Keyboard Shortcuts
- **Enter**: Send message
- **Shift + Enter**: New line in message

## Status Indicators
- 🔵 **Uploading**: File being uploaded
- 🔄 **Processing**: Document being chunked and indexed
- ✅ **Ready**: Document available for RAG
- ❌ **Error**: Upload or processing failed

## Styling

Built with:
- **Tailwind CSS v4**: Utility-first styling
- **shadcn/ui**: Component primitives
- **Geist Fonts**: Sans + Mono for code
- **oklch Colors**: Modern color space with dark mode

All colors use CSS variables defined in `globals.css` for easy theming.

## Future Enhancements (optional)
- [ ] Model selector dropdown (GPT-4, Claude, Ollama)
- [ ] Chat history in sidebar
- [ ] Export conversations
- [ ] Regenerate responses
- [ ] Copy code blocks
- [ ] Multi-language support
