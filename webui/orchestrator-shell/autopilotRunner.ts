#!/usr/bin/env node
/**
 * Autopilot Runner - Local, hermetic executor for pmagent commands
 * 
 * Executes allowed pmagent commands and writes output to static log files
 * in share/autopilot/. This script uses a strict allowlist - no arbitrary
 * command execution.
 * 
 * Usage:
 *   node autopilotRunner.ts <command-id>
 * 
 * Or via npm script:
 *   npm run autopilot:run <command-id>
 */

import { execSync } from 'child_process';
import { writeFileSync, mkdirSync } from 'fs';
import { join } from 'path';

// Strict allowlist of allowed commands
const ALLOWED_COMMANDS: Record<string, { command: string; description: string }> = {
    'health': {
        command: 'pmagent health',
        description: 'System health check (DB + LM + Graph)',
    },
    'control_summary': {
        command: 'pmagent control summary',
        description: 'Control-plane summary (aggregated status)',
    },
    'docs_status': {
        command: 'pmagent docs status',
        description: 'Documentation status and inventory',
    },
    'ledger_verify': {
        command: 'pmagent ledger verify',
        description: 'Verify ledger artifacts are current',
    },
    'reality_green': {
        command: 'make reality.green',
        description: 'Full system truth gate (reality.green)',
    },
};

// Log file mapping
const LOG_FILES: Record<string, string> = {
    'health': 'health.log',
    'control_summary': 'control_summary.log',
    'docs_status': 'docs_status.log',
    'ledger_verify': 'ledger_verify.log',
    'reality_green': 'reality_green.log',
};

const AUTOPILOT_DIR = join(process.cwd(), 'share', 'autopilot');

function ensureAutopilotDir(): void {
    try {
        mkdirSync(AUTOPILOT_DIR, { recursive: true });
    } catch (error) {
        // Directory might already exist, ignore
    }
}

function executeCommand(commandId: string): { success: boolean; output: string; error?: string } {
    const cmd = ALLOWED_COMMANDS[commandId];
    if (!cmd) {
        return {
            success: false,
            output: '',
            error: `Command "${commandId}" is not in the allowlist. Allowed commands: ${Object.keys(ALLOWED_COMMANDS).join(', ')}`,
        };
    }

    try {
        const output = execSync(cmd.command, {
            encoding: 'utf-8',
            stdio: ['ignore', 'pipe', 'pipe'],
            cwd: process.cwd(),
            env: process.env,
        });
        return { success: true, output };
    } catch (error: any) {
        const errorOutput = error.stdout || error.stderr || error.message || String(error);
        return {
            success: false,
            output: errorOutput,
            error: error.message || 'Command execution failed',
        };
    }
}

function writeLog(commandId: string, result: { success: boolean; output: string; error?: string }): void {
    const logFile = LOG_FILES[commandId];
    if (!logFile) {
        console.error(`No log file mapping for command: ${commandId}`);
        return;
    }

    const logPath = join(AUTOPILOT_DIR, logFile);
    const timestamp = new Date().toISOString();
    const logContent = `=== Autopilot Run: ${commandId} ===
Timestamp: ${timestamp}
Success: ${result.success}
${result.error ? `Error: ${result.error}\n` : ''}
--- Output ---
${result.output}
--- End Output ---
`;

    try {
        writeFileSync(logPath, logContent, 'utf-8');
        console.log(`Log written to: ${logPath}`);
    } catch (error) {
        console.error(`Failed to write log file: ${error}`);
        process.exit(1);
    }
}

function main(): void {
    const commandId = process.argv[2];

    if (!commandId) {
        console.error('Usage: node autopilotRunner.ts <command-id>');
        console.error(`\nAllowed commands:\n${Object.entries(ALLOWED_COMMANDS).map(([id, cmd]) => `  ${id}: ${cmd.description}`).join('\n')}`);
        process.exit(1);
    }

    ensureAutopilotDir();

    console.log(`Executing: ${ALLOWED_COMMANDS[commandId]?.command || commandId}`);
    const result = executeCommand(commandId);
    writeLog(commandId, result);

    if (result.success) {
        console.log('Command executed successfully');
        process.exit(0);
    } else {
        console.error('Command execution failed:', result.error);
        process.exit(1);
    }
}

if (require.main === module) {
    main();
}

export { ALLOWED_COMMANDS, LOG_FILES, executeCommand, writeLog };

