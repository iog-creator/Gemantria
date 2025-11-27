import React from "react";
import { useHeaderData } from "./useHeaderData";

export default function Header() {
    const { db, lm, system } = useHeaderData();

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'healthy': return 'bg-green-500';
            case 'degraded': return 'bg-yellow-500';
            case 'offline': return 'bg-red-500';
            default: return 'bg-gray-500';
        }
    };

    const getStatusMessage = (label: string, status: string, reason?: string) => {
        if (status === 'unknown') {
            return `When ${label} health exports are available, this tile will show live status.`;
        }
        if (status === 'offline') {
            if (label === 'DB') {
                return 'When Postgres is available and DB health passes, this will show live status.';
            }
            if (label === 'LM') {
                return 'When LM Studio is reachable, this will show the active model.';
            }
        }
        return reason || status;
    };

    return (
        <div className="orchestrator-header flex gap-6 px-6 py-4 bg-gray-900/95 backdrop-blur-xl border-b border-white/10 text-white items-center shadow-lg z-20">
            <div className="flex items-center gap-3 mr-4">
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 shadow-[0_0_15px_rgba(59,130,246,0.3)] flex items-center justify-center font-bold text-white">
                    G
                </div>
                <span className="font-bold text-lg tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">Gemantria</span>
            </div>

            <div className="h-6 w-px bg-white/10 mx-2" />

            <div className="tile flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/5 border border-white/10 hover:bg-white/10 transition-colors cursor-help" title={getStatusMessage('DB', db.status, db.reason)}>
                <div className={`w-2.5 h-2.5 rounded-full shadow-[0_0_8px_currentColor] ${getStatusColor(db.status)}`} />
                <span className="text-sm font-medium text-gray-300">DB</span>
                {db.status !== 'unknown' && db.reason && <span className="text-xs text-gray-500">({db.reason})</span>}
            </div>
            <div className="tile flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/5 border border-white/10 hover:bg-white/10 transition-colors cursor-help" title={getStatusMessage('LM', lm.status, lm.reason)}>
                <div className={`w-2.5 h-2.5 rounded-full shadow-[0_0_8px_currentColor] ${getStatusColor(lm.status)}`} />
                <span className="text-sm font-medium text-gray-300">LM</span>
                {lm.status !== 'unknown' && lm.reason && <span className="text-xs text-gray-500">({lm.reason})</span>}
            </div>
            <div className="tile flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/5 border border-white/10 hover:bg-white/10 transition-colors cursor-help" title={getStatusMessage('System', system.status)}>
                <div className={`w-2.5 h-2.5 rounded-full shadow-[0_0_8px_currentColor] ${getStatusColor(system.status)}`} />
                <span className="text-sm font-medium text-gray-300">System</span>
            </div>
        </div>
    );
}
