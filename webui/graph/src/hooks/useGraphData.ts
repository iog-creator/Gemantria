import { useState, useEffect } from "react";
import { GraphData, GraphNode, GraphEdge } from "../types/graph";

export function useGraphData(graphUrl: string = "/exports/graph_latest.json") {
  const [data, setData] = useState<GraphData>({ nodes: [], edges: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadGraphData() {
      try {
        setLoading(true);
        setError(null);

        const response = await fetch(graphUrl);
        if (!response.ok) {
          throw new Error(`Failed to load graph data: ${response.statusText}`);
        }

        const rawData = await response.json();

        // Transform the data to match our expected format
        const nodes: GraphNode[] = rawData.nodes.map((node: any) => ({
          id: node.id,
          label: node.label || node.id,
          cluster: node.cluster,
          degree: node.degree,
          betweenness: node.betweenness,
          eigenvector: node.eigenvector,
        }));

        const edges: GraphEdge[] = rawData.edges.map((edge: any) => ({
          source: edge.source,
          target: edge.target,
          strength: edge.strength || 0,
          rerank: edge.rerank,
          yes: edge.yes,
        }));

        const transformedData: GraphData = {
          nodes,
          edges,
          metadata: rawData.metadata,
        };

        setData(transformedData);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error occurred");
        console.error("Error loading graph data:", err);
      } finally {
        setLoading(false);
      }
    }

    loadGraphData();
  }, [graphUrl]);

  return { data, loading, error, refetch: () => window.location.reload() };
}
