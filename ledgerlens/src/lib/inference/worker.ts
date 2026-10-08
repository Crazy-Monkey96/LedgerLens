/// <reference lib="webworker" />
import * as ort from "onnxruntime-web";
import type { Transaction, ForecastPoint } from "../../types";

/**
 * All model inference runs here, off the main thread, so the UI never blocks.
 * Models are loaded once and cached by the service worker; WebGPU is used
 * where available with a WASM fallback.
 */

let categorizer: ort.InferenceSession | null = null;

async function ensureCategorizer(): Promise<ort.InferenceSession> {
  if (categorizer) return categorizer;
  // TODO: ship public/models/categorizer.int8.onnx from the training pipeline.
  categorizer = await ort.InferenceSession.create("/models/categorizer.int8.onnx", {
    executionProviders: ["webgpu", "wasm"],
  });
  return categorizer;
}

export type WorkerRequest =
  | { type: "categorize"; txns: Transaction[] }
  | { type: "forecast"; txns: Transaction[] };

export type WorkerResponse =
  | { type: "categorize"; txns: Transaction[] }
  | { type: "forecast"; forecast: ForecastPoint[] };

self.onmessage = async (e: MessageEvent<WorkerRequest>) => {
  const msg = e.data;
  try {
    if (msg.type === "categorize") {
      const session = await ensureCategorizer();
      // TODO: featurise descriptions -> tensor, run session, argmax -> Category.
      void session;
      self.postMessage({ type: "categorize", txns: msg.txns } as WorkerResponse);
    } else if (msg.type === "forecast") {
      // TODO: build the quantile forecaster; return p10/p50/p90 per day.
      self.postMessage({ type: "forecast", forecast: [] } as WorkerResponse);
    }
  } catch (err) {
    self.postMessage({ type: "error", error: String(err) } as never);
  }
};
