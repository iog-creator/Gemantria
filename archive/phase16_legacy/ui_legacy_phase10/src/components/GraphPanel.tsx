import React from "react";
import RerankP90Tile from "./RerankP90Tile";

export default function GraphPanel() {
  return (
    <div className="grid gap-3">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <RerankP90Tile />
      </div>
      {/* existing content */}
    </div>
  );
}

