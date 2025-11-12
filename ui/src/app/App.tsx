// P10-UI-02: File loader + counts panel + minimal graph render

import React, { useState } from 'react';
import { EnvelopeStats } from '../components/EnvelopeStats';
import { FileLoader } from '../components/FileLoader';
import { GraphRenderer } from '../components/GraphRenderer';
import MetaPanel from '../components/MetaPanel';
import MetricsDashboard from '../components/MetricsDashboard';
import TemporalPage from '../views/TemporalPage';  // New import for temporal view
import XrefDemoPage from '../views/XrefDemoPage';  // New import for xref explorer
import MCPROProofTile from '../components/MCPROProofTile';  // PLAN-081: MCP RO Proof tile
import BrowserVerifiedBadge from '../components/BrowserVerifiedBadge';  // PLAN-081: Browser-Verified badge
import { Envelope } from '../types/envelope';

function App() {
  const [uploadedEnvelope, setUploadedEnvelope] = useState<Envelope | null>(null);
  const [activeTab, setActiveTab] = useState<'stats' | 'graph' | 'temporal' | 'xrefs'>('stats');  // Add tab types
  const [showMetrics, setShowMetrics] = useState(false);  // Dev toggle

  const handleFileLoad = (envelope: Envelope) => {
    setUploadedEnvelope(envelope);
  };

  return (
    <div className="App" style={{ maxWidth: '1200px', margin: '0 auto', padding: '20px' }}>
      <header style={{ marginBottom: '30px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
          <div>
            <h1>Gemantria Dashboard (P10-UI-02)</h1>
            <p>Local-only visualization: File loader + enhanced counts panel + minimal graph render</p>
          </div>
          <div style={{ marginTop: '8px' }}>
            <BrowserVerifiedBadge releaseVersion="v0.0.3" />
          </div>
        </div>
        {/* PLAN-081: Orchestrator dashboard polish — MCP RO Proof tile */}
        <MCPROProofTile />
      </header>

      <FileLoader onFileLoad={handleFileLoad} loading={false} />

      {uploadedEnvelope && (
        <div style={{ marginTop: '30px', marginBottom: '20px' }}>
          <button
            onClick={() => setActiveTab('stats')}
            style={{
              padding: '10px 20px',
              marginRight: '10px',
              backgroundColor: activeTab === 'stats' ? '#007bff' : '#f8f9fa',
              color: activeTab === 'stats' ? 'white' : 'black',
              border: '1px solid #ddd',
              borderRadius: '4px',
              cursor: 'pointer',
            }}
          >
            Statistics
          </button>
          <button
            onClick={() => setActiveTab('graph')}
            style={{
              padding: '10px 20px',
              marginRight: '10px',
              backgroundColor: activeTab === 'graph' ? '#007bff' : '#f8f9fa',
              color: activeTab === 'graph' ? 'white' : 'black',
              border: '1px solid #ddd',
              borderRadius: '4px',
              cursor: 'pointer',
            }}
          >
            Graph View
          </button>
          <button  // New button for temporal
            onClick={() => setActiveTab('temporal')}
            style={{
              padding: '10px 20px',
              marginRight: '10px',
              backgroundColor: activeTab === 'temporal' ? '#007bff' : '#f8f9fa',
              color: activeTab === 'temporal' ? 'white' : 'black',
              border: '1px solid #ddd',
              borderRadius: '4px',
              cursor: 'pointer',
            }}
          >
            Temporal Analytics
          </button>
          <button  // New button for xrefs
            onClick={() => setActiveTab('xrefs')}
            style={{
              padding: '10px 20px',
              backgroundColor: activeTab === 'xrefs' ? '#007bff' : '#f8f9fa',
              color: activeTab === 'xrefs' ? 'white' : 'black',
              border: '1px solid #ddd',
              borderRadius: '4px',
              cursor: 'pointer',
            }}
          >
            Cross-References
          </button>
        </div>
      )}

      {uploadedEnvelope && <MetaPanel meta={uploadedEnvelope.meta} />}  {/* Badge auto-renders */}
      {showMetrics && <MetricsDashboard />}  {/* Toggle for viz */}

      <div style={{ marginTop: '20px', marginBottom: '20px' }}>
        <button
          onClick={() => setShowMetrics(!showMetrics)}
          style={{
            padding: '8px 16px',
            backgroundColor: showMetrics ? '#28a745' : '#6c757d',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
          }}
        >
          {showMetrics ? 'Hide Metrics (Dev)' : 'Show Metrics (Dev)'}
        </button>
      </div>

      {activeTab === 'stats' && <EnvelopeStats uploadedEnvelope={uploadedEnvelope} />}
      {activeTab === 'graph' && <GraphRenderer envelope={uploadedEnvelope} />}
      {activeTab === 'temporal' && <TemporalPage />}  // New conditional render
      {activeTab === 'xrefs' && <XrefDemoPage />}  // New xref explorer
    </div>
  );
}

export default App;
