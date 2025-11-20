import React from 'react';
import { useComplianceData, ComplianceLevel, ViolationItem } from './useComplianceData';

const ComplianceBadge: React.FC<{ level: ComplianceLevel | null }> = ({ level }) => {
    const getStatusColor = (l: ComplianceLevel | null) => {
        switch (l) {
            case 'OK':
                return 'bg-green-500';
            case 'WARN':
                return 'bg-yellow-500';
            case 'ERROR':
                return 'bg-red-500';
            default:
                return 'bg-gray-500';
        }
    };

    const getStatusText = (l: ComplianceLevel | null) => {
        switch (l) {
            case 'OK':
                return 'OK';
            case 'WARN':
                return 'WARN';
            case 'ERROR':
                return 'ERROR';
            default:
                return 'Unknown';
        }
    };

    return (
        <div className="flex items-center gap-2">
            <div className={`w-4 h-4 rounded-full ${getStatusColor(level)}`} />
            <span className="font-semibold text-xl">{getStatusText(level)}</span>
        </div>
    );
};

const SeverityBadge: React.FC<{ severity: 'HINT' | 'WARN' | 'ERROR' }> = ({ severity }) => {
    const getColor = (s: string) => {
        switch (s) {
            case 'ERROR':
                return 'bg-red-100 text-red-800 border-red-300';
            case 'WARN':
                return 'bg-yellow-100 text-yellow-800 border-yellow-300';
            default:
                return 'bg-blue-100 text-blue-800 border-blue-300';
        }
    };

    return (
        <span
            className={`px-2 py-1 text-xs font-semibold rounded border ${getColor(severity)}`}
        >
            {severity}
        </span>
    );
};

const ViolationsList: React.FC<{ violations: ViolationItem[]; windowLabel: string }> = ({
    violations,
    windowLabel,
}) => {
    if (violations.length === 0) {
        return (
            <div className="text-sm text-gray-500 italic">
                No violations recorded in {windowLabel}.
            </div>
        );
    }

    return (
        <div className="space-y-2">
            {violations.map((violation, idx) => (
                <div
                    key={idx}
                    className="flex items-center justify-between py-2 px-3 bg-gray-50 rounded border border-gray-200"
                >
                    <div className="flex items-center gap-3">
                        <span className="font-mono text-sm font-medium text-gray-900">
                            {violation.violation_code}
                        </span>
                        {violation.rule_title && (
                            <span className="text-sm text-gray-600">{violation.rule_title}</span>
                        )}
                    </div>
                    <div className="flex items-center gap-3">
                        <SeverityBadge severity={violation.severity || 'HINT'} />
                        <span className="text-sm font-medium text-gray-700">
                            {violation.count} {violation.count === 1 ? 'occurrence' : 'occurrences'}
                        </span>
                    </div>
                </div>
            ))}
        </div>
    );
};

export default function CompliancePanel() {
    const compliance = useComplianceData();

    // Determine if we have any data
    const hasData =
        compliance.level !== null ||
        compliance.top7d.length > 0 ||
        compliance.top30d.length > 0;

    return (
        <div className="p-6 max-w-7xl mx-auto bg-gray-50 min-h-screen">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-2xl font-bold text-gray-900">Compliance</h1>
                {compliance.lastRunAt && (
                    <div className="text-xs text-gray-400">
                        Last Updated: {new Date(compliance.lastRunAt).toLocaleString()}
                    </div>
                )}
            </div>

            {!hasData ? (
                // Empty/offline state
                <div className="bg-white p-8 rounded-lg shadow-sm border border-gray-200 text-center">
                    <h2 className="text-lg font-semibold text-gray-700 mb-2">
                        Compliance data not available
                    </h2>
                    <p className="text-gray-600 mb-4">
                        Check compliance export targets (PLAN-076/078) or run{' '}
                        <code className="bg-gray-100 px-2 py-1 rounded text-xs">
                            make reality.green
                        </code>
                        .
                    </p>
                </div>
            ) : (
                <div className="space-y-6">
                    {/* Compliance Posture Card */}
                    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                        <h2 className="text-lg font-semibold text-gray-900 mb-4">
                            Compliance Posture
                        </h2>
                        <div className="mb-4">
                            <ComplianceBadge level={compliance.level} />
                        </div>
                        <p className="text-base text-gray-700 mb-4">{compliance.headline}</p>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                            <div>
                                <span className="text-gray-500">Checks:</span>{' '}
                                <span className="font-medium">{compliance.stats.totalChecks}</span>
                            </div>
                            <div>
                                <span className="text-gray-500">Hints:</span>{' '}
                                <span className="font-medium text-blue-600">
                                    {compliance.stats.totalHints}
                                </span>
                            </div>
                            <div>
                                <span className="text-gray-500">Warnings:</span>{' '}
                                <span className="font-medium text-yellow-600">
                                    {compliance.stats.totalWarnings}
                                </span>
                            </div>
                            <div>
                                <span className="text-gray-500">Errors:</span>{' '}
                                <span className="font-medium text-red-600">
                                    {compliance.stats.totalErrors}
                                </span>
                            </div>
                        </div>
                    </div>

                    {/* Top Violations - Last 7 Days */}
                    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                        <h2 className="text-lg font-semibold text-gray-900 mb-4">
                            Top Violations — Last 7 Days
                        </h2>
                        <ViolationsList violations={compliance.top7d} windowLabel="last 7 days" />
                    </div>

                    {/* Top Violations - Last 30 Days */}
                    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                        <h2 className="text-lg font-semibold text-gray-900 mb-4">
                            Top Violations — Last 30 Days
                        </h2>
                        <ViolationsList
                            violations={compliance.top30d}
                            windowLabel="last 30 days"
                        />
                    </div>

                    {/* Signals / Notes */}
                    {compliance.hints.length > 0 && (
                        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                            <h2 className="text-lg font-semibold text-gray-900 mb-4">Signals</h2>
                            <ul className="space-y-2">
                                {compliance.hints.map((hint, idx) => (
                                    <li key={idx} className="flex items-start gap-2 text-sm text-gray-700">
                                        <span className="text-gray-400 mt-0.5">•</span>
                                        <span>{hint}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}

                    {/* WHEN/THEN messaging for missing data */}
                    {compliance.level === 'WARN' &&
                        compliance.hints.some(
                            (h) => h.includes('not found') || h.includes('unavailable')
                        ) && (
                            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                                <h3 className="font-semibold text-yellow-900 mb-2">WHEN/THEN</h3>
                                <div className="text-sm text-yellow-800 space-y-1">
                                    <p>
                                        <strong>Some compliance data is missing.</strong> When
                                        compliance exports are available, this panel will show live
                                        guard and rules posture.
                                    </p>
                                    <p className="text-xs mt-2">
                                        Run{' '}
                                        <code className="bg-yellow-100 px-1 py-0.5 rounded">
                                            make reality.green
                                        </code>{' '}
                                        to verify system state and compliance exports.
                                    </p>
                                </div>
                            </div>
                        )}
                </div>
            )}
        </div>
    );
}

