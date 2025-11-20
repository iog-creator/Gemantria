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
        <div className="orchestrator-header flex gap-4 p-4 bg-gray-800 text-white">
            <div className="tile flex items-center gap-2" title={getStatusMessage('DB', db.status, db.reason)}>
                <div className={`w-3 h-3 rounded-full ${getStatusColor(db.status)}`} />
                <span>DB</span>
                {db.status !== 'unknown' && db.reason && <span className="text-xs text-gray-400">({db.reason})</span>}
            </div>
            <div className="tile flex items-center gap-2" title={getStatusMessage('LM', lm.status, lm.reason)}>
                <div className={`w-3 h-3 rounded-full ${getStatusColor(lm.status)}`} />
                <span>LM</span>
                {lm.status !== 'unknown' && lm.reason && <span className="text-xs text-gray-400">({lm.reason})</span>}
            </div>
            <div className="tile flex items-center gap-2" title={getStatusMessage('System', system.status)}>
                <div className={`w-3 h-3 rounded-full ${getStatusColor(system.status)}`} />
                <span>System</span>
            </div>
        </div>
    );
}
