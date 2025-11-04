import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import GraphDashboard from "./pages/GraphDashboard";
import CorrelationExplorer from "./components/CorrelationExplorer";

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-100">
        {/* Navigation */}
        <nav className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex space-x-8">
                <Link
                  to="/"
                  className="inline-flex items-center px-1 pt-1 border-b-2 border-transparent text-sm font-medium text-gray-500 hover:text-gray-700 hover:border-gray-300"
                >
                  Dashboard
                </Link>
                <Link
                  to="/correlations"
                  className="inline-flex items-center px-1 pt-1 border-b-2 border-transparent text-sm font-medium text-gray-500 hover:text-gray-700 hover:border-gray-300"
                >
                  Correlations
                </Link>
              </div>
              <div className="flex items-center">
                <span className="text-sm text-gray-500">Gematria Analytics</span>
              </div>
            </div>
          </div>
        </nav>

        {/* Routes */}
        <Routes>
          <Route path="/" element={<GraphDashboard />} />
          <Route path="/correlations" element={<CorrelationExplorer />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
