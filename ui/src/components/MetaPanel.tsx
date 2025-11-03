import React, { useEffect, useState } from 'react';

interface Props {
  meta: any;
}

const MetaPanel: React.FC<Props> = ({ meta }) => {
  // P11 Sprint 2: Perf badge from var/ui/perf.json (local fetch, color-coded)
  const [perf, setPerf] = useState({ ms: 0, color: 'gray' });

  useEffect(() => {
    fetch('/var/ui/perf.json').then(r => r.json()).then(d => {
      const ms = d.probe.ms;
      setPerf({ ms, color: ms < 200 ? 'green' : ms < 500 ? 'yellow' : 'red' });
    }).catch(() => setPerf({ ms: 0, color: 'gray' }));
  }, []);

  return (
    <div>
      <h3>Meta</h3>
      <pre>{JSON.stringify(meta, null, 2)}</pre>
      <div title={`Load: ${perf.ms}ms`} style={{ display: 'inline-block', width: '10px', height: '10px', background: perf.color, borderRadius: '50%', marginLeft: '10px' }} />
    </div>
  );
};

export default MetaPanel;
