import React, { useEffect, useState } from "react";

type Blend = {
  stats?: { p90?: number };
  thresholds?: { strict?: number };
};

export default function RerankP90Tile() {
  const [p90, setP90] = useState<string>("—");
  useEffect(() => {
    fetch("/share/eval/rerank_blend_report.json")
      .then((r) => r.json())
      .then((d: Blend) => {
        const v = d?.stats?.p90;
        setP90(typeof v === "number" ? v.toFixed(2) : "—");
      })
      .catch(() => setP90("—"));
  }, []);
  return (
    <div
      className="rounded-2xl shadow p-3 bg-white/5 border border-white/10"
      role="status"
      aria-label="Rerank 90th percentile score"
      tabIndex={0}
    >
      <div className="text-xs opacity-80">Rerank p90</div>
      <div className="text-2xl font-semibold">{p90}</div>
    </div>
  );
}

