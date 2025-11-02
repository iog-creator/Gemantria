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

export function getEnvelopeStats(envelope: Envelope) {
  return {
    nodeCount: envelope.nodes.length,
    edgeCount: envelope.edges.length,
    version: envelope.meta.version,
    source: envelope.meta.source,
    createdAt: envelope.meta.created_at,
  };
}
