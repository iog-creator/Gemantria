// Type definitions for graph visualization data

export interface GraphNode {
  id: string;
  label: string;
  cluster?: number;
  degree?: number;
  betweenness?: number;
  eigenvector?: number;
  x?: number;
  y?: number;
  vx?: number;
  vy?: number;
  index?: number;
}

export interface GraphEdge {
  source: string | GraphNode;
  target: string | GraphNode;
  strength: number;
  rerank?: number;
  yes?: boolean;
  index?: number;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
  metadata?: {
    node_count: number;
    edge_count: number;
    cluster_count: number;
    export_timestamp: string;
  };
}

export interface NodeStats {
  id: string;
  label: string;
  cluster?: number;
  degree?: number;
  betweenness?: number;
  eigenvector?: number;
  connections: number;
}
