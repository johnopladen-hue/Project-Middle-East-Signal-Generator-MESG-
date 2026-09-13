import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  // MapLibre GL JS renders via a Web Worker; Vite's dep pre-bundler mangles
  // that worker file (maplibre-gl-worker.mjs goes missing at runtime, tiles
  // never render - only the plain background layer + DOM markers show up).
  // Excluding it from pre-bundling lets it load natively instead.
  optimizeDeps: {
    exclude: ["maplibre-gl"],
  },
  server: {
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./src/test/setup.js"],
    pool: "threads",
  },
});
