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
      for (let j=i+1;j<ns.length;j++){
        const dx = ns[j].x - ns[i].x, dy = ns[j].y - ns[i].y;
        const d2 = (dx*dx + dy*dy + 1e-3), f = rep / d2, fx = f * dx, fy = f * dy;
        ns[i].vx -= fx; ns[i].vy -= fy; ns[j].vx += fx; ns[j].vy += fy;
      }
    }
    for (const L of links){
      const si = idx.get(L.s), ti = idx.get(L.t); if (si==null||ti==null) continue;
      const dx = ns[ti].x - ns[si].x, dy = ns[ti].y - ns[si].y;
      ns[si].vx += k*dx; ns[si].vy += k*dy; ns[ti].vx -= k*dx; ns[ti].vy -= k*dy;
    }
    for (const n of ns){ n.x += n.vx*0.01; n.y += n.vy*0.01; n.vx*=0.9; n.vy*=0.9; }
  }
  self.postMessage({ nodes: ns.map(({vx,vy,...rest}) => rest), stats: { iters } });
};

export {};
