import React, { useState, useCallback, useMemo } from "react";
import ForceGraph2D from "react-force-graph-2d";
import { scaleOrdinal } from "@visx/scale";
import { Group } from "@visx/group";
import { Text } from "@visx/text";
import { Circle, Line } from "@visx/shape";
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

export default function GraphView({
  nodes,
  edges,
  width,
  height,
  onNodeSelect,
}: GraphViewProps) {
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [hoveredNode, setHoveredNode] = useState<GraphNode | null>(null);

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

  return (
    <div className="w-full h-full bg-gray-50 rounded-lg overflow-hidden">
      <ForceGraph2D
        graphData={{
          nodes: nodes.map((node) => ({ ...node })),
          links: edges.map((edge) => ({
            source:
              typeof edge.source === "string" ? edge.source : edge.source.id,
            target:
              typeof edge.target === "string" ? edge.target : edge.target.id,
            ...edge,
          })),
        }}
        width={width}
        height={height}
        cooldownTicks={100}
        nodeId={(node) => node.id}
        linkDistance={100}
        centerAt={{ x: width / 2, y: height / 2 }}
      >
        {({ nodes: forceNodes, links: forceLinks }) => (
          <Group>
            {/* Render edges */}
            {forceLinks.map((link, i) => {
              const sourceNode = forceNodes.find(
                (n) => n.id === link.source?.id,
              );
              const targetNode = forceNodes.find(
                (n) => n.id === link.target?.id,
              );

              if (!sourceNode || !targetNode) return null;

              return (
                <Line
                  key={`edge-${i}`}
                  from={{ x: sourceNode.x || 0, y: sourceNode.y || 0 }}
                  to={{ x: targetNode.x || 0, y: targetNode.y || 0 }}
                  stroke="#999"
                  strokeWidth={Math.max(1, (link.strength || 0) * 3)}
                  strokeOpacity={edgeOpacity(link as GraphEdge)}
                />
              );
            })}

            {/* Render nodes */}
            {forceNodes.map((node, i) => {
              const originalNode = nodeMap.get(node.id);
              if (!originalNode) return null;

              const radius = nodeRadius(originalNode);
              const isSelected = selectedNode?.id === node.id;
              const isHovered = hoveredNode?.id === node.id;

              return (
                <Group key={`node-${i}`}>
                  <Circle
                    cx={node.x || 0}
                    cy={node.y || 0}
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
                    x={node.x || 0}
                    y={(node.y || 0) - radius - 5}
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
        )}
      </ForceGraph2D>

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
