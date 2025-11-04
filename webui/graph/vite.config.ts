import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/exports": {
        target: "http://localhost:4000", // Serving exports directly
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/exports/, ''),
      },
      "/api": {
        target: "http://localhost:8000", // API server for temporal and forecast data
        changeOrigin: true,
      },
    },
  },
});
