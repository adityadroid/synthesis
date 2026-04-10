/* eslint-disable @typescript-eslint/no-explicit-any */
export const API_BASE_URL = "http://localhost:8000/api";

// Types
export interface User {
  id: string;
  email: string;
  full_name: string | null;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export type MessageRole = "user" | "assistant" | "system";

export interface Message {
  id: string;
  role: MessageRole;
  content: string;
  token_count: number | null;
  created_at: string;
}

export interface Conversation {
  id: string;
  title: string | null;
  model: string | null;
  created_at: string;
  updated_at: string;
}

export interface ChatResponse {
  message: Message;
  conversation: Conversation;
}

export interface StreamChunk {
  content: string;
  done: boolean;
}

// Auth helpers
const ACCESS_TOKEN_KEY = "access_token";
const REFRESH_TOKEN_KEY = "refresh_token";

export function getAccessToken(): string | null {
  return localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function setTokens(accessToken: string, refreshToken: string): void {
  localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
  localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
}

export function clearTokens(): void {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
}

// API client
class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private getHeaders(): HeadersInit {
    const token = getAccessToken();
    const headers: HeadersInit = {
      "Content-Type": "application/json",
    };
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
    return headers;
  }

  async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers: {
        ...this.getHeaders(),
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: "Request failed" }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
  }

  // Auth endpoints
  async signup(email: string, password: string, fullName?: string): Promise<User> {
    return this.request<User>("/auth/signup", {
      method: "POST",
      body: JSON.stringify({ email, password, full_name: fullName }),
    });
  }

  async login(email: string, password: string): Promise<TokenResponse> {
    return this.request<TokenResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
  }

  async logout(): Promise<void> {
    // Just clear local tokens - server doesn't need to do anything for JWT
  }

  async refreshToken(refreshToken: string): Promise<TokenResponse> {
    return this.request<TokenResponse>("/auth/refresh", {
      method: "POST",
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
  }

  // User endpoints
  async getCurrentUser(): Promise<User> {
    return this.request<User>("/users/me");
  }

  // Chat endpoints
  async sendMessage(message: string, conversationId?: string): Promise<ChatResponse> {
    return this.request<ChatResponse>("/chat/send", {
      method: "POST",
      body: JSON.stringify({ message, conversation_id: conversationId }),
    });
  }

  async getConversations(): Promise<Conversation[]> {
    return this.request<Conversation[]>("/chat/conversations");
  }

  async getMessages(conversationId: string): Promise<Message[]> {
    return this.request<Message[]>(`/chat/conversations/${conversationId}/messages`);
  }

  // Streaming
  async *streamMessage(conversationId: string, message: string): AsyncGenerator<StreamChunk> {
    const response = await fetch(`${this.baseUrl}/chat/stream/${conversationId}`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify({ message }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: "Stream failed" }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    const reader = response.body?.getReader();
    if (!reader) throw new Error("No response body");

    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() || "";

      for (const line of lines) {
        if (line.startsWith("data: ")) {
          try {
            const chunk: StreamChunk = JSON.parse(line.slice(6));
            yield chunk;
            if (chunk.done) return;
          } catch {
            // Skip invalid JSON
          }
        }
      }
    }
  }
}

export const api = new ApiClient(API_BASE_URL);