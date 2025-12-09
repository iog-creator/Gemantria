# Status Polling Optimization

## Problem

Multiple React components are polling `/api/status/system` simultaneously, causing:
- Excessive API calls
- Potential LM Studio health check thrashing
- Unnecessary load on the backend

## Current Polling Components

1. **useHeaderData.ts** - Polls every 60s
2. **AutopilotStatusTile.tsx** - Polls every 60s (fetches `/exports/control-plane/autopilot_summary.json`)
3. **BrowserVerifiedBadge.tsx** - Polls every 60s
4. **MCPROProofTile.tsx** - Polls every 60s
5. **useInsightsData.ts** - Polls every 30s
6. **useAutopilot.ts** - Polls every 5s (autopilot logs)
7. **useComplianceData.ts** - Polls every 30s

## Solution: Shared Status Hook

Create a single shared status hook that all components can use, with:
- Single polling interval (60s)
- Shared state across components
- Automatic cleanup when no components are using it

## Implementation

### 1. Create Shared Hook (`useSharedSystemStatus.ts`)

```typescript
import { useState, useEffect, useRef } from 'react';

interface SystemStatus {
  db: { reachable: boolean; mode: string; notes: string };
  lm: { slots: Array<{ name: string; provider: string; model: string; service: string }>; notes: string };
  updatedAt?: string;
}

let globalStatus: SystemStatus | null = null;
let subscribers = new Set<() => void>();
let pollInterval: NodeJS.Timeout | null = null;

const POLL_INTERVAL = 60000; // 60s

async function fetchStatus(): Promise<SystemStatus | null> {
  try {
    const res = await fetch('/api/status/system');
    if (res.ok) {
      const data = await res.json();
      globalStatus = {
        db: data.db || { reachable: false, mode: 'unknown', notes: '' },
        lm: data.lm || { slots: [], notes: '' },
        updatedAt: new Date().toISOString(),
      };
      subscribers.forEach(cb => cb());
      return globalStatus;
    }
  } catch (error) {
    console.error('Failed to fetch system status:', error);
  }
  return null;
}

function startPolling() {
  if (pollInterval) return; // Already polling
  fetchStatus(); // Initial fetch
  pollInterval = setInterval(fetchStatus, POLL_INTERVAL);
}

function stopPolling() {
  if (pollInterval) {
    clearInterval(pollInterval);
    pollInterval = null;
  }
}

export function useSharedSystemStatus() {
  const [status, setStatus] = useState<SystemStatus | null>(globalStatus);
  const updateRef = useRef(() => setStatus(globalStatus));

  useEffect(() => {
    subscribers.add(updateRef.current);
    startPolling();
    return () => {
      subscribers.delete(updateRef.current);
      if (subscribers.size === 0) {
        stopPolling();
      }
    };
  }, []);

  return status;
}
```

### 2. Update Components to Use Shared Hook

Replace individual polling with the shared hook:

```typescript
// Before (useHeaderData.ts)
const [data, setData] = useState<HeaderData>({...});
useEffect(() => {
  const fetchData = async () => {
    const statusRes = await fetch('/api/status/system');
    // ...
  };
  fetchData();
  const interval = setInterval(fetchData, 60000);
  return () => clearInterval(interval);
}, []);

// After
import { useSharedSystemStatus } from './useSharedSystemStatus';
const systemStatus = useSharedSystemStatus();
// Use systemStatus.db and systemStatus.lm directly
```

## Benefits

1. **Single API call** per polling interval (60s) instead of multiple
2. **Reduced backend load** - one status check instead of 7+
3. **Consistent data** - all components see the same status
4. **Automatic cleanup** - polling stops when no components need it

## Migration Steps

1. Create `useSharedSystemStatus.ts`
2. Update `useHeaderData.ts` to use shared hook
3. Update other components one by one
4. Test that all components still update correctly
5. Monitor API server logs to verify reduced calls

## Temporary Workaround

If migration is not immediate, increase polling intervals:

- `useInsightsData.ts`: 30s → 60s
- `useComplianceData.ts`: 30s → 60s
- `useAutopilot.ts`: 5s → 30s (for logs, this might be acceptable)

This reduces load but doesn't eliminate duplicate calls.

