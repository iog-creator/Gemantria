import React, { useState, useEffect } from 'react';
import SemanticSearchTab from './SemanticSearchTab';
import CrossLanguageTab from './CrossLanguageTab';
import SearchTab from './SearchTab';
import LexiconTab from './LexiconTab';
import InsightsTab from './InsightsTab';

interface BibleScholarSummary {
    status?: string;
    version?: string;
    generated_at?: string;
}

const TabButton: React.FC<{
    active: boolean;
    onClick: () => void;
    children: React.ReactNode;
}> = ({ active, onClick, children }) => (
    <button
        onClick={onClick}
        className={`px-4 py-2 font-medium text-sm rounded-t-lg transition-colors ${
            active
                ? 'bg-white text-blue-600 border-t-2 border-blue-600 shadow-sm'
                : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
        }`}
    >
        {children}
    </button>
);

async function fetchJsonSafe<T>(path: string): Promise<T | null> {
    try {
        const response = await fetch(path);
        if (!response.ok) {
            return null;
        }
        return await response.json();
    } catch (error) {
        console.error(`Failed to fetch ${path}:`, error);
        return null;
    }
}

type TabName = 'semantic' | 'crosslang' | 'search' | 'lexicon' | 'insights';

export default function BibleScholarPanel() {
    const [activeTab, setActiveTab] = useState<TabName>('semantic');
    const [summary, setSummary] = useState<BibleScholarSummary | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadData = async () => {
            setLoading(true);
            try {
                const data = await fetchJsonSafe<BibleScholarSummary>('/exports/biblescholar/summary.json');
                if (data) {
                    setSummary(data);
                }
            } catch (err) {
                console.error('Failed to load BibleScholar summary:', err);
            } finally {
                setLoading(false);
            }
        };
        loadData();
    }, []);

    return (
        <div className="p-6 max-w-7xl mx-auto bg-gray-50 min-h-screen">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-2xl font-bold text-gray-900">BibleScholar</h1>
                {summary?.generated_at && (
                    <div className="text-xs text-gray-400">
                        Last Updated: {new Date(summary.generated_at).toLocaleString()}
                    </div>
                )}
            </div>

            {/* Summary Card */}
            {summary && (
                <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200 mb-6">
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-green-500" />
                        <span className="font-medium">Status: {summary.status || 'active'}</span>
                        {summary.version && (
                            <span className="text-sm text-gray-500">v{summary.version}</span>
                        )}
                    </div>
                </div>
            )}

            {/* Tabs */}
            <div className="mb-6 border-b border-gray-200 flex gap-2">
                <TabButton active={activeTab === 'semantic'} onClick={() => setActiveTab('semantic')}>
                    Semantic Search
                </TabButton>
                <TabButton active={activeTab === 'crosslang'} onClick={() => setActiveTab('crosslang')}>
                    Cross-Language
                </TabButton>
                <TabButton active={activeTab === 'search'} onClick={() => setActiveTab('search')}>
                    Search
                </TabButton>
                <TabButton active={activeTab === 'lexicon'} onClick={() => setActiveTab('lexicon')}>
                    Lexicon
                </TabButton>
                <TabButton active={activeTab === 'insights'} onClick={() => setActiveTab('insights')}>
                    Insights
                </TabButton>
            </div>

            {/* Tab Content */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                {activeTab === 'semantic' && <SemanticSearchTab />}
                {activeTab === 'crosslang' && <CrossLanguageTab />}
                {activeTab === 'search' && <SearchTab />}
                {activeTab === 'lexicon' && <LexiconTab />}
                {activeTab === 'insights' && <InsightsTab />}
            </div>
        </div>
    );
}

