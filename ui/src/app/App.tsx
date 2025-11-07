import React from "react";
import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import TemporalPage from "../views/TemporalPage";

export default function App() {
  return (
    <BrowserRouter>
      <div className="p-4">
        <nav className="mb-4 flex gap-4 text-sm">
          <Link to="/">Home</Link>
          <Link to="/temporal">Temporal</Link>
        </nav>
        <Routes>
          <Route path="/" element={<div>Home</div>} />
          <Route path="/temporal" element={<TemporalPage />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}
