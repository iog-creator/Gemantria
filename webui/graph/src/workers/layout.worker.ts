export type WNode = {id: string|number, x: number, y: number, vx?: number, vy?: number};
export type WEdge = {source: any, target: any};

self.onmessage = (e: MessageEvent) => {
  const { nodes, edges, iters = 100 } = e.data as {nodes: WNode[], edges: WEdge[], iters?: number};
  const ns = nodes.map(n => ({...n, vx: n.vx||0, vy: n.vy||0}));
  const links = edges.map(e => ({s: (typeof e.source==='object'?e.source.id:e.source), t: (typeof e.target==='object'?e.target.id:e.target)}));
  const idx = new Map<any, number>(); ns.forEach((n,i)=>idx.set(n.id,i));
  const k = 0.02, rep = 200;
  for (let step=0; step<iters; step++) {
    for (let i=0;i<ns.length;i++){
      for (let j=i+1;j<ns.length;j++) {
        const dx = ns[j].x - ns[i].x, dy = ns[j].y - ns[i].y;
        const d2 = (dx*dx + dy*dy + 1e-3), f = rep / d2, fx = f * dx, fy = f * dy;
        ns[i].vx -= fx; ns[i].vy -= fy; ns[j].vx += fx; ns[j].vy += fy;
      }
    }
    for (let l of links) {
      const i = idx.get(l.s), j = idx.get(l.t);
      if (i===undefined || j===undefined) continue;
      const dx = ns[j].x - ns[i].x, dy = ns[j].y - ns[i].y;
      const d = Math.sqrt(dx*dx + dy*dy + 1e-3), f = k * (d - 50);
      const fx = f * dx / d, fy = f * dy / d;
      ns[i].vx += fx; ns[i].vy += fy; ns[j].vx -= fx; ns[j].vy -= fy;
    }
    for (let n of ns) {
      n.x += n.vx * 0.1; n.y += n.vy * 0.1;
      n.vx *= 0.9; n.vy *= 0.9;
    }
  }
  self.postMessage({ nodes: ns });
};
