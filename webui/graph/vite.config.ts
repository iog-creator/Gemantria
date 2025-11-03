import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "src"),
      "src": path.resolve(__dirname, "src"),
    }
  },
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./test/setup.ts"],
    alias: {
      "@": path.resolve(__dirname, "src"),
      "src": path.resolve(__dirname, "src"),
    }
  },
  server: {
    port: 5173,
    proxy: {
      "/exports": {
        target: "http://localhost:8000", // Assuming backend runs on port 8000
        changeOrigin: true,
      },
    },
  },
});
