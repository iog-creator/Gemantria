import { useState, useCallback, useMemo, useEffect, useRef } from "react";
import { scaleOrdinal } from "@visx/scale";
import { Group } from "@visx/group";
import { Text } from "@visx/text";
import { Circle, Line } from "@visx/shape";
import * as d3 from "d3-force";
import { GraphNode, GraphEdge } from "../types/graph";
import { usePerformance } from "../hooks/usePerformance";
import { canUseWebGL } from "../utils/capabilities";
import WebGLRenderer from "../renderers/webgl/Renderer";

interface GraphViewProps {
  nodes: GraphNode[];
  edges: GraphEdge[];
  width: number;
  height: number;
  onNodeSelect?: (node: GraphNode | null) => void;
  onMetricsReport?: (metrics: {
    visibleNodes: number;
    totalNodes: number;
    visibleEdges: number;
    totalEdges: number;
    zoomLevel: number;
    isLargeDataset: boolean;
  }) => void;
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
  onMetricsReport,
}: GraphViewProps) {
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [hoveredNode, setHoveredNode] = useState<GraphNode | null>(null);
  const [simulationNodes, setSimulationNodes] = useState<SimulationNode[]>([]);
  const [simulationLinks, setSimulationLinks] = useState<SimulationLink[]>([]);

  // WebGL escalation check (Sprint 3)
  const [useWebGL, setUseWebGL] = useState<boolean>(() => {
    // Check localStorage first (primary)
    const stored = localStorage.getItem('enable_webgl_fallback');
    if (stored !== null) {
      return JSON.parse(stored);
    }

    // For initial state, we'll use false and update in useEffect
    return false;
  });

  // Check escalation file on mount (async)
  useEffect(() => {
    if (localStorage.getItem('enable_webgl_fallback') === null) {
      // Only check file if localStorage not set
      fetch('/var/ui/escalation.json')
        .then(res => res.ok ? res.json() : null)
        .then(data => {
          if (data?.enable_webgl_fallback) {
            setUseWebGL(true);
            localStorage.setItem('enable_webgl_fallback', 'true');
          }
        })
        .catch(() => {
          // File doesn't exist or can't be read, stay with default
        });
    }
  }, []);

  // Performance monitoring
  const { metrics, measureRenderTime, countDOMNodes, setContainerRef, isSlow, needsWebGL } = usePerformance();

  // Zoom and pan state
  const [zoom, setZoom] = useState({ scale: 1, x: 0, y: 0 });
  const svgRef = useRef<SVGSVGElement>(null);

  // Large dataset detection (>10k nodes triggers optimizations)
  const isLargeDataset = nodes.length > 10000;
  const visibleNodeCount = useMemo(() => {
    if (!isLargeDataset) return nodes.length;

    // Calculate viewport bounds
    const viewportBounds = {
      left: -zoom.x / zoom.scale,
      right: (-zoom.x + width) / zoom.scale,
      top: -zoom.y / zoom.scale,
      bottom: (-zoom.y + height) / zoom.scale,
    };

    // Count nodes in viewport (rough estimate)
    return simulationNodes.filter(node =>
      node.x !== undefined && node.y !== undefined &&
      node.x >= viewportBounds.left && node.x <= viewportBounds.right &&
      node.y >= viewportBounds.top && node.y <= viewportBounds.bottom
    ).length;
  }, [simulationNodes, zoom, width, height, isLargeDataset]);

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

  // Viewport culling: filter nodes and edges to visible area
  const visibleNodes = useMemo(() => {
    if (!isLargeDataset) return simulationNodes;

    const viewportBounds = {
      left: -zoom.x / zoom.scale - 50, // Add padding
      right: (-zoom.x + width) / zoom.scale + 50,
      top: -zoom.y / zoom.scale - 50,
      bottom: (-zoom.y + height) / zoom.scale + 50,
    };

    return simulationNodes.filter(node =>
      node.x !== undefined && node.y !== undefined &&
      node.x >= viewportBounds.left && node.x <= viewportBounds.right &&
      node.y >= viewportBounds.top && node.y <= viewportBounds.bottom
    );
  }, [simulationNodes, zoom, width, height, isLargeDataset]);

  const visibleEdges = useMemo(() => {
    if (!isLargeDataset) return simulationLinks;

    const visibleNodeIds = new Set(visibleNodes.map(n => n.id));
    return simulationLinks.filter(link =>
      visibleNodeIds.has(link.source.id) && visibleNodeIds.has(link.target.id)
    );
  }, [simulationLinks, visibleNodes, isLargeDataset]);

  // Zoom and pan handlers
  const handleZoom = useCallback((event: React.WheelEvent) => {
    event.preventDefault();
    const delta = event.deltaY > 0 ? 0.9 : 1.1;
    const newScale = Math.max(0.1, Math.min(5, zoom.scale * delta));

    // Zoom towards mouse position
    const rect = svgRef.current?.getBoundingClientRect();
    if (rect) {
      const mouseX = event.clientX - rect.left;
      const mouseY = event.clientY - rect.top;
      const newX = mouseX - (mouseX - zoom.x) * (newScale / zoom.scale);
      const newY = mouseY - (mouseY - zoom.y) * (newScale / zoom.scale);

      setZoom({ scale: newScale, x: newX, y: newY });
    }
  }, [zoom]);

  const handlePanStart = useCallback((event: React.MouseEvent) => {
    if (event.button !== 0) return; // Only left mouse button

    const startX = event.clientX - zoom.x;
    const startY = event.clientY - zoom.y;

    const handleMouseMove = (e: MouseEvent) => {
      setZoom(prev => ({
        ...prev,
        x: e.clientX - startX,
        y: e.clientY - startY,
      }));
    };

    const handleMouseUp = () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
  }, [zoom]);

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

  // Report metrics to parent
  useEffect(() => {
    if (onMetricsReport) {
      onMetricsReport({
        visibleNodes: visibleNodes.length,
        totalNodes: nodes.length,
        visibleEdges: visibleEdges.length,
        totalEdges: edges.length,
        zoomLevel: zoom.scale,
        isLargeDataset,
      });
    }
  }, [visibleNodes.length, visibleEdges.length, nodes.length, edges.length, zoom.scale, isLargeDataset, onMetricsReport]);

  // Performance measurement
  useEffect(() => {
    const startTime = performance.now();
    return () => {
      measureRenderTime(startTime);
      countDOMNodes();
    };
  }, [simulationNodes, simulationLinks, measureRenderTime, countDOMNodes]);

  // Conditional rendering: WebGL vs SVG (Sprint 3)
  if (useWebGL && canUseWebGL()) {
    return (
      <div className="w-full h-full bg-gray-50 rounded-lg overflow-hidden relative">
        {/* WebGL mode indicator */}
        <div className="absolute top-2 left-2 bg-green-600 text-white px-3 py-1 rounded-lg text-sm font-medium z-10 shadow-lg">
          WebGL Mode • Nodes: {nodes.length.toLocaleString()}
        </div>

        {/* Performance indicator */}
        {isSlow && (
          <div className="absolute top-2 right-2 bg-yellow-500 text-white px-3 py-1 rounded-lg text-sm z-10 shadow-lg">
            WebGL Active
          </div>
        )}

        <WebGLRenderer
          data={{
            nodes: simulationNodes.map(n => ({
              id: n.id,
              x: n.x || 0,
              y: n.y || 0
            })),
            edges: simulationLinks
          }}
          width={width}
          height={height}
        />
      </div>
    );
  }

  // Default SVG rendering
  return (
    <div
      ref={setContainerRef}
      className="w-full h-full bg-gray-50 rounded-lg overflow-hidden relative"
    >
      {/* Large dataset overlay */}
      {isLargeDataset && (
        <div className="absolute top-2 left-2 bg-blue-600 text-white px-3 py-1 rounded-lg text-sm font-medium z-10 shadow-lg">
          Large mode • Nodes: {nodes.length.toLocaleString()} • Visible: {visibleNodeCount}
          {needsWebGL && (
            <span className="ml-2 text-yellow-300">⚠️ Consider WebGL</span>
          )}
        </div>
      )}

      {/* Performance indicator */}
      {isSlow && (
        <div className="absolute top-2 right-2 bg-yellow-500 text-white px-3 py-1 rounded-lg text-sm z-10 shadow-lg">
          Slow: {metrics.tti.toFixed(0)}ms TTI
        </div>
      )}

      <svg
        ref={svgRef}
        width={width}
        height={height}
        onWheel={handleZoom}
        onMouseDown={handlePanStart}
        style={{ cursor: 'grab' }}
      >
        <g transform={`translate(${zoom.x}, ${zoom.y}) scale(${zoom.scale})`}>
          <Group>
            {/* Render edges */}
            {(isLargeDataset ? visibleEdges : simulationLinks).map((link, i) => {
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
            {(isLargeDataset ? visibleNodes : simulationNodes).map((node, i) => {
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
                  {/* Only show labels for selected/hovered nodes in large datasets */}
                  {(isSelected || isHovered || !isLargeDataset) && (
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
                  )}
                </Group>
              );
            })}
          </Group>
        </g>
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
