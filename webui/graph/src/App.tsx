import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import GraphDashboard from "./pages/GraphDashboard";
import TemporalExplorer from "../../dashboard/src/components/TemporalExplorer";
import ForecastDashboard from "../../dashboard/ForecastDashboard";
import DocControlPanel from "../../dashboard/src/components/DocControlPanel";
import DocControlPage from "./pages/DocControlPage";
import OrchestratorShell from "../../orchestrator-shell/OrchestratorShell";
import BiblePage from "./pages/BiblePage";
import SystemDashboard from "./pages/SystemDashboard";
import KeywordSearchPage from "./pages/KeywordSearchPage";
import LexiconPage from "./pages/LexiconPage";
import VectorSearchPage from "./pages/VectorSearchPage";
import LMInsightsPage from "./pages/LMInsightsPage";
import DBInsightsPage from "./pages/DBInsightsPage";
import InsightsPage from "./pages/InsightsPage";
import CrossLanguagePage from "./pages/CrossLanguagePage";
import ShellLayout from "./components/ShellLayout";

function App() {
  return (
    <Router>
      <Routes>
        <Route element={<ShellLayout />}>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/graph" element={<GraphDashboard />} />
          <Route path="/temporal" element={<TemporalExplorer />} />
          <Route path="/forecast" element={<ForecastDashboard />} />
          <Route path="/docs" element={<DocControlPanel />} />
          <Route path="/doc-control" element={<DocControlPage />} />
          <Route path="/bible" element={<BiblePage />} />
          <Route path="/search" element={<KeywordSearchPage />} />
          <Route path="/vector-search" element={<VectorSearchPage />} />
          <Route path="/lexicon" element={<LexiconPage />} />
          <Route path="/dashboard" element={<SystemDashboard />} />
          <Route path="/lm-insights" element={<LMInsightsPage />} />
          <Route path="/db-insights" element={<DBInsightsPage />} />
          <Route path="/insights" element={<InsightsPage />} />
          <Route path="/cross-language" element={<CrossLanguagePage />} />
          <Route path="/shell" element={<OrchestratorShell />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
