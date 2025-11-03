import { useState, useCallback, useMemo, useEffect } from "react";
import { scaleOrdinal } from "@visx/scale";
import { Group } from "@visx/group";
import { Text } from "@visx/text";
import { Circle, Line } from "@visx/shape";
import * as d3 from "d3-force";
import { GraphNode, GraphEdge } from "../types/graph";

interface GraphViewProps {
  nodes: GraphNode[];
  edges: GraphEdge[];
  width: number;
  height: number;
  onNodeSelect?: (node: GraphNode | null) => void;
}

const colorScale = scaleOrdinal({
  domain: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
  range: [
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd",
    "#8c564b",
    "#e377c2",
    "#7f7f7f",
    "#bcbd22",
    "#17becf",
    "#aec7e8",
  ],
});

interface SimulationNode extends GraphNode {
  x?: number;
  y?: number;
  vx?: number;
  vy?: number;
  fx?: number | null;
  fy?: number | null;
}

interface SimulationLink extends GraphEdge {
  source: SimulationNode;
  target: SimulationNode;
}

export default function GraphView({
  nodes,
  edges,
  width,
  height,
  onNodeSelect,
}: GraphViewProps) {
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [hoveredNode, setHoveredNode] = useState<GraphNode | null>(null);
  const [simulationNodes, setSimulationNodes] = useState<SimulationNode[]>([]);
  const [simulationLinks, setSimulationLinks] = useState<SimulationLink[]>([]);

  const nodeMap = useMemo(() => {
    const map = new Map<string, GraphNode>();
    nodes.forEach((node) => map.set(node.id, node));
    return map;
  }, [nodes]);

  const handleNodeClick = useCallback(
    (node: GraphNode) => {
      const newSelected = selectedNode?.id === node.id ? null : node;
      setSelectedNode(newSelected);
      onNodeSelect?.(newSelected);
    },
    [selectedNode, onNodeSelect],
  );

  const handleNodeHover = useCallback((node: GraphNode | null) => {
    setHoveredNode(node);
  }, []);

  const nodeRadius = useCallback((node: GraphNode) => {
    const baseRadius = 5;
    const degreeMultiplier = Math.min(node.degree || 0, 0.1) * 50;
    return baseRadius + degreeMultiplier;
  }, []);

  const edgeOpacity = useCallback((edge: GraphEdge) => {
    return Math.max(0.1, Math.min(1, edge.strength));
  }, []);

  // Run d3-force simulation
  useEffect(() => {
    if (!nodes.length || !width || !height) return;

    // Initialize nodes with positions
    const initialNodes: SimulationNode[] = nodes.map((node) => ({
      ...node,
      x: Math.random() * width,
      y: Math.random() * height,
    }));

    // Initialize links
    const initialLinks: SimulationLink[] = edges.map((edge) => {
      const source = initialNodes.find(n => n.id === (typeof edge.source === 'string' ? edge.source : edge.source.id));
      const target = initialNodes.find(n => n.id === (typeof edge.target === 'string' ? edge.target : edge.target.id));
      return {
        ...edge,
        source: source!,
        target: target!,
      };
    });

    // Create simulation
    const simulation = d3.forceSimulation<SimulationNode>(initialNodes)
      .force('link', d3.forceLink<SimulationNode, SimulationLink>(initialLinks).id(d => d.id).distance(100))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('x', d3.forceX(width / 2).strength(0.1))
      .force('y', d3.forceY(height / 2).strength(0.1));

    // Update state on simulation tick
    const tick = () => {
      setSimulationNodes([...initialNodes]);
      setSimulationLinks([...initialLinks]);
    };

    simulation.on('tick', tick);

    // Run simulation for a few ticks then stop
    simulation.tick(100);
    simulation.stop();

    // Update state with final positions
    setSimulationNodes([...initialNodes]);
    setSimulationLinks([...initialLinks]);

    return () => {
      simulation.stop();
    };
  }, [nodes, edges, width, height]);

  return (
    <div className="w-full h-full bg-gray-50 rounded-lg overflow-hidden">
      <svg width={width} height={height}>
          <Group>
            {/* Render edges */}
          {simulationLinks.map((link, i) => {
            const sourceNode = link.source;
            const targetNode = link.target;

            if (!sourceNode || !targetNode || !sourceNode.x || !sourceNode.y || !targetNode.x || !targetNode.y) return null;

              return (
                <Line
                  key={`edge-${i}`}
                from={{ x: sourceNode.x, y: sourceNode.y }}
                to={{ x: targetNode.x, y: targetNode.y }}
                  stroke="#999"
                  strokeWidth={Math.max(1, (link.strength || 0) * 3)}
                strokeOpacity={edgeOpacity(link)}
                />
              );
            })}

            {/* Render nodes */}
          {simulationNodes.map((node, i) => {
              const originalNode = nodeMap.get(node.id);
            if (!originalNode || !node.x || !node.y) return null;

              const radius = nodeRadius(originalNode);
              const isSelected = selectedNode?.id === node.id;
              const isHovered = hoveredNode?.id === node.id;

              return (
                <Group key={`node-${i}`}>
                  <Circle
                  cx={node.x}
                  cy={node.y}
                    r={radius}
                    fill={colorScale(originalNode.cluster || 0)}
                    stroke={isSelected ? "#000" : isHovered ? "#666" : "none"}
                    strokeWidth={isSelected ? 3 : isHovered ? 2 : 0}
                    style={{ cursor: "pointer" }}
                    onClick={() => handleNodeClick(originalNode)}
                    onMouseEnter={() => handleNodeHover(originalNode)}
                    onMouseLeave={() => handleNodeHover(null)}
                  />
                  <Text
                  x={node.x}
                  y={node.y - radius - 5}
                    textAnchor="middle"
                    fontSize={10}
                    fill="#333"
                    style={{ pointerEvents: "none" }}
                  >
                    {originalNode.label.length > 10
                      ? `${originalNode.label.substring(0, 10)}...`
                      : originalNode.label}
                  </Text>
                </Group>
              );
            })}
          </Group>
      </svg>

      {/* Legend */}
      <div className="absolute top-4 right-4 bg-white p-3 rounded-lg shadow-lg">
        <h3 className="text-sm font-semibold mb-2">Clusters</h3>
        <div className="grid grid-cols-2 gap-1">
          {Array.from(new Set(nodes.map((n) => n.cluster).filter(Boolean)))
            .slice(0, 10)
            .map((cluster) => (
              <div key={cluster} className="flex items-center gap-2">
                <div
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: colorScale(cluster || 0) }}
                />
                <span className="text-xs">{cluster}</span>
              </div>
            ))}
        </div>
      </div>
    </div>
  );
}
