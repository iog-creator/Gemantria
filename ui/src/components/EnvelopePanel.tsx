import React from "react";

function useEnvelope() {
  try { return require("../../out/unified_envelope.json"); } catch { return null; }
}

export default function EnvelopePanel() {
  const env = useEnvelope();
  if (!env) return <div>Unified envelope not found.</div>;

  const nodes = (env.graph?.nodes || []).length;
  const edges = (env.graph?.edges || []).length;
  const strong = env.correlation?.edge_class_counts?.strong ?? 0;
  const weak = env.correlation?.edge_class_counts?.weak ?? 0;
  const other = env.correlation?.edge_class_counts?.other ?? 0;

  return (
    <div className="space-y-2">
      <div className="text-sm opacity-70">Book: {env.book} · Run: {env.meta?.run_id}</div>
      <div className="grid grid-cols-3 gap-3 text-center">
        <div className="p-3 rounded-lg shadow">Nodes<br/><b>{nodes}</b></div>
        <div className="p-3 rounded-lg shadow">Edges<br/><b>{edges}</b></div>
        <div className="p-3 rounded-lg shadow">Strong/Weak/Other<br/><b>{strong}/{weak}/{other}</b></div>
      </div>
    </div>
  );
}
