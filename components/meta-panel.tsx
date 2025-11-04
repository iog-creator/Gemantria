"use client"
import type { Envelope } from "@/lib/types"

interface MetaPanelProps {
  meta: Envelope["meta"]
}

export function MetaPanel({ meta }: MetaPanelProps) {
  return (
    <div className="border border-border rounded-lg p-4 bg-card">
      <h2 className="font-semibold text-lg mb-3">Metadata</h2>
      <div className="space-y-2 text-sm">
        <div>
          <span className="text-muted-foreground">Version:</span>
          <span className="ml-2 font-mono text-foreground">{meta.version}</span>
        </div>
        <div>
          <span className="text-muted-foreground">Source:</span>
          <span className="ml-2 font-mono text-foreground">{meta.source}</span>
        </div>
        <div>
          <span className="text-muted-foreground">Snapshot:</span>
          <span className="ml-2 font-mono text-foreground text-xs break-all">{meta.snapshot_path}</span>
        </div>
        <div>
          <span className="text-muted-foreground">Seed:</span>
          <span className="ml-2 font-mono text-foreground">{meta.seed}</span>
        </div>
        {meta.created_at && (
          <div>
            <span className="text-muted-foreground">Created:</span>
            <span className="ml-2 font-mono text-foreground text-xs">{new Date(meta.created_at).toLocaleString()}</span>
          </div>
        )}
      </div>
    </div>
  )
}
