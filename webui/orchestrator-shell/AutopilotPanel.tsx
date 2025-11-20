import React from 'react';
import { useAutopilot, AutopilotCommand } from './useAutopilot';

const StatusBadge: React.FC<{ status: AutopilotCommand['status'] }> = ({ status }) => {
    const getStatusColor = (s: AutopilotCommand['status']) => {
        switch (s) {
            case 'success':
                return 'bg-green-500';
            case 'error':
                return 'bg-red-500';
            case 'running':
                return 'bg-yellow-500';
            default:
                return 'bg-gray-500';
        }
    };

    const getStatusText = (s: AutopilotCommand['status']) => {
        switch (s) {
            case 'success':
                return 'Success';
            case 'error':
                return 'Error';
            case 'running':
                return 'Running';
            default:
                return 'Idle';
        }
    };

    return (
        <div className="flex items-center gap-2">
            <div className={`w-3 h-3 rounded-full ${getStatusColor(status)}`} />
            <span className="text-sm font-medium">{getStatusText(status)}</span>
        </div>
    );
};

const CommandCard: React.FC<{ command: AutopilotCommand }> = ({ command }) => {
    return (
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
            <div className="flex items-start justify-between mb-2">
                <div className="flex-1">
                    <h3 className="font-semibold text-lg">{command.description}</h3>
                    <p className="text-sm text-gray-600 font-mono mt-1">{command.id}</p>
                </div>
                <StatusBadge status={command.status} />
            </div>

            {command.lastRun && (
                <div className="text-xs text-gray-500 mb-2">
                    Last run: {new Date(command.lastRun).toLocaleString()}
                </div>
            )}

            {command.output && (
                <details className="mt-3">
                    <summary className="cursor-pointer text-sm font-medium text-gray-700 hover:text-gray-900">
                        View output
                    </summary>
                    <pre className="mt-2 p-3 bg-gray-50 rounded text-xs overflow-x-auto max-h-64 overflow-y-auto">
                        {command.output}
                    </pre>
                </details>
            )}

            {command.status === 'error' && command.output && (
                <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded text-sm text-red-800">
                    <strong>Error:</strong> Command execution failed. Check output for details.
                </div>
            )}
        </div>
    );
};

export default function AutopilotPanel() {
    const { commands, loading, allowedCommands } = useAutopilot();

    if (loading) {
        return (
            <div className="p-8">
                <p>Loading Autopilot commands...</p>
            </div>
        );
    }

    return (
        <div className="p-8 space-y-6">
            <div>
                <h1 className="text-2xl font-bold mb-2">Autopilot</h1>
                <p className="text-gray-600 mb-4">
                    Local, hermetic executor for pmagent commands. Commands are executed via{' '}
                    <code className="text-xs bg-gray-100 px-1 py-0.5 rounded">autopilotRunner.ts</code> and
                    results are written to static log files in <code className="text-xs bg-gray-100 px-1 py-0.5 rounded">share/autopilot/</code>.
                </p>
                <div className="bg-blue-50 border border-blue-200 rounded p-4 mb-6">
                    <h3 className="font-semibold mb-2">How to use:</h3>
                    <ol className="list-decimal list-inside space-y-1 text-sm">
                        <li>Run a command manually: <code className="bg-white px-1 rounded">node webui/orchestrator-shell/autopilotRunner.ts &lt;command-id&gt;</code></li>
                        <li>Or use npm script: <code className="bg-white px-1 rounded">npm run autopilot:run &lt;command-id&gt;</code></li>
                        <li>This panel will automatically poll and display the latest results</li>
                    </ol>
                    <p className="text-sm mt-3">
                        <strong>Allowed commands:</strong>{' '}
                        {Object.keys(allowedCommands).join(', ')}
                    </p>
                </div>
            </div>

            <div className="space-y-4">
                <h2 className="text-xl font-bold">Command Status</h2>
                {commands.length === 0 ? (
                    <div className="bg-gray-50 border border-gray-200 rounded p-4 text-center text-gray-600">
                        No commands available. Check allowlist configuration.
                    </div>
                ) : (
                    commands.map((cmd) => <CommandCard key={cmd.id} command={cmd} />)
                )}
            </div>

            <div className="bg-yellow-50 border border-yellow-200 rounded p-4">
                <h3 className="font-semibold mb-2">Security Note</h3>
                <p className="text-sm">
                    Autopilot uses a <strong>strict allowlist</strong> of commands. Only the following commands
                    are permitted: <code className="bg-white px-1 rounded">{Object.keys(allowedCommands).join(', ')}</code>.
                    No arbitrary command execution is allowed.
                </p>
            </div>
        </div>
    );
}

