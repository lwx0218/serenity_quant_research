import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// The API runs on :5000; in dev every /api call is proxied there.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: { "/api": "http://127.0.0.1:5000" },
  },
  build: { outDir: "dist", sourcemap: false },
});
