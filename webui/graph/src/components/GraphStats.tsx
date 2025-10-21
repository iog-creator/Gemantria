import useGraphStats from "../hooks/useGraphStats";

export default function GraphStats() {
  const s = useGraphStats();
  if (!s) return <div className="p-4">Loading stats…</div>;

  const Card = ({ label, value }: { label: string; value: any }) => (
    <div className="rounded-2xl shadow p-4">
      <div className="text-sm opacity-70">{label}</div>
      <div className="text-2xl font-semibold">{value ?? "—"}</div>
    </div>
  );

  return (
    <div className="grid grid-cols-2 gap-3">
      <Card label="Nodes" value={s.nodes} />
      <Card label="Edges" value={s.edges} />
      <Card label="Clusters" value={s.clusters} />
      <Card label="Avg Degree" value={s.avg_degree?.toFixed?.(2) ?? s.avg_degree} />
      <Card label="Avg Cluster Density" value={s.avg_cluster_density?.toFixed?.(3) ?? s.avg_cluster_density} />
      <Card label="Avg Cluster Diversity" value={s.avg_cluster_diversity?.toFixed?.(3) ?? s.avg_cluster_diversity} />
    </div>
  );
}
