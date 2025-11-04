import { useGraphData } from "../hooks/useGraphData";
import useGraphStats from "../hooks/useGraphStats";

export default function GraphStats() {
  const s = useGraphStats();
  const { data } = useGraphData();
  if (!s) return <div className="p-4">Loading stats…</div>;

  const download = (name: string, blob: Blob) => {
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = name;
    a.click();
  };

  const exportCSV = () => download('nodes.csv',
    new Blob([data.nodes.map((n: any) => Object.values(n).join(',')).join('\n')], {type: 'text/csv'}));

  const exportJSON = () => download('envelope.json',
    new Blob([JSON.stringify(data, null, 2)], {type: 'application/json'}));

  const Card = ({ label, value }: { label: string; value: any }) => (
    <div className="rounded-2xl shadow p-4">
      <div className="text-sm opacity-70">{label}</div>
      <div className="text-2xl font-semibold">{value ?? "—"}</div>
    </div>
  );

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-3">
        <Card label="Nodes" value={s.nodes} />
        <Card label="Edges" value={s.edges} />
        <Card label="Clusters" value={s.clusters} />
        <Card
          label="Avg Degree"
          value={s.avg_degree?.toFixed?.(2) ?? s.avg_degree}
        />
        <Card
          label="Avg Cluster Density"
          value={s.avg_cluster_density?.toFixed?.(3) ?? s.avg_cluster_density}
        />
        <Card
          label="Avg Cluster Diversity"
          value={s.avg_cluster_diversity?.toFixed?.(3) ?? s.avg_cluster_diversity}
        />
      </div>
      <div className="flex gap-2 justify-center">
        <button
          onClick={exportCSV}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm"
        >
          Export CSV
        </button>
        <button
          onClick={exportJSON}
          className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 text-sm"
        >
          Export JSON
        </button>
      </div>
    </div>
  );
}
