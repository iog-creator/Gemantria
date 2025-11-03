// P10-UI-02: File loader + counts panel + minimal graph render

import React, { useState } from 'react';
import { EnvelopeStats } from '../components/EnvelopeStats';
import { FileLoader } from '../components/FileLoader';
import { GraphRenderer } from '../components/GraphRenderer';
import { Envelope } from '../types/envelope';

function App() {
  const [uploadedEnvelope, setUploadedEnvelope] = useState<Envelope | null>(null);
  const [activeTab, setActiveTab] = useState<'stats' | 'graph'>('stats');

  const handleFileLoad = (envelope: Envelope) => {
    setUploadedEnvelope(envelope);
  };

  return (
    <div className="App" style={{ maxWidth: '1200px', margin: '0 auto', padding: '20px' }}>
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

      {activeTab === 'stats' && <EnvelopeStats uploadedEnvelope={uploadedEnvelope} />}
      {activeTab === 'graph' && <GraphRenderer envelope={uploadedEnvelope} />}
    </div>
  );
}

export default App;
