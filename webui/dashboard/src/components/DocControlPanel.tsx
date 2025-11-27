
import React, { useState, useEffect } from 'react';
import {
    getDocsSummary,
    getCanonicalDocs,
    getArchiveCandidateGroups,
    getUnreviewedBatch,
    getOrphans,
    getArchiveDryrun,
    SummaryData,
    CanonicalList,
    ArchiveCandidates,
    UnreviewedBatch,
    Orphans,
    ArchiveDryRun
} from '../utils/docsControlData';

const TabButton: React.FC<{
    active: boolean;
    onClick: () => void;
    children: React.ReactNode;
}> = ({ active, onClick, children }) => (
    <button
        onClick={onClick}
        className={`px-4 py-2 font-medium text-sm rounded-t-lg transition-colors ${active
            ? 'bg-white text-blue-600 border-t-2 border-blue-600 shadow-sm'
            : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
            }`}
    >
        {children}
    </button>
);

const SummaryTile: React.FC<{ title: string; value: number | string; subtext?: string }> = ({
    title,
    value,
    subtext,
}) => (
    <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-100">
        <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">{title}</h3>
        <div className="mt-1 text-2xl font-bold text-gray-900">{value}</div>
        {subtext && <div className="mt-1 text-xs text-gray-400">{subtext}</div>}
    </div>
);

