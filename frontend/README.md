# AIForge Frontend

Modern Next.js 15 frontend for AIForge, built with TypeScript, Tailwind CSS, and shadcn/ui.

## Features

- **Next.js 15** with App Router
- **TypeScript** for type safety
- **Tailwind CSS** for styling
- **shadcn/ui** for beautiful, accessible components
- **API Client** with streaming support for real-time AI responses
- **Responsive Design** optimized for desktop and mobile

## Getting Started

### Prerequisites

- Node.js 18+ and npm

### Installation

```bash
# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local
# Edit .env.local with your configuration
```

### Development

```bash
# Start the development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Build

```bash
# Create production build
npm run build

# Start production server
npm start
```

## Project Structure

```
src/
├── app/                    # Next.js App Router pages
│   ├── layout.tsx         # Root layout with metadata
│   ├── page.tsx           # Landing page
│   └── globals.css        # Global styles + Tailwind config
├── components/
│   └── ui/                # shadcn/ui components
├── lib/
│   ├── api.ts             # API client for backend communication
│   └── utils.ts           # Utility functions
└── ...
```

## API Client

The `src/lib/api.ts` file provides a complete API client for communicating with the FastAPI backend:

### Basic Usage

```typescript
import { api } from '@/lib/api';

// Health check
const health = await api.health();

// RAG chat
const response = await api.rag.chat('What is AIForge?');

// Streaming chat
for await (const chunk of api.rag.chat('Tell me more', { stream: true })) {
  console.log(chunk);
}

// Agent chat
const agentResponse = await api.agents.chat('Hello, agent!');
```

### Authentication

```typescript
import { api, authUtils } from '@/lib/api';

// Login
const { token } = await api.auth.login('user@example.com', 'password');
authUtils.setToken(token);

// Logout
await api.auth.logout();
authUtils.clearToken();
```

### Streaming Responses

The API client supports Server-Sent Events (SSE) for real-time AI responses:

```typescript
// Example: Streaming RAG chat
async function streamChat(query: string) {
  for await (const chunk of api.rag.chat(query, { stream: true })) {
    // chunk contains incremental response data
    console.log(chunk);
  }
}
```

## Environment Variables

Create a `.env.local` file with:

```bash
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Supabase (optional, for client-side auth)
NEXT_PUBLIC_SUPABASE_URL=your-supabase-url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key
```

## Adding New Pages

To add a new page (e.g., dashboard):

```bash
# Create the page
mkdir -p src/app/dashboard
touch src/app/dashboard/page.tsx
```

Example page:

```typescript
export default function Dashboard() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold">Dashboard</h1>
    </div>
  );
}
```

## Adding shadcn/ui Components

```bash
# Add a new component
npx shadcn@latest add [component-name]

# Example: Add dialog component
npx shadcn@latest add dialog
```

## Deployment

### Vercel (Recommended)

1. Push your code to GitHub
2. Import the repository in Vercel
3. Set environment variables in Vercel dashboard
4. Deploy

### Other Platforms

```bash
# Build the app
npm run build

# The output will be in .next/
# Serve using Node.js or any static hosting
```

## Tech Stack

- **Framework:** Next.js 15
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **UI Components:** shadcn/ui
- **Icons:** lucide-react
- **HTTP Client:** Fetch API with streaming support

## Learn More

- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [shadcn/ui](https://ui.shadcn.com)
- [TypeScript](https://www.typescriptlang.org/docs)
