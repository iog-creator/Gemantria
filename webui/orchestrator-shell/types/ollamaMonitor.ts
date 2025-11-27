/** TypeScript types for Ollama Monitor */

export type OllamaEndpoint = "generate" | "chat" | "embeddings" | "raw";

export interface OllamaRequestLog {
  id: string;
  timestamp: string; // ISO string
  endpoint: OllamaEndpoint;
  method: "POST" | "GET";
  model?: string | null;
  promptPreview?: string | null;
  inputTokens?: number | null;
  outputTokens?: number | null;
  durationMs?: number | null;
  status: "pending" | "success" | "error";
  httpStatus?: number | null;
  errorMessage?: string | null;
}

export interface OllamaMonitorSnapshot {
  lastUpdated: string;
  activeRequests: OllamaRequestLog[];
  recentRequests: OllamaRequestLog[];
}

