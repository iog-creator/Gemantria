import { forceSimulation, forceManyBody, forceLink, forceCenter } from 'd3-force';

interface GraphNode {
  id: string;
  x?: number;
  y?: number;
  vx?: number;
  vy?: number;
  fx?: number;
  fy?: number;
}

interface GraphEdge {
  source: string | GraphNode;
  target: string | GraphNode;
}

self.onmessage = (e: MessageEvent) => {
  const { nodes, edges, width, height } = e.data as {
    nodes: GraphNode[];
    edges: GraphEdge[];
    width: number;
    height: number;
  };

  const simulation = forceSimulation(nodes as any)
    .force('link', forceLink(edges as any).id((d: any) => d.id))
    .force('charge', forceManyBody().strength(-100))
    .force('center', forceCenter(width / 2, height / 2))
    .stop();

  for (let i = 0; i < 300; ++i) simulation.tick();
  self.postMessage({ nodes });
};
