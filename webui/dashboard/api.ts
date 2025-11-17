// webui/dashboard/api.ts
// API helpers for orchestrator dashboard

export interface SystemStatusSnapshot {
  level: 'OK' | 'WARN' | 'ERROR';
  dbMode: string; // e.g. "ready" | "db_off" | "partial"
  lmMode: string; // e.g. "lm_ready" | "lm_off" | "degraded"
  headline: string;
  details: string;
}

export interface LmIndicatorSnapshot {
  status: string; // offline/healthy/degraded
  reason?: string;
  generated_at?: string;
  success_rate?: number;
  error_rate?: number;
  total_calls?: number;
  db_off?: boolean;
  top_error_reason?: string;
  window_days?: number;
}

export interface ComplianceHeadSnapshot {
  generated_at: string;
  latest_agent_run?: {
    id: string | null;
    created_at: string | null;
  } | null;
  windows?: {
    '7d'?: {
      runs?: number;
      por_ok_ratio?: number;
      schema_ok_ratio?: number;
      provenance_ok_ratio?: number;
    };
    '30d'?: {
      runs?: number;
      por_ok_ratio?: number;
      schema_ok_ratio?: number;
      provenance_ok_ratio?: number;
    };
  };
}

export interface KbDocsHeadSnapshot {
  generated_at: string;
  docs?: any[];
  schema?: string;
  ok?: boolean;
  db_off?: boolean;
  connection_ok?: boolean;
  error?: string;
}

export interface OrchestratorDashboardSnapshot {
  system: SystemStatusSnapshot | null;
  lm: LmIndicatorSnapshot | null;
  compliance: ComplianceHeadSnapshot | null;
  kb: KbDocsHeadSnapshot | null;
  lastUpdated: string;
}

async function fetchSystemStatus(): Promise<SystemStatusSnapshot | null> {
  try {
    const response = await fetch('/api/status/system');
    if (!response.ok) {
      return null;
    }
    const data = await response.json();

    // Also fetch explanation for level/headline/details
    let explanation = null;
    try {
      const explainResponse = await fetch('/api/status/explain');
      if (explainResponse.ok) {
        explanation = await explainResponse.json();
      }
    } catch (e) {
      // Explanation is optional
    }

    // Determine LM mode from slots
    const lmSlots = data.lm?.slots || [];
    const okSlots = lmSlots.filter((s: any) => s.service === 'OK').length;
    const totalSlots = lmSlots.length;
    let lmMode = 'lm_off';
    if (okSlots === totalSlots && totalSlots > 0) {
      lmMode = 'lm_ready';
    } else if (okSlots > 0) {
      lmMode = 'degraded';
    }

    return {
      level: (explanation?.level as 'OK' | 'WARN' | 'ERROR') || 'OK',
      dbMode: data.db?.mode || 'db_off',
      lmMode,
      headline: explanation?.headline || 'System status summary',
      details: explanation?.details || 'No details available',
    };
  } catch (e) {
    return null;
  }
}

async function fetchLmIndicator(): Promise<LmIndicatorSnapshot | null> {
  try {
    const response = await fetch('/api/lm/indicator');
    if (!response.ok) {
      return null;
    }
    const data = await response.json();
    return data.snapshot || null;
  } catch (e) {
    return null;
  }
}

async function fetchComplianceHead(): Promise<ComplianceHeadSnapshot | null> {
  try {
    const response = await fetch('/api/compliance/head');
    if (!response.ok) {
      return null;
    }
    const data = await response.json();
    if (data.ok && data.snapshot) {
      return data.snapshot;
    }
    return null;
  } catch (e) {
    return null;
  }
}

async function fetchKbDocsHead(): Promise<KbDocsHeadSnapshot | null> {
  try {
    const response = await fetch('/api/kb/docs_head');
    if (!response.ok) {
      return null;
    }
    const data = await response.json();
    if (data.ok && data.snapshot) {
      return data.snapshot;
    }
    return null;
  } catch (e) {
    return null;
  }
}

export async function fetchOrchestratorSnapshot(): Promise<OrchestratorDashboardSnapshot> {
  // Fetch all endpoints in parallel
  const [system, lm, compliance, kb] = await Promise.all([
    fetchSystemStatus(),
    fetchLmIndicator(),
    fetchComplianceHead(),
    fetchKbDocsHead(),
  ]);

  return {
    system,
    lm,
    compliance,
    kb,
    lastUpdated: new Date().toISOString(),
  };
}

