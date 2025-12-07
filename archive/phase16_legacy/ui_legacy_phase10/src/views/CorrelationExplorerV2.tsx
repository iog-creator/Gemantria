// Phase 10: Correlation Visualization Explorer
// Redesign: Premium "Cosmic/Ethereal" Aesthetic
// Vision: Minimalist, Delightful, Instant Comprehension

import React, { useState, useEffect, useMemo } from 'react';
import {
  ReactFlow,
  Node,
  Edge,
  useNodesState,
  useEdgesState,
  Controls,
  Background,
  BackgroundVariant,
  Panel,
} from 'reactflow';
import 'reactflow/dist/style.css';

// --- Types ---
interface GraphStats {
  nodes: number;
  edges: number;
  clusters: number;
  density: number;
  centrality: {
    avg_degree: number;
    avg_betweenness: number;
  };
  generated_at?: string;
}

interface GraphNode {
  id: string;
  surface?: string;
  hebrew?: string;
  gematria?: number;
  class?: string;
  [key: string]: any;
}

interface GraphEdge {
  source: string;
  target: string;
  cosine?: number;
  rerank_score?: number;
  edge_strength?: number;
  class?: string;
  [key: string]: any;
}

interface ScoredGraph {
  schema: string;
  nodes: GraphNode[];
  edges: GraphEdge[];
  metadata?: any;
}

// --- Components ---

const GlassPanel = ({ children, className = '' }: { children: React.ReactNode; className?: string }) => (
  <div className={`backdrop-blur-xl bg-slate-900/60 border border-white/10 shadow-2xl rounded-2xl overflow-hidden transition-all duration-300 ${className}`}>
    {children}
  </div>
);

const StatBadge = ({ label, value, subtext }: { label: string; value: string | number; subtext?: string }) => (
  <div className="flex flex-col items-center justify-center px-4 py-2">
    <div className="text-2xl font-light text-white tracking-tight">{value}</div>
    <div className="text-[10px] uppercase tracking-widest text-slate-400 font-medium">{label}</div>
    {subtext && <div className="text-[9px] text-slate-500 mt-0.5">{subtext}</div>}
  </div>
);

