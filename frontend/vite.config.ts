import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    port: 3000,
    proxy: {
      "/api": {
        target: "http://localhost:6000",
        changeOrigin: true,
      },
      "/shipments": {
        target: "http://localhost:6000",
        changeOrigin: true,
      },
      "/alerts": {
        target: "http://localhost:6000",
        changeOrigin: true,
      },
      "/reroute": {
        target: "http://localhost:6000",
        changeOrigin: true,
      },
      "/ws": {
        target: "ws://localhost:6000",
        ws: true,
      },
    },
  },
});
