import { useEffect, useState } from "react";

export type Stats = {
  nodes: number;
  edges: number;
  clusters: number;
  avg_degree?: number;
  avg_cluster_density?: number;
  avg_cluster_diversity?: number;
};

export default function useGraphStats() {
  const [stats, setStats] = useState<Stats | null>(null);

  useEffect(() => {
    fetch("/exports/graph_latest.json") // fallback if stats file not hosted
      .catch(() => null);
    fetch("/exports/graph_stats.json").then(async r => {
      if (r.ok) {
        setStats(await r.json());
        return;
      }
      // fallback to on-demand script output path if you serve it
      try {
        const r2 = await fetch("/api/stats");
        setStats(await r2.json());
      } catch {}
    }).catch(() => {});
  }, []);

  return stats;
}
