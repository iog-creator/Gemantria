import { GraphNode } from "../types/graph";

interface NodeDetailsProps {
  node: GraphNode | null;
}

export default function NodeDetails({ node }: NodeDetailsProps) {
  if (!node) {
    return (
      <div className="p-4 bg-white rounded-lg shadow-lg">
        <h3 className="text-lg font-semibold mb-2">Node Details</h3>
        <p className="text-gray-500">Click on a node to see details</p>
      </div>
    );
  }

  return (
    <div className="p-4 bg-white rounded-lg shadow-lg max-w-sm">
      <h3 className="text-lg font-semibold mb-3">Node Details</h3>

      <div className="space-y-2">
        <div>
          <label className="text-sm font-medium text-gray-600">ID:</label>
          <p className="text-sm font-mono bg-gray-100 p-1 rounded">{node.id}</p>
        </div>

        <div>
          <label className="text-sm font-medium text-gray-600">Label:</label>
          <p className="text-sm">{node.label}</p>
        </div>

        {node.cluster !== undefined && (
          <div>
            <label className="text-sm font-medium text-gray-600">
              Cluster:
            </label>
            <p className="text-sm">{node.cluster}</p>
          </div>
        )}

        {node.degree !== undefined && (
          <div>
            <label className="text-sm font-medium text-gray-600">
              Degree Centrality:
            </label>
            <p className="text-sm">{node.degree.toFixed(4)}</p>
          </div>
        )}

        {node.betweenness !== undefined && (
          <div>
            <label className="text-sm font-medium text-gray-600">
              Betweenness:
            </label>
            <p className="text-sm">{node.betweenness.toExponential(2)}</p>
          </div>
        )}

        {node.eigenvector !== undefined && (
          <div>
            <label className="text-sm font-medium text-gray-600">
              Eigenvector:
            </label>
            <p className="text-sm">{node.eigenvector.toFixed(4)}</p>
          </div>
        )}
      </div>
    </div>
  );
}
