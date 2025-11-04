"use client"
import type { Envelope, FilterState } from "@/lib/types"

interface FilterPanelProps {
  envelope: Envelope
  filters: FilterState
  onFilterChange: (filters: FilterState) => void
}

export function FilterPanel({ envelope, filters, onFilterChange }: FilterPanelProps) {
  const types = Array.from(new Set(envelope.nodes.map((n) => n.type || "untyped")))
  const relTypes = Array.from(new Set(envelope.edges.map((e) => e.rel_type)))

  const handleTextChange = (text: string) => {
    onFilterChange({ ...filters, textFilter: text })
  }

  const handleTypeToggle = (type: string) => {
    const newTypes = new Set(filters.selectedTypes)
    if (newTypes.has(type)) {
      newTypes.delete(type)
    } else {
      newTypes.add(type)
    }
    onFilterChange({ ...filters, selectedTypes: newTypes })
  }

  const handleRelTypeToggle = (relType: string) => {
    const newRelTypes = new Set(filters.selectedRelTypes)
    if (newRelTypes.has(relType)) {
      newRelTypes.delete(relType)
    } else {
      newRelTypes.add(relType)
    }
    onFilterChange({ ...filters, selectedRelTypes: newRelTypes })
  }

  const handleWeightChange = (weight: number) => {
    onFilterChange({ ...filters, minWeight: weight })
  }

  const maxWeight = Math.max(0, ...envelope.edges.map((e) => e.weight ?? 0))

  return (
    <div className="border border-border rounded-lg p-4 bg-card space-y-4">
      <h2 className="font-semibold text-lg">Filters</h2>

      {/* Text filter */}
      <div>
        <label className="text-sm font-medium text-foreground">Label</label>
        <input
          type="text"
          value={filters.textFilter}
          onChange={(e) => handleTextChange(e.target.value)}
          placeholder="Filter by label..."
          className="w-full mt-1 px-2 py-1 border border-border rounded bg-background text-foreground text-sm"
        />
      </div>

      {/* Type filter */}
      {types.length > 0 && (
        <div>
          <label className="text-sm font-medium text-foreground block mb-2">Node Type</label>
          <div className="space-y-1 max-h-32 overflow-y-auto">
            {types.map((type) => (
              <label key={type} className="flex items-center gap-2 cursor-pointer text-sm">
                <input
                  type="checkbox"
                  checked={filters.selectedTypes.has(type)}
                  onChange={() => handleTypeToggle(type)}
                  className="w-4 h-4"
                />
                <span>{type}</span>
              </label>
            ))}
          </div>
        </div>
      )}

      {/* Rel type filter */}
      {relTypes.length > 0 && (
        <div>
          <label className="text-sm font-medium text-foreground block mb-2">Relation Type</label>
          <div className="space-y-1 max-h-32 overflow-y-auto">
            {relTypes.map((relType) => (
              <label key={relType} className="flex items-center gap-2 cursor-pointer text-sm">
                <input
                  type="checkbox"
                  checked={filters.selectedRelTypes.has(relType)}
                  onChange={() => handleRelTypeToggle(relType)}
                  className="w-4 h-4"
                />
                <span>{relType}</span>
              </label>
            ))}
          </div>
        </div>
      )}

      {/* Weight filter */}
      {maxWeight > 0 && (
        <div>
          <label className="text-sm font-medium text-foreground flex justify-between">
            <span>Min Weight</span>
            <span className="font-mono text-xs text-muted-foreground">{filters.minWeight.toFixed(2)}</span>
          </label>
          <input
            type="range"
            min="0"
            max={maxWeight}
            step="0.01"
            value={filters.minWeight}
            onChange={(e) => handleWeightChange(Number.parseFloat(e.target.value))}
            className="w-full mt-1"
          />
        </div>
      )}
    </div>
  )
}
