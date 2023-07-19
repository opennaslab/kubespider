import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { crx } from "@crxjs/vite-plugin";
import manifest from "./src/manifest";
import { resolve } from "path";

console.log(resolve(__dirname, "../chrome-extension"));

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react(), crx({ manifest })],
  resolve: {
    alias: {
      "@": resolve(__dirname, "src"),
      "@lib": resolve(__dirname, "src/lib"),
      "@api": resolve(__dirname, "src/lib/api"),
      "@bridge": resolve(__dirname, "src/lib/bridge"),
      "@component": resolve(__dirname, "src/lib/component"),
      "@message": resolve(__dirname, "src/lib/message"),
      "@polyfill": resolve(__dirname, "src/lib/polyfill"),
      "@storage": resolve(__dirname, "src/lib/storage"),
    },
  },
  build: {
    emptyOutDir: true,
    outDir: resolve(__dirname, "../chrome-extension"),
    rollupOptions: {
      output: {
        chunkFileNames: "assets/chunk-[hash].js",
      },
    },
  },
});
