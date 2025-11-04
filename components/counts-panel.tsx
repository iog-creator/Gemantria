"use client"
import type { Envelope } from "@/lib/types"

interface CountsPanelProps {
  envelope: Envelope | null
}

export function CountsPanel({ envelope }: CountsPanelProps) {
  if (!envelope) return null

  const density =
    envelope.nodes.length > 0
      ? (envelope.edges.length / (envelope.nodes.length * (envelope.nodes.length - 1))).toFixed(4)
      : "0"

  return (
    <div className="border border-border rounded-lg p-4 bg-card">
      <h2 className="font-semibold text-lg mb-4">Metrics</h2>
      <div className="grid grid-cols-2 gap-3">
        <div className="bg-background rounded p-3">
          <p className="text-xs text-muted-foreground uppercase">Nodes</p>
          <p className="text-2xl font-bold text-primary">{envelope.nodes.length}</p>
        </div>
        <div className="bg-background rounded p-3">
          <p className="text-xs text-muted-foreground uppercase">Edges</p>
          <p className="text-2xl font-bold text-primary">{envelope.edges.length}</p>
        </div>
        <div className="bg-background rounded p-3 col-span-2">
          <p className="text-xs text-muted-foreground uppercase">Density</p>
          <p className="text-lg font-bold text-primary">{density}</p>
        </div>
      </div>
    </div>
  )
}
