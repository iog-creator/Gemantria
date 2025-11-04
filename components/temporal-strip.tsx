"use client"
import type { Envelope, SelectedItems } from "@/lib/types"

interface TemporalStripProps {
  envelope: Envelope
  selection: SelectedItems
}

export function TemporalStrip({ envelope, selection }: TemporalStripProps) {
  return (
    <div className="w-full h-full p-4 flex flex-col justify-center bg-card">
      <div className="space-y-2">
        <h3 className="text-sm font-semibold text-foreground">Timeline</h3>

        {envelope.meta.created_at ? (
          <div className="flex items-center gap-2">
            <div className="flex-1 bg-background rounded h-8 flex items-center px-3 relative overflow-hidden">
              {/* Timeline bar background */}
              <div className="absolute inset-0 bg-gradient-to-r from-primary/20 via-primary/40 to-primary/20"></div>

              {/* Timeline marker */}
              <div className="absolute left-1/2 transform -translate-x-1/2 w-1 h-full bg-primary"></div>

              {/* Timeline label */}
              <div className="relative z-10 text-xs text-muted-foreground">
                Snapshot: {new Date(envelope.meta.created_at).toLocaleString()}
              </div>
            </div>
          </div>
        ) : (
          <div className="text-xs text-muted-foreground italic">No timeline data</div>
        )}

        {selection.nodeIds.size > 0 && (
          <div className="text-xs text-muted-foreground mt-2">
            {selection.nodeIds.size} node{selection.nodeIds.size !== 1 ? "s" : ""} selected
          </div>
        )}
      </div>
    </div>
  )
}
