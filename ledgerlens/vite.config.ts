import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// ONNX Runtime Web ships WASM/threads assets; these headers enable
// SharedArrayBuffer so multi-threaded WASM inference works in the browser.
export default defineConfig({
  plugins: [react()],
  server: {
    headers: {
      "Cross-Origin-Opener-Policy": "same-origin",
      "Cross-Origin-Embedder-Policy": "require-corp",
    },
  },
  // ort’s .wasm files must be served as-is, not inlined.
  optimizeDeps: { exclude: ["onnxruntime-web"] },
  worker: { format: "es" },
});
