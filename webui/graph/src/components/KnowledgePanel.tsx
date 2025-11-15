import { useKnowledgeSlice } from "../hooks/useKnowledgeSlice";

/**
 * Knowledge Panel component for displaying KB documents.
 *
 * Shows a clean, scrollable list of knowledge documents with titles, sections,
 * previews, and tags. Handles loading and empty states gracefully.
 */
export function KnowledgePanel() {
  const { docs, loading, error, isEmpty, db_off } = useKnowledgeSlice();

  if (loading) {
    return (
      <div className="p-4 border border-gray-200 rounded-lg bg-white">
        <h2 className="text-lg font-semibold mb-4">Knowledge Base</h2>
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-3 text-gray-600">Loading knowledge docs...</span>
        </div>
      </div>
    );
  }

  if (error || isEmpty || db_off) {
    return (
      <div className="p-4 border border-gray-200 rounded-lg bg-white">
        <h2 className="text-lg font-semibold mb-4">Knowledge Base</h2>
        <div className="py-8 text-center text-gray-500">
          <p className="mb-2">No knowledge docs available yet</p>
          {db_off && (
            <p className="text-sm text-gray-400">Database offline or export unavailable</p>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 border border-gray-200 rounded-lg bg-white">
      <h2 className="text-lg font-semibold mb-4">Knowledge Base</h2>
      <div className="space-y-4 max-h-96 overflow-y-auto">
        {docs.map((doc) => (
          <div
            key={doc.id}
            className="p-3 border border-gray-100 rounded-md hover:bg-gray-50 transition-colors"
          >
            <div className="flex items-start justify-between mb-2">
              <h3 className="font-medium text-gray-900">{doc.title}</h3>
              {doc.section && (
                <span className="ml-2 px-2 py-1 text-xs font-medium text-gray-600 bg-gray-100 rounded">
                  {doc.section}
                </span>
              )}
            </div>
            {doc.preview && (
              <p className="text-sm text-gray-600 mb-2 line-clamp-2">{doc.preview}</p>
            )}
            {doc.tags.length > 0 && (
              <div className="flex flex-wrap gap-1 mt-2">
                {doc.tags.map((tag, idx) => (
                  <span
                    key={idx}
                    className="px-2 py-0.5 text-xs text-blue-600 bg-blue-50 rounded"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

