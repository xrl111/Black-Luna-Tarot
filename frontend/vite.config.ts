import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const isProd = mode === "production";

  return {
    plugins: [react()],
    resolve: {
      alias: {
        "@": path.resolve(__dirname, "./src"),
      },
    },
    base: "/",
    build: {
      sourcemap: !isProd,
      target: "es2018",
      assetsInlineLimit: 4096,
      cssMinify: isProd,
      minify: isProd ? "esbuild" : false,
      chunkSizeWarningLimit: 1200,
    },
    server: {
      host: true, // Listen on all addresses
      allowedHosts: true, // Allow any host (Cloudflare Tunnel, Ngrok, etc)
      proxy: {
        "/api": {
          target: env.VITE_API_PROXY || "http://localhost:8000",
          changeOrigin: true,
        },
      },
    },
    preview: {
      proxy: {
        "/api": {
          target: env.VITE_API_PROXY || "http://localhost:8000",
          changeOrigin: true,
        },
      },
    },
  };
});
