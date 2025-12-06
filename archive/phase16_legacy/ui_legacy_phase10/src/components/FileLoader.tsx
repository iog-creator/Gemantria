// File upload component for P10-UI-01

import React, { useRef } from 'react';

interface FileLoaderProps {
  onFileLoad: (envelope: any) => void;
  loading: boolean;
}

export function FileLoader({ onFileLoad, loading }: FileLoaderProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!file.name.endsWith('.json')) {
      alert('Please select a JSON file');
      return;
    }

    try {
      const { loadEnvelopeFromFile } = await import('../lib/loadEnvelope');
      const envelope = await loadEnvelopeFromFile(file);
      onFileLoad(envelope);
    } catch (error) {
      alert(`Failed to load file: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div style={{ padding: '20px', border: '1px solid #ccc', margin: '20px' }}>
      <h3>Load Envelope File</h3>
      <input
        ref={fileInputRef}
        type="file"
        accept=".json"
        onChange={handleFileChange}
        style={{ display: 'none' }}
      />
      <button
        onClick={handleClick}
        disabled={loading}
        style={{
          padding: '10px 20px',
          backgroundColor: loading ? '#ccc' : '#007bff',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: loading ? 'not-allowed' : 'pointer'
        }}
      >
        {loading ? 'Loading...' : 'Choose JSON File'}
      </button>
      <p style={{ fontSize: '12px', color: '#666', marginTop: '10px' }}>
        Select a Gemantria envelope JSON file to visualize
      </p>
    </div>
  );
}
