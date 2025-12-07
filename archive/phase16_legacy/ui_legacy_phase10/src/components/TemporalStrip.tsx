import React from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer, Legend } from "recharts";

type PatternPoint = { idx: number; value?: number; forecast?: number; lower?: number; upper?: number; };

function useTemporalData(): { data: PatternPoint[]; meta: any } {
  let tp: any = { patterns: [], metadata: {} };
  let fc: any = {};
  try { tp = require("../../out/temporal_patterns.json"); } catch {}
  try { fc = require("../../out/pattern_forecast.json"); } catch {}

  // Minimal stub: render index vs value; extend later to real rolling metrics
  const rolling = Array.isArray(tp.patterns) ? tp.patterns : [];
  const data: PatternPoint[] = rolling.map((_: any, i: number) => ({ idx: i, value: undefined }));
  return { data, meta: tp.metadata || {} };
}

const TemporalStrip: React.FC = () => {
  const { data, meta } = useTemporalData();
  return (
    <div className="w-full h-64">
      <div className="text-sm opacity-70 mb-2">Temporal Strip — {meta?.analyzed_books?.[0] ?? "—"}</div>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="idx" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="value" name="Rolling Value" dot={false} />
          <Line type="monotone" dataKey="forecast" name="Forecast" strokeDasharray="4 4" dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};
export default TemporalStrip;
