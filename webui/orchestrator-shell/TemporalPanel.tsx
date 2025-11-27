import React from "react";
import { TileExpandedProps } from "./tileRegistry";

export default function TemporalPanel({ data }: TileExpandedProps) {
    const patterns = data?.temporal_patterns || [];
    const metadata = data?.metadata || {};
    const params = metadata.analysis_parameters || {};

    return (
        <div className="p-6">
            <h2 className="text-2xl font-bold mb-6 flex items-center gap-3">
                <span className="text-3xl">🕒</span>
                Temporal Patterns
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="bg-white p-4 rounded-lg border shadow-sm">
                    <div className="text-sm text-gray-500 uppercase tracking-wider mb-1">Total Series</div>
                    <div className="text-2xl font-bold">{metadata.total_series || 0}</div>
                </div>
                <div className="bg-white p-4 rounded-lg border shadow-sm">
                    <div className="text-sm text-gray-500 uppercase tracking-wider mb-1">Books Analyzed</div>
                    <div className="text-2xl font-bold">{metadata.books_analyzed?.length || 0}</div>
                </div>
                <div className="bg-white p-4 rounded-lg border shadow-sm">
                    <div className="text-sm text-gray-500 uppercase tracking-wider mb-1">Window Size</div>
                    <div className="text-2xl font-bold">{params.default_window || '-'}</div>
                </div>
            </div>

            <div className="bg-white border rounded-lg overflow-hidden shadow-sm">
                <div className="px-6 py-4 border-b bg-gray-50">
                    <h3 className="font-semibold text-gray-700">Detected Patterns</h3>
                </div>

                {patterns.length > 0 ? (
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                            <tr>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Series ID</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Confidence</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Details</th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {patterns.map((p: any, i: number) => (
                                <tr key={i}>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{p.id}</td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{p.type}</td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{(p.confidence * 100).toFixed(1)}%</td>
                                    <td className="px-6 py-4 text-sm text-gray-500">{p.description}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                ) : (
                    <div className="p-8 text-center text-gray-500">
                        <p className="italic">No temporal patterns detected yet.</p>
                        <p className="text-xs mt-2">Run analysis to generate patterns.</p>
                    </div>
                )}
            </div>

            <div className="mt-6 text-xs text-gray-400 text-right">
                Analysis generated: {metadata.generated_at ? new Date(metadata.generated_at).toLocaleString() : 'Unknown'}
            </div>
        </div>
    );
}
