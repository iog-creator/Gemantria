// P10-B entry point

import React from 'react';
import ReactDOM from 'react-dom/client';
import OrchestratorApp from './app/OrchestratorApp';
import '../../webui/graph/src/index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <OrchestratorApp />
  </React.StrictMode>,
);
