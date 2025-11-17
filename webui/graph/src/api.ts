// webui/graph/src/api.ts
// API helpers for graph dashboard orchestrator signals

export interface McpCatalogSummary {
  ok: boolean;
  endpoint_count: number | null;
  last_updated: string | null;
  error?: string | null;
}

export interface BrowserVerificationStatus {
  ok: boolean;
  status: "verified" | "partial" | "missing";
  verified_pages: number | null;
  error?: string | null;
}

export async function fetchMcpCatalogSummary(): Promise<McpCatalogSummary> {
  try {
    const response = await fetch("/api/mcp/catalog_summary");
    if (!response.ok) {
      return {
        ok: false,
        endpoint_count: null,
        last_updated: null,
        error: `HTTP ${response.status}: ${response.statusText}`,
      };
    }
    const data = await response.json();
    return data;
  } catch (e) {
    return {
      ok: false,
      endpoint_count: null,
      last_updated: null,
      error: e instanceof Error ? e.message : "Failed to fetch MCP catalog summary",
    };
  }
}

export async function fetchBrowserVerificationStatus(): Promise<BrowserVerificationStatus> {
  try {
    const response = await fetch("/api/atlas/browser_verification");
    if (!response.ok) {
      return {
        ok: false,
        status: "missing",
        verified_pages: null,
        error: `HTTP ${response.status}: ${response.statusText}`,
      };
    }
    const data = await response.json();
    return data;
  } catch (e) {
    return {
      ok: false,
      status: "missing",
      verified_pages: null,
      error: e instanceof Error ? e.message : "Failed to fetch browser verification status",
    };
  }
}

export interface GraphStatsSummary {
  ok: boolean;
  nodes: number | null;
  edges: number | null;
  clusters: number | null;
  density: number | null;
  error?: string | null;
}

export async function fetchGraphStatsSummary(): Promise<GraphStatsSummary> {
  try {
    const res = await fetch("/api/graph/stats_summary");
    if (!res.ok) {
      return {
        ok: false,
        nodes: null,
        edges: null,
        clusters: null,
        density: null,
        error: `HTTP ${res.status}`,
      };
    }
    const data = await res.json();
    return {
      ok: !!data.ok,
      nodes: data.nodes ?? null,
      edges: data.edges ?? null,
      clusters: data.clusters ?? null,
      density: data.density ?? null,
      error: data.error ?? null,
    };
  } catch (err: any) {
    return {
      ok: false,
      nodes: null,
      edges: null,
      clusters: null,
      density: null,
      error: err?.message ?? "Failed to load graph stats",
    };
  }
}

