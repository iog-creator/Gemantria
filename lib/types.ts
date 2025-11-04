export type Envelope = {
  meta: {
    version: string
    source: string
    snapshot_path: string
    seed: number
    created_at?: string
  }
  nodes: Array<{
    id: string
    label: string
    type?: string
    attrs?: Record<string, unknown>
  }>
  edges: Array<{
    src: string
    dst: string
    rel_type: string
    weight?: number
  }>
}

export type FilterState = {
  textFilter: string
  selectedTypes: Set<string>
  selectedRelTypes: Set<string>
  minWeight: number
}

export type SelectedItems = {
  nodeIds: Set<string>
  edgeIds: Set<string>
}
