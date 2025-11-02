// Placeholder stats view (P10-B)

import React, { useEffect, useState } from 'react';
import { Envelope } from '../types/envelope';
import { loadEnvelope, getEnvelopeStats } from '../lib/loadEnvelope';

export function EnvelopeStats() {
  const [envelope, setEnvelope] = useState<Envelope | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadEnvelope().then((data) => {
      setEnvelope(data);
      setLoading(false);
    });
  }, []);

  if (loading) {
    return <div>Loading envelope...</div>;
  }

  if (!envelope) {
    return (
      <div style={{ padding: '20px', border: '1px solid #ccc', margin: '20px' }}>
        <h3>Envelope Not Found</h3>
        <p>Run <code>make ingest.local.envelope</code> to generate /tmp/p9-ingest-envelope.json</p>
      </div>
    );
  }

  const stats = getEnvelopeStats(envelope);

  return (
    <div style={{ padding: '20px', border: '1px solid #ccc', margin: '20px' }}>
      <h3>Envelope Stats</h3>
      <ul>
        <li>Nodes: {stats.nodeCount}</li>
        <li>Edges: {stats.edgeCount}</li>
        <li>Version: {stats.version}</li>
        <li>Source: {stats.source}</li>
        <li>Created: {stats.createdAt}</li>
      </ul>
    </div>
  );
}
