import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import GraphDashboard from "./pages/GraphDashboard";
import TemporalExplorer from "../../dashboard/src/components/TemporalExplorer";
import ForecastDashboard from "../../dashboard/ForecastDashboard";
import DocControlPanel from "../../dashboard/src/components/DocControlPanel";
import OrchestratorShell from "../../orchestrator-shell/OrchestratorShell";

function App() {
  return (
    <Router>
      <nav className="bg-gray-800 text-white p-4">
        <div className="flex gap-4">
          <Link to="/" className="hover:text-gray-300">Graph</Link>
          <Link to="/temporal" className="hover:text-gray-300">Temporal Explorer</Link>
          <Link to="/forecast" className="hover:text-gray-300">Forecast Dashboard</Link>
          <Link to="/docs" className="hover:text-gray-300">Doc Control</Link>
        </div>
      </nav>
      <Routes>
        <Route path="/" element={<OrchestratorShell />} />
        <Route path="/graph" element={<GraphDashboard />} />
        <Route path="/temporal" element={<TemporalExplorer />} />
        <Route path="/forecast" element={<ForecastDashboard />} />
        <Route path="/docs" element={<DocControlPanel />} />
        <Route path="/shell" element={<OrchestratorShell />} />
      </Routes>
    </Router>
  );
}

export default App;
