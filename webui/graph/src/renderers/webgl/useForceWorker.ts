export function useForceWorker(enabled: boolean) {
  let worker: Worker | null = null;
  return {
    start(nodes: any[], edges: any[], iters=100, onDone: (out:any)=>void) {
      if (!enabled) return onDone({nodes, stats:{iters:0}});
      if (!worker) worker = new Worker(new URL('../../workers/layout.worker.ts', import.meta.url), { type: 'module' });
      let lastFrame = 0;
      const throttle = (e: MessageEvent) => {
        const now = performance.now();
        if (now - lastFrame > 1000/30) {  // 30Hz cap
          onDone(e.data);
          lastFrame = now;
        } else requestAnimationFrame(() => throttle(e));
      };
      worker.onmessage = throttle;
      worker.postMessage({ nodes, edges, iters });
    },
    stop() { if (worker) { worker.terminate(); worker = null; } }
  };
}
