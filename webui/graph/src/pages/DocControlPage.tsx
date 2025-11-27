import React, { useState, useEffect } from 'react';

interface CanonicalDoc {
  path: string;
  title: string;
  doc_type: string;
  status: string;
  is_canonical: boolean;
  last_modified: string;
  size_bytes: number;
}

interface CanonicalResponse {
  ok: boolean;
  items: CanonicalDoc[];
  total: number;
  generated_at?: string;
  error?: string;
}

interface ArchiveGroup {
  directory: string;
  count: number;
  example_paths: string[];
  confidence: string;
  notes?: string;
}

interface ArchiveCandidatesResponse {
  ok: boolean;
  groups: ArchiveGroup[];
  total_groups: number;
  total_items: number;
  generated_at?: string;
  error?: string;
}

const DocControlPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'canonical' | 'archive'>('canonical');
  const [canonicalData, setCanonicalData] = useState<CanonicalResponse | null>(null);
  const [archiveData, setArchiveData] = useState<ArchiveCandidatesResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      setError(null);
      try {
        if (activeTab === 'canonical') {
          const res = await fetch('/api/docs/control/canonical');
          if (!res.ok) {
            throw new Error(`Failed to load canonical documents: ${res.statusText}`);
          }
          const data = await res.json();
          setCanonicalData(data);
          if (!data.ok) {
            setError(data.error || 'Failed to load canonical documents');
          }
        } else {
          const res = await fetch('/api/docs/control/archive-candidates');
          if (!res.ok) {
            throw new Error(`Failed to load archive candidates: ${res.statusText}`);
          }
          const data = await res.json();
          setArchiveData(data);
          if (!data.ok) {
            setError(data.error || 'Failed to load archive candidates');
          }
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load data');
        console.error('Doc Control Panel fetch error:', err);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [activeTab]);

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleString();
    } catch {
      return dateString;
    }
  };

  const formatBytes = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="p-6 max-w-7xl mx-auto bg-gray-50 min-h-screen">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Doc Control Panel</h1>
        <p className="text-sm text-gray-500">
          Manage canonical documents and archive candidates (DM-002)
        </p>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="flex space-x-1">
          <button
            onClick={() => setActiveTab('canonical')}
            className={`px-4 py-2 font-medium text-sm rounded-t-lg transition-colors ${
              activeTab === 'canonical'
                ? 'bg-white text-blue-600 border-t-2 border-blue-600 shadow-sm'
                : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
            }`}
          >
            Canonical Documents
            {canonicalData?.total !== undefined && (
              <span className="ml-2 text-xs">({canonicalData.total})</span>
            )}
          </button>
          <button
            onClick={() => setActiveTab('archive')}
            className={`px-4 py-2 font-medium text-sm rounded-t-lg transition-colors ${
              activeTab === 'archive'
                ? 'bg-white text-blue-600 border-t-2 border-blue-600 shadow-sm'
                : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
            }`}
          >
            Archive Candidates
            {archiveData?.total_items !== undefined && (
              <span className="ml-2 text-xs">({archiveData.total_items})</span>
            )}
          </button>
        </nav>
      </div>

      {/* Content */}
      {loading && (
        <div className="text-center py-12 text-gray-500">Loading...</div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <div className="text-red-800 font-medium mb-1">Error</div>
          <div className="text-red-600 text-sm">{error}</div>
          <div className="text-red-500 text-xs mt-2">
            Ensure 'pmagent docs dashboard-refresh' has been run to generate exports.
          </div>
        </div>
      )}

      {!loading && !error && activeTab === 'canonical' && canonicalData && (
        <div>
          {canonicalData.generated_at && (
            <div className="text-xs text-gray-400 mb-4">
              Last refreshed: {formatDate(canonicalData.generated_at)}
            </div>
          )}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Path
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Title
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Size
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Last Modified
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {canonicalData.items.map((doc, idx) => (
                    <tr key={idx} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-600">
                        {doc.path}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900">{doc.title}</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800">
                          {doc.doc_type}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatBytes(doc.size_bytes)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatDate(doc.last_modified)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {!loading && !error && activeTab === 'archive' && archiveData && (
        <div>
          {archiveData.generated_at && (
            <div className="text-xs text-gray-400 mb-4">
              Last refreshed: {formatDate(archiveData.generated_at)}
            </div>
          )}
          <div className="grid gap-4">
            {archiveData.groups.length === 0 ? (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center text-gray-500">
                No archive candidates found
              </div>
            ) : (
              archiveData.groups.map((group, idx) => (
                <div
                  key={idx}
                  className="bg-white rounded-lg shadow-sm border border-gray-200 p-4"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <h3 className="font-medium text-gray-900 font-mono text-sm">
                        {group.directory}
                      </h3>
                      <p className="text-xs text-gray-500 mt-1">
                        {group.count} document{group.count !== 1 ? 's' : ''}
                      </p>
                    </div>
                    <span
                      className={`px-2 py-1 text-xs font-medium rounded-full ${
                        group.confidence === 'safe_cluster'
                          ? 'bg-green-100 text-green-800'
                          : 'bg-yellow-100 text-yellow-800'
                      }`}
                    >
                      {group.confidence}
                    </span>
                  </div>
                  {group.notes && (
                    <p className="text-sm text-gray-600 mt-2">{group.notes}</p>
                  )}
                  {group.example_paths.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-gray-100">
                      <p className="text-xs font-medium text-gray-500 mb-1">Example paths:</p>
                      <ul className="text-xs font-mono text-gray-600 space-y-1">
                        {group.example_paths.map((path, pidx) => (
                          <li key={pidx} className="truncate">
                            {path}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default DocControlPage;

