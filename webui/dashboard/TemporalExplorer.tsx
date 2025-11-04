import React, { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import axios from 'axios';

interface TemporalPattern {
  series_id: string;
  unit: string;
  window: number;
  values: number[];
  metric: string;
  book: string;
  change_points?: number[];
}

interface TemporalData {
  temporal_patterns: TemporalPattern[];
  metadata: {
    total_series: number;
    books_analyzed: string[];
    analysis_parameters: {
      default_unit: string;
      default_window: number;
      min_series_length: number;
    };
  };
  filters_applied?: {
    book?: string;
    metric?: string;
  };
  result_count: number;
}

const TemporalExplorer: React.FC = () => {
  const [data, setData] = useState<TemporalData | null>(null);
  const [loading, setLoading] = useState(true);
  const [metric, setMetric] = useState<string>('');
  const [book, setBook] = useState('Genesis');

  useEffect(() => {
    setLoading(true);
    const params = new URLSearchParams();
    if (book) params.append('book', book);
    if (metric) params.append('metric', metric);
    
    axios.get(`/temporal/patterns?${params.toString()}`)
      .then(res => {
        setData(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error('API error:', err);
        setLoading(false);
      });
  }, [book, metric]);

  if (loading) return <div>Loading...</div>;
  if (!data || data.temporal_patterns.length === 0) {
    return (
      <div className="p-4 bg-white rounded shadow">
        <h2 className="text-xl mb-4">Temporal Pattern Explorer</h2>
        <p>No temporal patterns found. Filters: book={book}, metric={metric || 'all'}</p>
      </div>
    );
  }

  // Use first pattern for visualization
  const pattern = data.temporal_patterns[0];
  const chartData = pattern.values.map((value, idx) => ({ index: idx, value }));

  return (
    <div className="p-4 bg-white rounded shadow">
      <h2 className="text-xl mb-4">Temporal Pattern Explorer</h2>
      <div className="mb-4 flex gap-4">
        <select value={book} onChange={e => setBook(e.target.value)} className="border rounded px-2 py-1">
          <option value="Genesis">Genesis</option>
          <option value="Exodus">Exodus</option>
        </select>
        <select value={metric} onChange={e => setMetric(e.target.value)} className="border rounded px-2 py-1">
          <option value="">All Metrics</option>
          <option value="frequency">Frequency</option>
          <option value="strength">Strength</option>
          <option value="cooccurrence">Co-occurrence</option>
        </select>
      </div>
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={chartData}>
          <XAxis dataKey="index" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="value" stroke="#8884d8" />
        </LineChart>
      </ResponsiveContainer>
      {pattern.change_points && pattern.change_points.length > 0 && (
        <p className="mt-2 text-sm">Change Points: {pattern.change_points.join(', ')}</p>
      )}
      <p className="mt-2 text-sm text-gray-600">
        Series: {pattern.series_id} | Book: {pattern.book} | Unit: {pattern.unit} | Window: {pattern.window} | Total: {data.result_count} patterns
      </p>
    </div>
  );
};

export default TemporalExplorer;

