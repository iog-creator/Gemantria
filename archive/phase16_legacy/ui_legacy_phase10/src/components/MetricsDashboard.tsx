import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';  // Assume pinned in package.json

const MetricsDashboard: React.FC = () => {
  const ref = useRef<SVGSVGElement>(null);
  useEffect(() => {
    fetch('/var/ui/metrics.jsonl').then(r => r.text()).then(text => {
      const data = text.trim().split('\n').map(line => JSON.parse(line));
      if (data.length === 0) return;
      const svg = d3.select(ref.current);
      svg.selectAll('*').remove();
      const width = 600, height = 200;
      svg.attr('width', width).attr('height', height);
      const x = d3.scaleLinear().domain([0, data.length - 1]).range([0, width]);
      const y = d3.scaleLinear().domain([0, d3.max(data, d => d.summary_bytes)]).range([height, 0]);
      svg.append('g').selectAll('circle').data(data).enter().append('circle')
        .attr('cx', (d, i) => x(i)).attr('cy', d => y(d.summary_bytes)).attr('r', 3).attr('fill', 'steelblue');
      svg.append('line').attr('x1', 0).attr('y1', height).attr('x2', width).attr('y2', height).attr('stroke', 'black');
    }).catch(() => console.log('Metrics jsonl missing; stub data'));
  }, []);

  const exportSVG = () => {
    const svg = ref.current;
    if (svg) {
      const serializer = new XMLSerializer();
      const str = serializer.serializeToString(svg);
      const blob = new Blob([str], { type: 'image/svg+xml' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url; a.download = 'metrics-trend.svg'; a.click();
      URL.revokeObjectURL(url);
    }
  };

  return (
    <div>
      <h3>Metrics Trends</h3>
      <svg ref={ref} />
      <button onClick={exportSVG}>Export SVG</button>
    </div>
  );
};

export default MetricsDashboard;
