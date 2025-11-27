import React from "react";
import { TileExpandedProps } from "./tileRegistry";

export default function ForecastPanel({ data }: TileExpandedProps) {
    const forecasts = data?.forecasts || [];
    const metadata = data?.metadata || {};
    const params = metadata.forecast_parameters || {};
    const distribution = metadata.model_distribution || {};

    return (
        <div className="p-6">
            <h2 className="text-2xl font-bold mb-6 flex items-center gap-3">
                <span className="text-3xl">📈</span>
                Pattern Forecasts
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                <div className="bg-white p-4 rounded-lg border shadow-sm">
                    <div className="text-sm text-gray-500 uppercase tracking-wider mb-1">Total Forecasts</div>
                    <div className="text-2xl font-bold">{metadata.total_forecasts || 0}</div>
                </div>
                <div className="bg-white p-4 rounded-lg border shadow-sm">
                    <div className="text-sm text-gray-500 uppercase tracking-wider mb-1">Horizon</div>
                    <div className="text-2xl font-bold">{params.default_horizon || '-'}</div>
                </div>
                <div className="bg-white p-4 rounded-lg border shadow-sm">
                    <div className="text-sm text-gray-500 uppercase tracking-wider mb-1">Avg RMSE</div>
                    <div className="text-2xl font-bold">{metadata.average_metrics?.rmse?.toFixed(4) || '0.0000'}</div>
                </div>
                <div className="bg-white p-4 rounded-lg border shadow-sm">
                    <div className="text-sm text-gray-500 uppercase tracking-wider mb-1">Models</div>
                    <div className="text-xs text-gray-600 mt-1">
                        {Object.entries(distribution).map(([k, v]) => (
                            <div key={k} className="flex justify-between">
                                <span className="uppercase">{k}</span>
                                <span className="font-mono">{v as number}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            <div className="bg-white border rounded-lg overflow-hidden shadow-sm">
                <div className="px-6 py-4 border-b bg-gray-50">
                    <h3 className="font-semibold text-gray-700">Forecast Data</h3>
                </div>

                {forecasts.length > 0 ? (
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                            <tr>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Target</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Model</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Next Value</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Trend</th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {forecasts.map((f: any, i: number) => (
                                <tr key={i}>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{f.target}</td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{f.model}</td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{f.next_value?.toFixed(2)}</td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${f.trend === 'up' ? 'bg-green-100 text-green-800' : f.trend === 'down' ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-800'}`}>
                                            {f.trend?.toUpperCase()}
                                        </span>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                ) : (
                    <div className="p-8 text-center text-gray-500">
                        <p className="italic">No forecasts generated yet.</p>
                        <p className="text-xs mt-2">Run forecast models to generate predictions.</p>
                    </div>
                )}
            </div>

            <div className="mt-6 text-xs text-gray-400 text-right">
                Forecast generated: {metadata.generated_at ? new Date(metadata.generated_at).toLocaleString() : 'Unknown'}
            </div>
        </div>
    );
}
