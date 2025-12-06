// Phase-9 envelope types (minimal for P10-B)

export interface EnvelopeNode {
  id: string;
  label: string;
  type?: string;
  attrs?: Record<string, any>;
}

export interface EnvelopeEdge {
  src: string;
  dst: string;
  rel_type: string;
  [key: string]: any;
}

export interface EnvelopeMeta {
  version: string;
  source: string;
  snapshot_path: string;
  seed: number;
  created_at: string;
}

export interface Envelope {
  meta: EnvelopeMeta;
  nodes: EnvelopeNode[];
  edges: EnvelopeEdge[];
}
