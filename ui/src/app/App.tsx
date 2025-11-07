// P10-UI-02: File loader + counts panel + minimal graph render

import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import { EnvelopeStats } from '../components/EnvelopeStats';
import { FileLoader } from '../components/FileLoader';
import { GraphRenderer } from '../components/GraphRenderer';
import MetaPanel from '../components/MetaPanel';
import MetricsDashboard from '../components/MetricsDashboard';
import EnvelopePage from '../views/EnvelopePage';
import { Envelope } from '../types/envelope';

function App() {
  const [uploadedEnvelope, setUploadedEnvelope] = useState<Envelope | null>(null);
  const [activeTab, setActiveTab] = useState<'stats' | 'graph'>('stats');
  const [showMetrics, setShowMetrics] = useState(false);  // Dev toggle

  const handleFileLoad = (envelope: Envelope) => {
    setUploadedEnvelope(envelope);
  };

  return (
    <BrowserRouter>
      <div className="App" style={{ maxWidth: '1200px', margin: '0 auto', padding: '20px' }}>
        <nav style={{ marginBottom: '20px', padding: '10px', borderBottom: '1px solid #ddd' }}>
          <Link to="/" style={{ marginRight: '20px', textDecoration: 'none', color: '#007bff' }}>Dashboard</Link>
          <Link to="/envelope" style={{ textDecoration: 'none', color: '#007bff' }}>Envelope</Link>
        </nav>

        <Routes>
          <Route path="/" element={
            <>
              <header style={{ marginBottom: '30px' }}>
                <h1>Gemantria Dashboard (P10-UI-02)</h1>
                <p>Local-only visualization: File loader + enhanced counts panel + minimal graph render</p>
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
                      backgroundColor: activeTab === 'graph' ? '#007bff' : '#f8f9fa',
                      color: activeTab === 'graph' ? 'white' : 'black',
                      border: '1px solid #ddd',
                      borderRadius: '4px',
                      cursor: 'pointer',
                    }}
                  >
                    Graph View
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
            </>
          } />
          <Route path="/envelope" element={<EnvelopePage />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
