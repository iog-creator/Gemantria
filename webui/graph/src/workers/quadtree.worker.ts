self.onmessage = (e) => {
  const { nodes, bounds, maxDepth = 8 } = e.data;

  class QuadTree {
    bounds: any;
    depth: number;
    nodes: any[];
    children: QuadTree[] | null;

    constructor(bounds: any, depth = 0) {
      this.bounds = bounds;
      this.depth = depth;
      this.nodes = [];
      this.children = null;
    }

    insert(node: any) {
      if (this.children) {
        const idx = this.getQuadIndex(node);
        this.children[idx].insert(node);
        return;
      }

      this.nodes.push(node);

      if (this.nodes.length > 4 && this.depth < maxDepth) {
        this.subdivide();
      }
    }

    subdivide() {
      const [x, y, w, h] = this.bounds;
      const hw = w / 2;
      const hh = h / 2;

      this.children = [
        new QuadTree([x, y, hw, hh], this.depth + 1),        // NW
        new QuadTree([x + hw, y, hw, hh], this.depth + 1),   // NE
        new QuadTree([x, y + hh, hw, hh], this.depth + 1),   // SW
        new QuadTree([x + hw, y + hh, hw, hh], this.depth + 1) // SE
      ];

      // Redistribute existing nodes
      const existingNodes = [...this.nodes];
      this.nodes = [];

      for (const node of existingNodes) {
        const idx = this.getQuadIndex(node);
        this.children[idx].insert(node);
      }
    }

    getQuadIndex(node: any): number {
      const [x, y, w, h] = this.bounds;
      const midX = x + w / 2;
      const midY = y + h / 2;

      if (node.x < midX && node.y < midY) return 0; // NW
      if (node.x >= midX && node.y < midY) return 1; // NE
      if (node.x < midX && node.y >= midY) return 2; // SW
      return 3; // SE
    }

    query(range: any): any[] {
      const [rx, ry, rw, rh] = range;
      const [bx, by, bw, bh] = this.bounds;

      // Check if range intersects this quad
      if (rx > bx + bw || rx + rw < bx || ry > by + bh || ry + rh < by) {
        return [];
      }

      let results: any[] = [];

      if (this.children) {
        // Query children
        for (const child of this.children) {
          results = results.concat(child.query(range));
        }
      } else {
        // Check nodes in this quad
        for (const node of this.nodes) {
          if (node.x >= rx && node.x <= rx + rw &&
              node.y >= ry && node.y <= ry + rh) {
            results.push(node);
          }
        }
      }

      return results;
    }
  }

  const qt = new QuadTree(bounds);
  nodes.forEach((n: any) => qt.insert(n));

  self.postMessage({ quadtree: qt });
};
