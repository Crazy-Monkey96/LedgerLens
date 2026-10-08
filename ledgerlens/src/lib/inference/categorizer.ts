import * as ort from "onnxruntime-web";
import type { Transaction, Category } from "../../types";
import { featurize, DIM } from "./featurize";

/**
 * Transaction categoriser — runs the int8 ONNX model exported by the training
 * pipeline. Featurisation here is identical to training (see featurize.ts), so
 * predictions match the offline evaluation.
 */
let session: ort.InferenceSession | null = null;
let classes: Category[] = [];

export async function initCategorizer(
  modelUrl = "/models/categorizer.int8.onnx",
  classesUrl = "/models/classes.json"
): Promise<void> {
  classes = (await (await fetch(classesUrl)).json()).classes;
  session = await ort.InferenceSession.create(modelUrl, {
    executionProviders: ["webgpu", "wasm"],
  });
}

export async function categorize(txns: Transaction[]): Promise<Transaction[]> {
  if (!session) await initCategorizer();
  const out: Transaction[] = [];
  for (const t of txns) {
    const feats = featurize(t.description, DIM);
    const input = new ort.Tensor("float32", feats, [1, DIM]);
    const result = await session!.run({ input });
    // pick the 2D probability output (the classifier also emits a label tensor)
    const probs = Object.values(result).find((v) => v.dims.length === 2);
    const data = probs!.data as Float32Array;
    let best = 0;
    for (let i = 1; i < data.length; i++) if (data[i] > data[best]) best = i;
    out.push({ ...t, category: classes[best] });
  }
  return out;
}
