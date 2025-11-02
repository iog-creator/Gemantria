// P10-B minimal app

import React from 'react';
import { EnvelopeStats } from '../components/EnvelopeStats';

function App() {
  return (
    <div className="App">
      <h1>Gemantria Dashboard (P10-B)</h1>
      <p>Local-only visualization of Phase-9 envelopes</p>
      <EnvelopeStats />
    </div>
  );
}

export default App;