const CorrelationExplorer: React.FC = () => {
  // --- State ---
  const [stats, setStats] = useState<GraphStats | null>(null);
  const [graph, setGraph] = useState<ScoredGraph | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Controls
  const [edgeStrengthThreshold, setEdgeStrengthThreshold] = useState(0.75);
  const [filterByClass, setFilterByClass] = useState<'all' | 'strong' | 'weak' | 'very_weak'>('all');
  const [isFiltersOpen, setIsFiltersOpen] = useState(true);

  // React Flow
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  // --- Data Loading ---
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        setError(null);

        const [statsRes, graphRes] = await Promise.all([
          fetch('/exports/graph_stats.json', { cache: 'no-store' }),
          fetch('/exports/graph_latest.scored.json', { cache: 'no-store' })
        ]);

        if (!statsRes.ok) throw new Error(`Stats load failed: ${statsRes.status}`);
        if (!graphRes.ok) throw new Error(`Graph load failed: ${graphRes.status}`);

        const statsData = await statsRes.json();
        const graphData = await graphRes.json();

        setStats(statsData);
        setGraph(graphData);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  // --- Graph Processing ---
  const filteredGraph = useMemo(() => {
    if (!graph) return { nodes: [], edges: [] };

    const filteredEdges = graph.edges.filter((edge) => {
      const strength = edge.edge_strength || edge.cosine || 0;
      if (strength < edgeStrengthThreshold) return false;
      if (filterByClass !== 'all' && edge.class !== filterByClass) return false;
      return true;
    });

    const nodeIds = new Set<string>();
    filteredEdges.forEach((e) => { nodeIds.add(e.source); nodeIds.add(e.target); });
    const filteredNodes = graph.nodes.filter((n) => nodeIds.has(n.id));

    return { nodes: filteredNodes, edges: filteredEdges };
  }, [graph, edgeStrengthThreshold, filterByClass]);

  const { flowNodes, flowEdges } = useMemo(() => {
    if (!filteredGraph.nodes.length) return { flowNodes: [], flowEdges: [] };

    const cols = Math.ceil(Math.sqrt(filteredGraph.nodes.length));

    const nodes: Node[] = filteredGraph.nodes.map((node, index) => {
      const row = Math.floor(index / cols);
      const col = index % cols;
      const label = node.surface || node.hebrew || node.id;

      // Ethereal Node Styling
      return {
        id: node.id,
        type: 'default',
        position: { x: col * 250, y: row * 250 }, // More space
        data: { label },
        style: {
          background: 'rgba(15, 23, 42, 0.8)', // Slate-900 with opacity
          border: '1px solid rgba(255, 255, 255, 0.2)',
          borderRadius: '50%',
          width: 120,
          height: 120,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#fff',
          fontSize: '14px',
          fontFamily: 'Inter, sans-serif',
          fontWeight: 300,
          letterSpacing: '0.05em',
          boxShadow: '0 0 20px rgba(56, 189, 248, 0.1)', // Subtle blue glow
          backdropFilter: 'blur(4px)',
          transition: 'all 0.3s ease',
        },
      };
    });

    const edges: Edge[] = filteredGraph.edges.map((edge, index) => {
      const strength = edge.edge_strength || edge.cosine || 0;
      // Starlight Edge Styling
      const opacity = Math.max(0.1, strength - 0.2); // Fade out weak edges
      const width = strength * 2;

      return {
        id: `e-${index}`,
        source: edge.source,
        target: edge.target,
        style: {
          stroke: `rgba(255, 255, 255, ${opacity})`, // White starlight
          strokeWidth: width,
        },
        animated: strength > 0.9, // Only animate strong connections
      };
    });

    return { flowNodes: nodes, flowEdges: edges };
  }, [filteredGraph]);

  useEffect(() => {
    setNodes(flowNodes);
    setEdges(flowEdges);
  }, [flowNodes, flowEdges, setNodes, setEdges]);

  // --- Render ---
  if (loading) return <div className="h-screen w-screen bg-slate-950 flex items-center justify-center text-slate-400 font-light tracking-widest animate-pulse">INITIALIZING VISUALIZATION...</div>;
  if (error) return <div className="h-screen w-screen bg-slate-950 flex items-center justify-center text-red-400 font-light">{error}</div>;
  if (!stats) return null;

  return (
    <div className="h-screen w-screen bg-slate-950 relative overflow-hidden font-sans text-slate-200">
      {/* Background Ambient Effects */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-slate-900 via-slate-950 to-black opacity-80 pointer-events-none" />

      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        fitView
        minZoom={0.1}
        maxZoom={4}
        defaultViewport={{ x: 0, y: 0, zoom: 0.5 }}
        proOptions={{ hideAttribution: true }}
      >
        <Background
          variant={BackgroundVariant.Dots}
          gap={30}
          size={1}
          color="rgba(255, 255, 255, 0.05)"
        />
        <Controls
          className="bg-slate-800/50 border-white/10 fill-white"
          showInteractive={false}
        />

        {/* --- Floating UI Panels --- */}

        {/* Top Right: Key Metrics */}
        <Panel position="top-right" className="m-6">
          <GlassPanel className="flex divide-x divide-white/10">
            <StatBadge label="Nodes" value={stats.nodes} />
            <StatBadge label="Edges" value={stats.edges} />
            <StatBadge label="Clusters" value={stats.clusters} />
            <StatBadge label="Visible" value={filteredGraph.edges.length} subtext={`${((filteredGraph.edges.length / stats.edges) * 100).toFixed(0)}%`} />
          </GlassPanel>
        </Panel>

        {/* Top Left: Title & Filters */}
        <Panel position="top-left" className="m-6 max-w-xs">
          <GlassPanel className="p-5">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h1 className="text-lg font-medium text-white tracking-tight">Correlation Explorer</h1>
                <p className="text-xs text-slate-400 mt-1">Semantic Network Visualization</p>
              </div>
              <button
                onClick={() => setIsFiltersOpen(!isFiltersOpen)}
                className="text-xs text-slate-500 hover:text-white transition-colors"
              >
                {isFiltersOpen ? 'Hide' : 'Show'}
              </button>
            </div>

            {isFiltersOpen && (
              <div className="space-y-6 animate-in fade-in slide-in-from-top-2 duration-300">
                {/* Strength Slider */}
                <div className="space-y-2">
                  <div className="flex justify-between text-xs">
                    <span className="text-slate-400">Connection Strength</span>
                    <span className="text-white font-mono">{edgeStrengthThreshold.toFixed(2)}</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.05"
                    value={edgeStrengthThreshold}
                    onChange={(e) => setEdgeStrengthThreshold(parseFloat(e.target.value))}
                    className="w-full h-1 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-white"
                  />
                  <div className="flex justify-between text-[10px] text-slate-600">
                    <span>Loose</span>
                    <span>Strict</span>
                  </div>
                </div>

                {/* Class Filter */}
                <div className="space-y-2">
                  <span className="text-xs text-slate-400 block">Filter by Class</span>
                  <div className="flex flex-wrap gap-2">
                    {['all', 'strong', 'weak'].map((opt) => (
                      <button
                        key={opt}
                        onClick={() => setFilterByClass(opt as any)}
                        className={`px-3 py-1 text-xs rounded-full border transition-all ${filterByClass === opt
                            ? 'bg-white text-slate-900 border-white font-medium'
                            : 'bg-transparent text-slate-400 border-slate-700 hover:border-slate-500'
                          }`}
                      >
                        {opt.charAt(0).toUpperCase() + opt.slice(1)}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </GlassPanel>
        </Panel>

        {/* Bottom Right: Legend */}
        <Panel position="bottom-right" className="m-6">
          <GlassPanel className="p-3">
            <div className="flex items-center gap-4 text-[10px] text-slate-400">
              <div className="flex items-center gap-1.5">
                <div className="w-2 h-2 rounded-full bg-slate-900 border border-white/50 shadow-[0_0_10px_rgba(255,255,255,0.3)]"></div>
                <span>Concept Node</span>
              </div>
              <div className="flex items-center gap-1.5">
                <div className="w-8 h-0.5 bg-white/50"></div>
                <span>Correlation</span>
              </div>
              <div className="flex items-center gap-1.5">
                <div className="w-8 h-0.5 border-t border-dashed border-white/30"></div>
                <span>Weak Link</span>
              </div>
            </div>
          </GlassPanel>
        </Panel>

      </ReactFlow>
    </div>
  );
};

export default CorrelationExplorer;

