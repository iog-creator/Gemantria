"use client"

import React, { useState, useCallback } from "react"
import type { Envelope, FilterState, SelectedItems } from "@/lib/types"
import { FileProvider, DevHTTPProvider } from "@/lib/providers"
import { EventBus } from "@/lib/events"
import { Toolbar } from "@/components/toolbar"
import { MetaPanel } from "@/components/meta-panel"
import { CountsPanel } from "@/components/counts-panel"
import { GraphPreview } from "@/components/graph-preview"
import { TemporalStrip } from "@/components/temporal-strip"
import { FilterPanel } from "@/components/filter-panel"

const eventBus = new EventBus()

export default function Dashboard() {
  const [envelope, setEnvelope] = useState<Envelope | null>(null)
  const [filters, setFilters] = useState<FilterState>({
    textFilter: "",
    selectedTypes: new Set(),
    selectedRelTypes: new Set(),
    minWeight: 0,
  })
  const [selection, setSelection] = useState<SelectedItems>({
    nodeIds: new Set(),
    edgeIds: new Set(),
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleLoadFile = useCallback(async (file?: File) => {
    setLoading(true)
    setError(null)
    try {
      let provider
      if (file) {
        provider = new FileProvider(file)
      } else {
        provider = new DevHTTPProvider("/envelope.json")
      }
      const data = await provider.load()
      setEnvelope(data)
      eventBus.emit("envelopeLoaded", {
        nodeCount: data.nodes.length,
        edgeCount: data.edges.length,
        meta: data.meta,
      })
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to load envelope"
      setError(message)
      console.error("[v0] Load error:", message)
    } finally {
      setLoading(false)
    }
  }, [])

  React.useEffect(() => {
    // Empty - user must explicitly upload file or load dev envelope
  }, [])

  const handleFilterChange = useCallback((newFilters: FilterState) => {
    setFilters(newFilters)
    eventBus.emit("filterChanged", newFilters)
  }, [])

  const handleSelectionChange = useCallback((nodeIds: Set<string>, edgeIds: Set<string>) => {
    setSelection({ nodeIds, edgeIds })
    eventBus.emit("selectionChanged", { nodeIds: Array.from(nodeIds), edgeIds: Array.from(edgeIds) })
  }, [])

  const filteredEnvelope = React.useMemo(() => {
    if (!envelope) return null

    let filteredNodes = envelope.nodes
    let filteredEdges = envelope.edges

    // Apply text filter
    if (filters.textFilter) {
      const lc = filters.textFilter.toLowerCase()
      filteredNodes = filteredNodes.filter((n) => n.label.toLowerCase().includes(lc))
    }

    // Apply type filter
    if (filters.selectedTypes.size > 0) {
      filteredNodes = filteredNodes.filter((n) => filters.selectedTypes.has(n.type || "untyped"))
    }

    // Apply rel_type filter
    if (filters.selectedRelTypes.size > 0) {
      filteredEdges = filteredEdges.filter((e) => filters.selectedRelTypes.has(e.rel_type))
    }

    // Apply weight filter
    filteredEdges = filteredEdges.filter((e) => (e.weight ?? 0) >= filters.minWeight)

    // Filter edges to only include those between filtered nodes
    const nodeIds = new Set(filteredNodes.map((n) => n.id))
    filteredEdges = filteredEdges.filter((e) => nodeIds.has(e.src) && nodeIds.has(e.dst))

    return { ...envelope, nodes: filteredNodes, edges: filteredEdges }
  }, [envelope, filters])

  return (
    <main className="h-screen w-screen flex flex-col bg-background text-foreground overflow-hidden">
      {/* Header */}
      <div className="border-b border-border p-4 bg-card">
        <h1 className="text-2xl font-bold">Gemantria Envelope Viewer</h1>
        <p className="text-sm text-muted-foreground mt-1">Phase-9 ingestion visualization (local-only, no network)</p>
      </div>

      {/* Toolbar */}
      <Toolbar onLoadFile={handleLoadFile} loading={loading} />

      {/* Error display */}
      {error && (
        <div className="bg-destructive/10 border-b border-destructive p-4 text-destructive">
          <p className="font-semibold">Error loading envelope:</p>
          <p className="text-sm">{error}</p>
          <button
            onClick={() => handleLoadFile()}
            className="mt-2 px-3 py-1 bg-destructive text-destructive-foreground rounded hover:opacity-90 text-sm"
          >
            Try Dev Envelope
          </button>
        </div>
      )}

      {!envelope ? (
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center space-y-4">
            <div>
              <p className="text-lg font-semibold text-foreground mb-2">Welcome to Gemantria</p>
              <p className="text-muted-foreground mb-4 max-w-sm">
                Upload a Phase-9 envelope JSON file or load the development envelope to visualize your ingestion graph.
              </p>
            </div>
            <div className="flex gap-3 justify-center">
              <button
                onClick={() => document.querySelector('input[type="file"]')?.click?.()}
                className="px-6 py-2 bg-primary text-primary-foreground rounded font-medium hover:opacity-90"
              >
                Upload File
              </button>
              <button
                onClick={() => handleLoadFile()}
                disabled={loading}
                className="px-6 py-2 bg-secondary text-secondary-foreground rounded font-medium hover:opacity-90 disabled:opacity-50"
              >
                {loading ? "Loading..." : "Load Dev Envelope"}
              </button>
            </div>
            {!loading && <p className="text-xs text-muted-foreground/50 mt-4">No envelope loaded</p>}
          </div>
        </div>
      ) : (
        <div className="flex-1 flex gap-4 p-4 overflow-hidden">
          {/* Left sidebar: meta, counts, filters */}
          <div className="w-80 flex flex-col gap-4 overflow-y-auto border-r border-border pr-4">
            <MetaPanel meta={envelope.meta} />
            <CountsPanel envelope={filteredEnvelope} />
            <FilterPanel envelope={envelope} filters={filters} onFilterChange={handleFilterChange} />
          </div>

          {/* Center: graph and temporal */}
          <div className="flex-1 flex flex-col gap-4 overflow-hidden">
            <div className="flex-1 border border-border rounded-lg overflow-hidden bg-card">
              <GraphPreview
                envelope={filteredEnvelope}
                selection={selection}
                onSelectionChange={handleSelectionChange}
              />
            </div>
            <div className="h-24 border border-border rounded-lg overflow-hidden bg-card">
              <TemporalStrip envelope={envelope} selection={selection} />
            </div>
          </div>
        </div>
      )}

      {/* Hidden file input for upload */}
      <input
        type="file"
        accept=".json"
        onChange={(e) => {
          const file = e.target.files?.[0]
          if (file) handleLoadFile(file)
        }}
        style={{ display: "none" }}
      />
    </main>
  )
}
