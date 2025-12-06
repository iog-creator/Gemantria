// Enhanced stats view with counts panel (P10-UI-01)

import React, { useEffect, useState } from 'react';
import { Envelope } from '../types/envelope';
import { loadEnvelope, getEnvelopeStats, saveEnvelopeArtifact } from '../lib/loadEnvelope';
import GraphPanel from './GraphPanel';

interface EnvelopeStatsProps {
  uploadedEnvelope?: Envelope | null;
}

export function EnvelopeStats({ uploadedEnvelope }: EnvelopeStatsProps) {
  const [envelope, setEnvelope] = useState<Envelope | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // If we have an uploaded envelope, use it; otherwise load the default
    if (uploadedEnvelope) {
      setEnvelope(uploadedEnvelope);
      setLoading(false);
      saveEnvelopeArtifact(uploadedEnvelope, 'demo-01-envelope-stats.json');
    } else {
      loadEnvelope().then((data) => {
        setEnvelope(data);
        setLoading(false);
      });
    }
  }, [uploadedEnvelope]);


  if (loading) {
    return <div style={{ padding: '20px' }}>Loading envelope...</div>;
  }

  if (!envelope) {
    return (
      <div style={{ padding: '20px', border: '1px solid #ccc', margin: '20px', borderRadius: '8px' }}>
        <h3>📁 No Envelope Loaded</h3>
        <p>Use the file loader above to select a Gemantria envelope JSON file, or run:</p>
        <code style={{ display: 'block', margin: '10px 0', padding: '10px', backgroundColor: '#f5f5f5' }}>
          make ingest.local.envelope
        </code>
        <p>to generate <code>/tmp/p9-ingest-envelope.json</code></p>
      </div>
    );
  }

  const stats = getEnvelopeStats(envelope);

  return (
    <div style={{ padding: '20px', border: '1px solid #ccc', margin: '20px', borderRadius: '8px' }}>
      <h3>📊 Envelope Statistics</h3>

      <GraphPanel />

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px', marginTop: '15px' }}>
        <div style={{ padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '6px' }}>
          <h4 style={{ margin: '0 0 10px 0', color: '#2c5aa0' }}>📋 Basic Counts</h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
            <div><strong>Nodes:</strong> {stats.nodeCount.toLocaleString()}</div>
            <div><strong>Edges:</strong> {stats.edgeCount.toLocaleString()}</div>
            <div><strong>Nodes with attrs:</strong> {stats.nodesWithAttrs.toLocaleString()}</div>
          </div>
        </div>

        <div style={{ padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '6px' }}>
          <h4 style={{ margin: '0 0 10px 0', color: '#2c5aa0' }}>🏷️ Types</h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
            <div><strong>Node types:</strong> {stats.nodeTypesCount}</div>
            <div><strong>Edge types:</strong> {stats.edgeTypesCount}</div>
          </div>
        </div>

        <div style={{ padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '6px' }}>
          <h4 style={{ margin: '0 0 10px 0', color: '#2c5aa0' }}>📄 Metadata</h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
            <div><strong>Version:</strong> {stats.version}</div>
            <div><strong>Source:</strong> {stats.source}</div>
            <div><strong>Seed:</strong> {stats.seed}</div>
            <div><strong>Created:</strong> {stats.createdAt}</div>
          </div>
        </div>
      </div>

      <div style={{ marginTop: '20px', padding: '10px', backgroundColor: '#e8f4fd', borderRadius: '4px' }}>
        <small style={{ color: '#666' }}>
          📁 Demo artifact saved to console log (would be ui/out/demo-01-envelope-stats.json in Node.js context)
        </small>
      </div>
    </div>
  );
}
