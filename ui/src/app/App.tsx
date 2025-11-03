// P10-UI-01: File loader + counts panel

import React, { useState } from 'react';
import { EnvelopeStats } from '../components/EnvelopeStats';
import { FileLoader } from '../components/FileLoader';
import { Envelope } from '../types/envelope';

function App() {
  const [uploadedEnvelope, setUploadedEnvelope] = useState<Envelope | null>(null);

  const handleFileLoad = (envelope: Envelope) => {
    setUploadedEnvelope(envelope);
  };

  return (
    <div className="App" style={{ maxWidth: '1200px', margin: '0 auto', padding: '20px' }}>
      <header style={{ marginBottom: '30px' }}>
        <h1>Gemantria Dashboard (P10-UI-01)</h1>
        <p>Local-only visualization: File loader + enhanced counts panel</p>
      </header>

      <FileLoader onFileLoad={handleFileLoad} loading={false} />

      <EnvelopeStats uploadedEnvelope={uploadedEnvelope} />
    </div>
  );
}

export default App;
