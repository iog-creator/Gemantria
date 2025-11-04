import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import GraphDashboard from "./pages/GraphDashboard";
import TemporalExplorer from "../../dashboard/src/components/TemporalExplorer";
import ForecastDashboard from "../../dashboard/ForecastDashboard";

function App() {
  return (
    <Router>
      <nav className="bg-gray-800 text-white p-4">
        <div className="flex gap-4">
          <Link to="/" className="hover:text-gray-300">Graph</Link>
          <Link to="/temporal" className="hover:text-gray-300">Temporal Explorer</Link>
          <Link to="/forecast" className="hover:text-gray-300">Forecast Dashboard</Link>
        </div>
      </nav>
      <Routes>
        <Route path="/" element={<GraphDashboard />} />
        <Route path="/temporal" element={<TemporalExplorer />} />
        <Route path="/forecast" element={<ForecastDashboard />} />
      </Routes>
    </Router>
  );
}

export default App;
