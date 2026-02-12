/**
 * API client for communicating with the FastAPI backend
 * Handles authentication, streaming responses, and error handling
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface ApiError {
  detail: string;
  status?: number;
}

/**
 * Generic fetch wrapper with error handling
 */
async function apiFetch<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  const defaultHeaders: HeadersInit = {
    'Content-Type': 'application/json',
  };

  // Add auth token if available
  const token = typeof window !== 'undefined'
    ? localStorage.getItem('auth_token')
    : null;

  if (token) {
    defaultHeaders['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(url, {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error: ApiError = await response.json().catch(() => ({
      detail: 'An unknown error occurred',
      status: response.status,
    }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

/**
 * Stream handler for Server-Sent Events (SSE)
 */
async function* streamResponse(
  endpoint: string,
  options: RequestInit = {}
): AsyncGenerator<string, void, unknown> {
  const url = `${API_BASE_URL}${endpoint}`;

  const token = typeof window !== 'undefined'
    ? localStorage.getItem('auth_token')
    : null;

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(url, {
    ...options,
    headers: {
      ...headers,
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error: ApiError = await response.json().catch(() => ({
      detail: 'An unknown error occurred',
      status: response.status,
    }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  const reader = response.body?.getReader();
  if (!reader) {
    throw new Error('Response body is not readable');
  }

  const decoder = new TextDecoder();
  let buffer = '';

  try {
    while (true) {
      const { done, value } = await reader.read();

      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          if (data === '[DONE]') {
            return;
          }
          try {
            const parsed = JSON.parse(data);
            yield parsed;
          } catch {
            // If not JSON, yield raw data
            yield data;
          }
        }
      }
    }
  } finally {
    reader.releaseLock();
  }
}

/**
 * API endpoints
 */
export const api = {
  // Health check
  health: () => apiFetch<{ status: string }>('/health'),

  // RAG endpoints
  rag: {
    ingest: (data: { file: File; metadata?: Record<string, unknown> }) => {
      const formData = new FormData();
      formData.append('file', data.file);
      if (data.metadata) {
        formData.append('metadata', JSON.stringify(data.metadata));
      }
      return apiFetch<{ document_id: string }>('/api/v1/rag/ingest', {
        method: 'POST',
        body: formData,
        headers: {}, // Let browser set Content-Type for FormData
      });
    },

    chat: (query: string, options?: { stream?: boolean }) => {
      if (options?.stream) {
        return streamResponse('/api/v1/rag/chat', {
          method: 'POST',
          body: JSON.stringify({ query }),
        });
      }
      return apiFetch<{
        answer: string;
        sources: Array<{ content: string; metadata: Record<string, unknown> }>;
      }>('/api/v1/rag/chat', {
        method: 'POST',
        body: JSON.stringify({ query }),
      });
    },

    search: (query: string, limit = 5) =>
      apiFetch<Array<{ content: string; score: number; metadata: Record<string, unknown> }>>(
        `/api/v1/rag/search?query=${encodeURIComponent(query)}&limit=${limit}`
      ),
  },

  // Agent endpoints
  agents: {
    chat: (message: string, sessionId?: string, stream = false) => {
      if (stream) {
        return streamResponse('/api/v1/agents/chat', {
          method: 'POST',
          body: JSON.stringify({ message, session_id: sessionId }),
        });
      }
      return apiFetch<{
        response: string;
        session_id: string;
      }>('/api/v1/agents/chat', {
        method: 'POST',
        body: JSON.stringify({ message, session_id: sessionId }),
      });
    },

    history: (sessionId: string) =>
      apiFetch<Array<{ role: string; content: string }>>(`/api/v1/agents/history/${sessionId}`),
  },

  // WhatsApp endpoints
  whatsapp: {
    sendMessage: (to: string, message: string) =>
      apiFetch<{ message_id: string }>('/api/v1/whatsapp/send', {
        method: 'POST',
        body: JSON.stringify({ to, message }),
      }),

    sendMedia: (to: string, mediaUrl: string, caption?: string) =>
      apiFetch<{ message_id: string }>('/api/v1/whatsapp/send-media', {
        method: 'POST',
        body: JSON.stringify({ to, media_url: mediaUrl, caption }),
      }),
  },

  // Auth endpoints (Supabase integration)
  auth: {
    login: (email: string, password: string) =>
      apiFetch<{ token: string; user: Record<string, unknown> }>('/api/v1/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      }),

    signup: (email: string, password: string) =>
      apiFetch<{ token: string; user: Record<string, unknown> }>('/api/v1/auth/signup', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      }),

    logout: () =>
      apiFetch<{ success: boolean }>('/api/v1/auth/logout', {
        method: 'POST',
      }),
  },
};

// Utility to store/retrieve auth token
export const authUtils = {
  setToken: (token: string) => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('auth_token', token);
    }
  },

  getToken: () => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('auth_token');
    }
    return null;
  },

  clearToken: () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token');
    }
  },
};
