// Cross-reference visualization demo page

import React, { useState, useEffect } from 'react';
import { XrefIndex, XrefNode, XrefReference } from '../types/xrefs';
import { loadXrefIndex } from '../lib/loadXrefIndex';
import XrefChips from '../components/XrefChips';
import XrefSidePanel from '../components/XrefSidePanel';

const XrefDemoPage: React.FC = () => {
  const [xrefIndex, setXrefIndex] = useState<XrefIndex | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedNode, setSelectedNode] = useState<XrefNode | null>(null);
  const [selectedXref, setSelectedXref] = useState<XrefReference | null>(null);
  const [searchTerm, setSearchTerm] = useState('');

  // Load xref index on mount
  useEffect(() => {
    loadXrefIndex()
      .then((data) => {
        setXrefIndex(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  const handleChipClick = (node: XrefNode) => (xref: XrefReference) => {
    setSelectedNode(node);
    setSelectedXref(xref);
  };

  const handleCloseSidePanel = () => {
    setSelectedXref(null);
    setSelectedNode(null);
  };

  // Filter nodes by search term (Hebrew text or gematria)
  const filteredNodes = xrefIndex?.nodes.filter((node) => {
    if (!searchTerm) return true;
    const term = searchTerm.toLowerCase();
    return (
      node.he.includes(searchTerm) ||
      node.gm.toString().includes(term)
    );
  }).slice(0, 20) || [];

  if (loading) {
    return (
      <div style={{ padding: '2rem', textAlign: 'center' }}>
        <div style={{ fontSize: '1.2rem', color: '#666' }}>
          Loading cross-reference index...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: '2rem', textAlign: 'center' }}>
        <div style={{ fontSize: '1.2rem', color: '#d32f2f', marginBottom: '1rem' }}>
          Error loading cross-reference index
        </div>
        <div style={{ fontSize: '0.9rem', color: '#666' }}>{error}</div>
      </div>
    );
  }

  return (
    <div style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
      {/* Header */}
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ marginBottom: '0.5rem', color: '#01579b' }}>
          Cross-Reference Explorer
        </h1>
        <div style={{ fontSize: '0.9rem', color: '#666' }}>
          Total Nodes: {xrefIndex?.total_nodes} | Generated:{' '}
          {xrefIndex?.generated_at
            ? new Date(xrefIndex.generated_at).toLocaleString()
            : 'N/A'}
        </div>
      </div>

      {/* Search */}
      <div style={{ marginBottom: '2rem' }}>
        <input
          type="text"
          placeholder="Search by Hebrew text or gematria value..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          style={{
            width: '100%',
            padding: '0.75rem',
            fontSize: '1rem',
            border: '1px solid #ddd',
            borderRadius: '8px',
          }}
        />
      </div>

      {/* Node cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: '1rem' }}>
        {filteredNodes.map((node, index) => (
          <div
            key={`${node.he}-${node.gm}-${index}`}
            style={{
              padding: '1rem',
              border: '1px solid #ddd',
              borderRadius: '8px',
              backgroundColor: '#fafafa',
              transition: 'all 0.2s ease',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.boxShadow = '0 4px 8px rgba(0,0,0,0.1)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.boxShadow = 'none';
            }}
          >
            {/* Hebrew + Gematria */}
            <div style={{ marginBottom: '0.75rem' }}>
              <div style={{ fontSize: '1.5rem', fontWeight: '600', marginBottom: '0.25rem' }}>
                {node.he}
              </div>
              <div style={{ fontSize: '0.85rem', color: '#666' }}>
                Gematria: <span style={{ fontWeight: '600' }}>{node.gm}</span> |{' '}
                References: <span style={{ fontWeight: '600' }}>{node.xref_count}</span>
              </div>
            </div>

            {/* Xref chips */}
            <XrefChips
              xrefs={node.xrefs}
              onChipClick={handleChipClick(node)}
              maxVisible={5}
            />
          </div>
        ))}
      </div>

      {/* No results message */}
      {filteredNodes.length === 0 && (
        <div style={{ textAlign: 'center', padding: '3rem', color: '#999' }}>
          <div style={{ fontSize: '1.2rem' }}>No matching nodes found</div>
          <div style={{ fontSize: '0.9rem', marginTop: '0.5rem' }}>
            Try a different search term
          </div>
        </div>
      )}

      {/* Side panel */}
      <XrefSidePanel
        selectedXref={selectedXref}
        node={selectedNode}
        onClose={handleCloseSidePanel}
      />
    </div>
  );
};

export default XrefDemoPage;