const DocControlPanel: React.FC = () => {
    const [activeTab, setActiveTab] = useState('overview');
    const [summary, setSummary] = useState<SummaryData | null>(null);
    const [canonical, setCanonical] = useState<CanonicalList | null>(null);
    const [candidates, setCandidates] = useState<ArchiveCandidates | null>(null);
    const [unreviewed, setUnreviewed] = useState<UnreviewedBatch | null>(null);
    const [orphans, setOrphans] = useState<Orphans | null>(null);
    const [dryrun, setDryrun] = useState<ArchiveDryRun | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const loadData = async () => {
            setLoading(true);
            try {
                const [sum, can, cand, unrev, orph, dry] = await Promise.all([
                    getDocsSummary(),
                    getCanonicalDocs(),
                    getArchiveCandidateGroups(),
                    getUnreviewedBatch(),
                    getOrphans(),
                    getArchiveDryrun(),
                ]);
                setSummary(sum);
                setCanonical(can);
                setCandidates(cand);
                setUnreviewed(unrev);
                setOrphans(orph);
                setDryrun(dry);
                setError(null);
            } catch (err) {
                console.error(err);
                setError('Failed to load docs control data. Ensure "pmagent docs dashboard-refresh" has been run.');
            } finally {
                setLoading(false);
            }
        };
        loadData();
    }, []);

    if (loading) return <div className="p-8 text-center text-gray-500">Loading Doc Control Panel...</div>;
    if (error) return (
        <div className="p-8 text-center">
            <div className="text-red-600 font-medium mb-2">Error Loading Data</div>
            <div className="text-gray-500 text-sm">{error}</div>
        </div>
    );
    if (!summary) return null;

    return (
        <div className="p-6 max-w-7xl mx-auto bg-gray-50 h-full overflow-auto">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-2xl font-bold text-gray-900">Doc Control Panel</h1>
                <div className="text-xs text-gray-400">
                    Last Refreshed: {new Date(summary.generated_at).toLocaleString()}
                </div>
            </div>

            {/* Summary Strip */}
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
                <SummaryTile title="Total Docs" value={summary.totals.total} />
                <SummaryTile title="Canonical" value={summary.totals.canonical} subtext="SSOT & Reference" />
                <SummaryTile title="Archive Candidates" value={summary.totals.archive_candidates} subtext="Ready to move" />
                <SummaryTile title="Unreviewed" value={summary.totals.unreviewed} subtext="Needs triage" />
                <SummaryTile title="SSOT Ratio" value={`${Math.round((summary.path_buckets.ssot / summary.totals.total) * 100)}%`} subtext={`${summary.path_buckets.ssot} files`} />
            </div>

            {/* Tabs */}
            <div className="mb-6 border-b border-gray-200 flex gap-2">
                <TabButton active={activeTab === 'overview'} onClick={() => setActiveTab('overview')}>Overview</TabButton>
                <TabButton active={activeTab === 'canonical'} onClick={() => setActiveTab('canonical')}>Canonical</TabButton>
                <TabButton active={activeTab === 'candidates'} onClick={() => setActiveTab('candidates')}>Archive Candidates</TabButton>
                <TabButton active={activeTab === 'unreviewed'} onClick={() => setActiveTab('unreviewed')}>Unreviewed</TabButton>
                <TabButton active={activeTab === 'orphans'} onClick={() => setActiveTab('orphans')}>Orphans</TabButton>
            </div>

            {/* Tab Content */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                {activeTab === 'overview' && (
                    <div className="space-y-6">
                        <h2 className="text-lg font-semibold text-gray-800">System Status</h2>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div className="p-4 bg-blue-50 rounded-lg border border-blue-100">
                                <h3 className="font-medium text-blue-900 mb-2">Action Items</h3>
                                <ul className="list-disc list-inside text-sm text-blue-800 space-y-1">
                                    {summary.totals.unreviewed > 1000 && <li>High volume of unreviewed documents ({summary.totals.unreviewed})</li>}
                                    {summary.totals.archive_candidates > 500 && <li>Large batch of archive candidates ready ({summary.totals.archive_candidates})</li>}
                                    {orphans && orphans.categories.length > 0 && <li>Orphaned items detected ({orphans.categories.length} categories)</li>}
                                </ul>
                            </div>
                            <div className="p-4 bg-gray-50 rounded-lg border border-gray-100">
                                <h3 className="font-medium text-gray-900 mb-2">Storage Distribution</h3>
                                <div className="space-y-2 text-sm">
                                    <div className="flex justify-between"><span>SSOT</span> <span className="font-mono">{summary.path_buckets.ssot}</span></div>
                                    <div className="flex justify-between"><span>Archive</span> <span className="font-mono">{summary.path_buckets.archive}</span></div>
                                    <div className="flex justify-between"><span>Other</span> <span className="font-mono">{summary.path_buckets.other}</span></div>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {activeTab === 'canonical' && canonical && (
                    <div>
                        <div className="flex justify-between items-center mb-4">
                            <h2 className="text-lg font-semibold">Canonical Documents</h2>
                            <span className="text-sm text-gray-500">{canonical.total} items</span>
                        </div>
                        <div className="overflow-x-auto">
                            <table className="min-w-full divide-y divide-gray-200">
                                <thead className="bg-gray-50">
                                    <tr>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Path</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Last Modified</th>
                                    </tr>
                                </thead>
                                <tbody className="bg-white divide-y divide-gray-200">
                                    {canonical.items.map((doc) => (
                                        <tr key={doc.path}>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{doc.path}</td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                                <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${doc.doc_type === 'ssot' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                                                    }`}>
                                                    {doc.doc_type}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{new Date(doc.last_modified).toLocaleDateString()}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                )}

                {activeTab === 'candidates' && candidates && (
                    <div>
                        <div className="flex justify-between items-center mb-4">
                            <h2 className="text-lg font-semibold">Archive Candidates</h2>
                            <span className="text-sm text-gray-500">{candidates.total_items} items in {candidates.total_groups} groups</span>
                        </div>
                        <div className="grid grid-cols-1 gap-4">
                            {candidates.groups.map((group) => (
                                <div key={group.directory} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
                                    <div className="flex justify-between items-start">
                                        <div>
                                            <h3 className="font-medium text-gray-900">{group.directory}</h3>
                                            <p className="text-sm text-gray-500 mt-1">{group.notes}</p>
                                            <div className="mt-2 text-xs text-gray-400">
                                                Examples: {group.example_paths.join(', ')}
                                            </div>
                                        </div>
                                        <div className="text-right">
                                            <span className={`inline-block px-2 py-1 text-xs font-semibold rounded ${group.confidence === 'safe_cluster' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                                                }`}>
                                                {group.confidence === 'safe_cluster' ? 'Safe' : 'Mixed'}
                                            </span>
                                            <div className="mt-1 text-sm font-bold text-gray-700">{group.count} files</div>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                        {dryrun && (
                            <div className="mt-8 pt-6 border-t border-gray-200">
                                <h3 className="text-md font-semibold mb-2">Dry Run Plan</h3>
                                <p className="text-sm text-gray-600 mb-4">
                                    Ready to move {dryrun.total_candidates} files.
                                </p>
                                <div className="bg-gray-900 text-gray-100 p-4 rounded text-xs font-mono overflow-x-auto">
                                    {dryrun.items.slice(0, 5).map((item, i) => (
                                        <div key={i} className="mb-1">
                                            mv {item.from} -&gt; {item.to}
                                        </div>
                                    ))}
                                    {dryrun.items.length > 5 && <div className="text-gray-500">... and {dryrun.items.length - 5} more</div>}
                                </div>
                            </div>
                        )}
                    </div>
                )}

                {activeTab === 'unreviewed' && unreviewed && (
                    <div>
                        <div className="flex justify-between items-center mb-4">
                            <h2 className="text-lg font-semibold">Unreviewed Batch</h2>
                            <span className="text-sm text-gray-500">Batch Size: {unreviewed.batch_size} | Remaining: ~{unreviewed.remaining_estimate}</span>
                        </div>
                        <div className="space-y-4">
                            {unreviewed.items.map((doc) => (
                                <div key={doc.path} className="border rounded-lg p-4">
                                    <div className="flex justify-between mb-2">
                                        <h3 className="font-medium text-gray-900">{doc.path}</h3>
                                        <span className="text-xs text-gray-500">{new Date(doc.last_modified).toLocaleDateString()}</span>
                                    </div>
                                    <div className="text-sm text-gray-600 bg-gray-50 p-2 rounded mb-2 font-mono text-xs">
                                        {doc.snippet}
                                    </div>
                                    <div className="flex gap-2 text-xs">
                                        <span className="px-2 py-1 bg-blue-50 text-blue-700 rounded">Guess: {doc.guess}</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {activeTab === 'orphans' && orphans && (
                    <div>
                        <h2 className="text-lg font-semibold mb-4">Orphans & Backups</h2>
                        <div className="space-y-6">
                            {orphans.categories.map((cat) => (
                                <div key={cat.name} className="border rounded-lg p-4">
                                    <h3 className="font-medium text-gray-900 mb-1 capitalize">{cat.name.replace('_', ' ')}</h3>
                                    <p className="text-sm text-gray-500 mb-3">{cat.description}</p>
                                    <ul className="space-y-2">
                                        {cat.items.map((item) => (
                                            <li key={item.path} className="text-sm flex justify-between items-center bg-gray-50 p-2 rounded">
                                                <span className="font-mono text-gray-700">{item.path}</span>
                                                <span className="text-xs text-gray-500">
                                                    {item.type === 'directory' ? `${item.item_count} items` : `${(item.size_bytes || 0 / 1024).toFixed(1)} KB`}
                                                </span>
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default DocControlPanel;
