import React, { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, Area } from 'recharts';
import axios from 'axios';

interface Forecast {
  model: string;
  series_id: string;
  book: string;
  predictions: number[];
  prediction_intervals?: {
    lower: number[];
    upper: number[];
  };
  metrics?: {
    rmse: number;
    mae: number;
  };
}

interface ForecastData {
  forecasts: Forecast[];
  metadata: {
    generated_at: string;
    forecast_parameters: {
      default_horizon: number;
      default_model: string;
      min_training_length: number;
    };
    average_metrics: {
      rmse: number | null;
      mae: number | null;
    };
  };
  filters_applied?: {
    model?: string;
    horizon?: number;
  };
  result_count: number;
}

const ForecastDashboard: React.FC = () => {
  const [data, setData] = useState<ForecastData | null>(null);
  const [loading, setLoading] = useState(true);
  const [model, setModel] = useState('naive');
  const [horizon, setHorizon] = useState(10);

  useEffect(() => {
    setLoading(true);
    axios.get(`/temporal/forecast?model=${model}&horizon=${horizon}`)
      .then(res => {
        setData(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error('API error:', err);
        setLoading(false);
      });
  }, [model, horizon]);

  if (loading) return <div>Loading...</div>;
  if (!data || data.forecasts.length === 0) {
    return (
      <div className="p-4 bg-white rounded shadow">
        <h2 className="text-xl mb-4">Forecast Dashboard</h2>
        <p>No forecast data available for model: {model}</p>
      </div>
    );
  }

  const forecast = data.forecasts[0];
  const intervals = forecast.prediction_intervals;
  const chartData = forecast.predictions.map((val, idx) => ({
    step: idx + 1,
    forecast: val,
    lower: intervals?.lower?.[idx],
    upper: intervals?.upper?.[idx]
  }));

  const metrics = forecast.metrics || data.metadata.average_metrics;

  return (
    <div className="p-4 bg-white rounded shadow">
      <h2 className="text-xl mb-4">Forecast Dashboard</h2>
      <div className="mb-4 flex gap-4">
        <select value={model} onChange={e => setModel(e.target.value)} className="border rounded px-2 py-1">
          <option value="naive">Naive</option>
          <option value="sma">SMA</option>
          <option value="arima">ARIMA</option>
        </select>
        <input 
          type="number" 
          value={horizon} 
          onChange={e => setHorizon(parseInt(e.target.value) || 10)}
          min="1"
          max="100"
          className="border rounded px-2 py-1 w-24"
        />
        <label className="flex items-center">Horizon</label>
      </div>
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={chartData}>
          <XAxis dataKey="step" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="forecast" stroke="#8884d8" name="Forecast" />
          {intervals && (
            <>
              <Area type="monotone" dataKey="upper" fill="#8884d8" fillOpacity={0.2} stroke="none" />
              <Area type="monotone" dataKey="lower" fill="#8884d8" fillOpacity={0.2} stroke="none" />
            </>
          )}
        </LineChart>
      </ResponsiveContainer>
      <div className="mt-2 text-sm">
        <p>Series: {forecast.series_id} | Book: {forecast.book}</p>
        {metrics && (
          <p>Metrics: RMSE {metrics.rmse?.toFixed(4) || 'N/A'}, MAE {metrics.mae?.toFixed(4) || 'N/A'}</p>
        )}
      </div>
    </div>
  );
};

export default ForecastDashboard;
