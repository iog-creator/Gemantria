import { useState, useEffect } from 'react';

export interface AutopilotCommand {
    id: string;
    description: string;
    lastRun: string | null;
    status: 'idle' | 'running' | 'success' | 'error';
    output: string | null;
}

export interface AutopilotLog {
    commandId: string;
    timestamp: string;
    success: boolean;
    output: string;
    error?: string;
}

const ALLOWED_COMMANDS: Record<string, { command: string; description: string }> = {
    health: {
        command: 'pmagent health',
        description: 'System health check (DB + LM + Graph)',
    },
    control_summary: {
        command: 'pmagent control summary',
        description: 'Control-plane summary (aggregated status)',
    },
    docs_status: {
        command: 'pmagent docs status',
        description: 'Documentation status and inventory',
    },
    ledger_verify: {
        command: 'pmagent ledger verify',
        description: 'Verify ledger artifacts are current',
    },
    reality_green: {
        command: 'make reality.green',
        description: 'Full system truth gate (reality.green)',
    },
};

const LOG_FILES: Record<string, string> = {
    health: 'health.log',
    control_summary: 'control_summary.log',
    docs_status: 'docs_status.log',
    ledger_verify: 'ledger_verify.log',
    reality_green: 'reality_green.log',
};

/**
 * Parse log file content into structured format
 */
function parseLogFile(content: string): AutopilotLog | null {
    try {
        const timestampMatch = content.match(/Timestamp: (.+)/);
        const successMatch = content.match(/Success: (true|false)/);
        const errorMatch = content.match(/Error: (.+)/);
        const outputMatch = content.match(/--- Output ---\n([\s\S]*?)\n--- End Output ---/);

        if (!timestampMatch || !successMatch || !outputMatch) {
            return null;
        }

        return {
            commandId: '',
            timestamp: timestampMatch[1],
            success: successMatch[1] === 'true',
            output: outputMatch[1].trim(),
            error: errorMatch ? errorMatch[1] : undefined,
        };
    } catch {
        return null;
    }
}

/**
 * Fetch log file from static exports
 */
async function fetchLogFile(commandId: string): Promise<AutopilotLog | null> {
    const logFile = LOG_FILES[commandId];
    if (!logFile) {
        return null;
    }

    try {
        // Try to fetch from static exports (same pattern as other panels)
        const response = await fetch(`/exports/autopilot/${logFile}`);
        if (!response.ok) {
            return null;
        }
        const content = await response.text();
        const log = parseLogFile(content);
        if (log) {
            log.commandId = commandId;
        }
        return log;
    } catch {
        return null;
    }
}

/**
 * Hook to manage Autopilot commands and read log files
 */
export function useAutopilot() {
    const [commands, setCommands] = useState<AutopilotCommand[]>([]);
    const [loading, setLoading] = useState(true);

    // Initialize commands from allowlist
    useEffect(() => {
        const initialCommands: AutopilotCommand[] = Object.entries(ALLOWED_COMMANDS).map(([id, cmd]) => ({
            id,
            description: cmd.description,
            lastRun: null,
            status: 'idle',
            output: null,
        }));
        setCommands(initialCommands);
        setLoading(false);
    }, []);

    // Poll log files periodically
    useEffect(() => {
        if (loading) {
            return;
        }

        const pollLogs = async () => {
            const updatedCommands = await Promise.all(
                commands.map(async (cmd) => {
                    const log = await fetchLogFile(cmd.id);
                    if (log) {
                        return {
                            ...cmd,
                            lastRun: log.timestamp,
                            status: log.success ? 'success' : 'error',
                            output: log.output,
                        };
                    }
                    return cmd;
                })
            );
            setCommands(updatedCommands);
        };

        // Initial load
        pollLogs();

        // Poll every 5 seconds
        const interval = setInterval(pollLogs, 5000);
        return () => clearInterval(interval);
    }, [loading, commands.length]);

    return {
        commands,
        loading,
        allowedCommands: ALLOWED_COMMANDS,
    };
}

