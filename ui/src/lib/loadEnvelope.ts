// Local envelope loader (Phase-9 data source)

import { Envelope } from '../types/envelope';

const ENVELOPE_PATH = '/tmp/p9-ingest-envelope.json';

export async function loadEnvelope(): Promise<Envelope | null> {
  try {
    const response = await fetch(ENVELOPE_PATH);
    if (!response.ok) {
      console.warn(`Envelope not found at ${ENVELOPE_PATH}`);
      return null;
    }
    const data = await response.json();
    return data as Envelope;
  } catch (error) {
    console.warn('Failed to load envelope:', error);
    return null;
  }
}

export async function loadEnvelopeFromFile(file: File): Promise<Envelope> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const data = JSON.parse(e.target?.result as string);
        resolve(data as Envelope);
      } catch (error) {
        reject(new Error('Invalid JSON file'));
      }
    };
    reader.onerror = () => reject(new Error('Failed to read file'));
    reader.readAsText(file);
  });
}

export function getEnvelopeStats(envelope: Envelope) {
  // Calculate additional stats
  const nodeTypes = new Set(envelope.nodes.map(n => n.type || 'unknown'));
  const edgeTypes = new Set(envelope.edges.map(e => e.rel_type));
  const nodesWithAttrs = envelope.nodes.filter(n => n.attrs && Object.keys(n.attrs).length > 0).length;

  return {
    nodeCount: envelope.nodes.length,
    edgeCount: envelope.edges.length,
    nodeTypesCount: nodeTypes.size,
    edgeTypesCount: edgeTypes.size,
    nodesWithAttrs,
    version: envelope.meta.version,
    source: envelope.meta.source,
    createdAt: envelope.meta.created_at,
    snapshotPath: envelope.meta.snapshot_path,
    seed: envelope.meta.seed,
  };
}

export function saveEnvelopeArtifact(envelope: Envelope, filename: string) {
  // Save to ui/out/ directory for demo artifacts
  const artifact = {
    timestamp: new Date().toISOString(),
    envelope: {
      meta: envelope.meta,
      stats: getEnvelopeStats(envelope),
    },
  };

  // In browser environment, we can't directly write files
  // This would need to be implemented in a Node.js context or use downloads
  console.log(`Demo artifact would be saved to ui/out/${filename}:`, artifact);
  return artifact;
}
