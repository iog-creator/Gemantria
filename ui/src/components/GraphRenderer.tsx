// P10-UI-02: Minimal graph render using React Flow

import React, { useCallback, useMemo } from 'react';
import {
  ReactFlow,
  Node,
  Edge,
  addEdge,
  Connection,
  useNodesState,
  useEdgesState,
  Controls,
  Background,
  BackgroundVariant,
} from 'reactflow';
import 'reactflow/dist/style.css';

import { Envelope } from '../types/envelope';

interface GraphRendererProps {
  envelope: Envelope | null;
}

const GraphRenderer: React.FC<GraphRendererProps> = ({ envelope }) => {
  // Convert envelope nodes/edges to React Flow format
  const { initialNodes, initialEdges } = useMemo(() => {
    if (!envelope) {
      return { initialNodes: [], initialEdges: [] };
    }

    // Convert nodes - simple circular nodes positioned in a grid
    const nodes: Node[] = envelope.nodes.map((node, index) => {
      const cols = Math.ceil(Math.sqrt(envelope.nodes.length));
      const row = Math.floor(index / cols);
      const col = index % cols;

      return {
        id: node.id,
        type: 'default',
        position: { x: col * 150 + 50, y: row * 100 + 50 },
        data: { label: node.label },
        style: {
          background: '#e1f5fe',
          border: '1px solid #01579b',
          borderRadius: '50%',
          width: 80,
          height: 80,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '12px',
          fontWeight: 'bold',
        },
      };
    });

    // Convert edges
    const edges: Edge[] = envelope.edges.map((edge, index) => ({
      id: `edge-${index}`,
      source: edge.src,
      target: edge.dst,
      type: 'default',
      animated: false,
      style: { stroke: '#666', strokeWidth: 2 },
      label: edge.rel_type,
      labelStyle: { fontSize: '10px' },
    }));

    return { initialNodes: nodes, initialEdges: edges };
  }, [envelope]);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  if (!envelope) {
    return (
      <div style={{ padding: '20px', textAlign: 'center', color: '#666' }}>
        Load an envelope file to visualize the graph
      </div>
    );
  }

  if (!envelope.nodes.length) {
    return (
      <div className="p-6 text-sm text-gray-500">
        No nodes found in the envelope. Export first, then load
        <code className="mx-1">share/exports/envelope.json</code>.
      </div>
    );
  }
  // Derive simple temporal bounds for a hint (best-effort; safe if fields missing)
  const years: number[] = []
  envelope.nodes.slice(0, 2000).forEach((n: any) => {
    const d = typeof n.data === 'object' && n.data ? n.data : {}
    const y = Number.isInteger(n.year) ? n.year
      : Number.isInteger(d?.year) ? d.year
      : Number.isInteger(d?.start_year) ? d.start_year
      : null
    if (Number.isInteger(y)) years.push(Number(y))
  })
  const minY = years.length ? Math.min(...years) : null
  const maxY = years.length ? Math.max(...years) : null

  return (
    <div className="h-full w-full">
      {!!years.length && (
        <div className="px-3 py-2 text-xs text-gray-500">
          Temporal hint: {minY} – {maxY} ({years.length} nodes with year data)
        </div>
      )}
      <div style={{ width: '100%', height: '600px', border: '1px solid #ddd' }}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          fitView
          attributionPosition="bottom-left"
        >
          <Controls />
          <Background variant={BackgroundVariant.Dots} gap={20} size={1} />
        </ReactFlow>
      </div>
    </div>
  );
};

export { GraphRenderer };
