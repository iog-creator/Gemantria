import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // Note: /exports is served statically from public/exports/ directory
      // Files are synced via npm run sync-doc-exports before build
      "/api": {
        target: "http://localhost:8000", // API server for temporal and forecast data
        changeOrigin: true,
      },
      "/temporal": {
        target: "http://localhost:8000", // API server for temporal routes
        changeOrigin: true,
      },
    },
  },
});
