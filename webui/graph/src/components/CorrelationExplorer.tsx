import { useEffect, useState, useMemo } from "react";
import { Group } from "@visx/group";
import { scaleLinear } from "@visx/scale";
import { AxisLeft, AxisBottom } from "@visx/axis";
import { GridRows, GridColumns } from "@visx/grid";
import { Circle, Line } from "@visx/shape";

interface CorrelationNode {
  id: string;
  label: string;
  type: string;
}

interface CorrelationEdge {
  source: string;
  target: string;
  correlation: number;
  weight: number;
  p_value: number;
  metric: string;
  cluster_source?: number;
  cluster_target?: number;
  significance: "significant" | "not_significant";
}

interface CorrelationNetwork {
  nodes: CorrelationNode[];
  edges: CorrelationEdge[];
  metadata: {
    node_count: number;
    edge_count: number;
    connected_components: number;
    is_connected: boolean;
    avg_weighted_degree?: number;
    max_weighted_degree?: number;
    avg_clustering_coeff?: number;
    correlation_threshold: number;
    total_input_correlations: number;
    filtered_correlations: number;
    correlation_methods: string[];
    export_timestamp: string;
    top_weighted_degree_nodes?: Array<{
      node: string;
      weighted_degree: number;
    }>;
  };
}

export default function CorrelationExplorer() {
  const [data, setData] = useState<CorrelationNetwork | null>(null);
  const [correlationThreshold, setCorrelationThreshold] = useState(0.4);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("/exports/graph_correlation_network.json")
      .then(async (r) => {
        if (r.ok) {
          const correlationData = await r.json();
          setData(correlationData);
        } else {
          setError("Correlation network data not available");
        }
      })
      .catch(() => {
        setError("Failed to load correlation network data");
      })
      .finally(() => setLoading(false));
  }, []);

  const filteredData = useMemo(() => {
    if (!data) return null;

    const filteredEdges = data.edges.filter(
      (edge) => Math.abs(edge.correlation) >= correlationThreshold,
    );

    // Get unique nodes from filtered edges
    const nodeIds = new Set<string>();
    filteredEdges.forEach((edge) => {
      nodeIds.add(edge.source);
      nodeIds.add(edge.target);
    });

    const filteredNodes = data.nodes.filter((node) => nodeIds.has(node.id));

    return {
      ...data,
      nodes: filteredNodes,
      edges: filteredEdges,
      metadata: {
        ...data.metadata,
        node_count: filteredNodes.length,
        edge_count: filteredEdges.length,
      },
    };
  }, [data, correlationThreshold]);

  if (loading) {
    return <div className="p-4">Loading correlation network…</div>;
  }

  if (error || !data) {
    return (
      <div className="p-4 text-red-600">
        {error || "No correlation network data available"}
      </div>
    );
  }

  if (!filteredData || filteredData.edges.length === 0) {
    return (
      <div className="p-4">
        <div className="mb-4">
          <label className="block text-sm font-medium mb-2">
            Correlation Threshold: {correlationThreshold.toFixed(2)}
          </label>
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={correlationThreshold}
            onChange={(e) =>
              setCorrelationThreshold(parseFloat(e.target.value))
            }
            className="w-full"
          />
        </div>
        <div className="text-gray-600">
          No correlations found above threshold{" "}
          {correlationThreshold.toFixed(2)}. Try lowering the threshold.
        </div>
      </div>
    );
  }

  const width = 600;
  const height = 400;
  const margin = { top: 20, right: 20, bottom: 60, left: 60 };

  // Create a simple node-link diagram layout
  const nodes = filteredData.nodes.map((node, i) => ({
    ...node,
    x: (i % 5) * 100 + 50, // Simple grid layout
    y: Math.floor(i / 5) * 100 + 50,
  }));

  const nodeMap = new Map(nodes.map((node) => [node.id, node]));

  // Color scale for correlation strength
  const colorScale = scaleLinear({
    domain: [-1, 1],
    range: ["#ff4444", "#4444ff"], // Red for negative, blue for positive
  });

  return (
    <div className="p-4">
      <div className="mb-4">
        <h3 className="text-lg font-semibold mb-2">
          Correlation Network Explorer
        </h3>
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="text-sm">
            <strong>Nodes:</strong> {filteredData.metadata.node_count} |
            <strong> Edges:</strong> {filteredData.metadata.edge_count} |
            <strong> Threshold:</strong> ≥{correlationThreshold.toFixed(2)}
          </div>
          <div className="text-sm">
            <strong>Components:</strong>{" "}
            {filteredData.metadata.connected_components} |
            <strong> Connected:</strong>{" "}
            {filteredData.metadata.is_connected ? "Yes" : "No"}
          </div>
        </div>

        <div className="mb-4">
          <label className="block text-sm font-medium mb-2">
            Correlation Threshold: {correlationThreshold.toFixed(2)}
          </label>
          <input
            type="range"
            min="0"
            max="1"
            step="0.05"
            value={correlationThreshold}
            onChange={(e) =>
              setCorrelationThreshold(parseFloat(e.target.value))
            }
            className="w-full"
          />
        </div>

        {filteredData.metadata.top_weighted_degree_nodes && (
          <div className="mb-4">
            <h4 className="text-sm font-medium mb-1">
              Top Connected Concepts:
            </h4>
            <div className="text-xs space-y-1">
              {filteredData.metadata.top_weighted_degree_nodes
                .slice(0, 3)
                .map((node, i) => (
                  <div key={node.node} className="flex justify-between">
                    <span>
                      {node.node.slice(0, 20)}
                      {node.node.length > 20 ? "..." : ""}
                    </span>
                    <span className="font-mono">
                      {node.weighted_degree.toFixed(2)}
                    </span>
                  </div>
                ))}
            </div>
          </div>
        )}
      </div>

      <div className="border rounded-lg p-4 bg-white">
        <svg width={width} height={height}>
          <rect width={width} height={height} fill="#f8f9fa" />

          {/* Edges */}
          {filteredData.edges.map((edge, i) => {
            const sourceNode = nodeMap.get(edge.source);
            const targetNode = nodeMap.get(edge.target);

            if (!sourceNode || !targetNode) return null;

            return (
              <Line
                key={`edge-${i}`}
                from={{ x: sourceNode.x, y: sourceNode.y }}
                to={{ x: targetNode.x, y: targetNode.y }}
                stroke={colorScale(edge.correlation)}
                strokeWidth={Math.abs(edge.weight) * 3 + 1}
                strokeOpacity={edge.significance === "significant" ? 1 : 0.6}
              />
            );
          })}

          {/* Nodes */}
          {nodes.map((node) => (
            <g key={`node-${node.id}`}>
              <Circle
                cx={node.x}
                cy={node.y}
                r={8}
                fill="#666"
                stroke="#fff"
                strokeWidth={2}
              />
              <text
                x={node.x}
                y={node.y - 12}
                textAnchor="middle"
                fontSize="10px"
                fill="#333"
                className="pointer-events-none"
              >
                {node.label.slice(0, 8)}
                {node.label.length > 8 ? "..." : ""}
              </text>
            </g>
          ))}
        </svg>
      </div>

      <div className="mt-4 text-xs text-gray-600">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <strong>Legend:</strong>
            <div className="flex items-center gap-2 mt-1">
              <div className="w-4 h-1 bg-blue-500"></div>
              <span>Positive correlation</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-1 bg-red-500"></div>
              <span>Negative correlation</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-1 bg-gray-400 opacity-60"></div>
              <span>Not significant (p ≥ 0.05)</span>
            </div>
          </div>
          <div>
            <strong>Methods:</strong>{" "}
            {data.metadata.correlation_methods.join(", ") || "Unknown"}
            <br />
            <strong>Updated:</strong>{" "}
            {new Date(data.metadata.export_timestamp).toLocaleString()}
          </div>
        </div>
      </div>
    </div>
  );
}
