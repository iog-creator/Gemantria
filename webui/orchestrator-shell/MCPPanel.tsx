import React from "react";
import { TileExpandedProps } from "./tileRegistry";

export default function MCPPanel({ data }: TileExpandedProps) {
    const proofs = data?.proofs || {};
    const allOk = data?.all_ok || false;
    const proofCount = data?.proofs_count || 0;

    return (
        <div className="p-6">
            <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold flex items-center gap-3">
                    <span className="text-3xl">🔗</span>
                    MCP Bundle Proofs
                </h2>
                <div className={`px-4 py-2 rounded-full font-medium ${allOk ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                    {allOk ? 'All Systems Go' : 'Verification Issues Detected'}
                </div>
            </div>

            <div className="bg-white border rounded-lg overflow-hidden shadow-sm">
                <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Proof ID</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Generated At</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Details</th>
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                        {Object.entries(proofs).map(([key, val]: [string, any]) => (
                            <tr key={key} className="hover:bg-gray-50">
                                <td className="px-6 py-4 whitespace-nowrap font-medium text-gray-900">
                                    {key.toUpperCase().replace(/_/g, ' ')}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${val?.ok ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                                        {val?.ok ? 'PASS' : 'FAIL'}
                                    </span>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                    {val?.generated_at ? new Date(val.generated_at).toLocaleString() : '-'}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                    <pre className="text-xs bg-gray-50 p-1 rounded max-w-xs overflow-hidden text-ellipsis">
                                        {JSON.stringify(val, null, 0).slice(0, 50)}...
                                    </pre>
                                </td>
                            </tr>
                        ))}
                        {Object.keys(proofs).length === 0 && (
                            <tr>
                                <td colSpan={4} className="px-6 py-8 text-center text-gray-500 italic">
                                    No proofs found in bundle.
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>

            <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-blue-50 p-4 rounded-lg border border-blue-100">
                    <div className="text-blue-800 text-sm font-medium uppercase mb-1">Total Proofs</div>
                    <div className="text-2xl font-bold text-blue-900">{proofCount}</div>
                </div>
                <div className="bg-green-50 p-4 rounded-lg border border-green-100">
                    <div className="text-green-800 text-sm font-medium uppercase mb-1">Passing</div>
                    <div className="text-2xl font-bold text-green-900">
                        {Object.values(proofs).filter((p: any) => p?.ok).length}
                    </div>
                </div>
                <div className="bg-red-50 p-4 rounded-lg border border-red-100">
                    <div className="text-red-800 text-sm font-medium uppercase mb-1">Failing</div>
                    <div className="text-2xl font-bold text-red-900">
                        {Object.values(proofs).filter((p: any) => !p?.ok).length}
                    </div>
                </div>
            </div>

            <div className="mt-6 text-xs text-gray-400 text-right">
                Bundle generated: {data?.generated_at ? new Date(data.generated_at).toLocaleString() : 'Unknown'}
            </div>
        </div>
    );
}
