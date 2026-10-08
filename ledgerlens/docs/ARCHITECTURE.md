# Architecture

LedgerLens has **no backend**. The entire application is the browser; a host only
serves static files (HTML, JS, and the `.onnx` model). Data a user drops in is
parsed in-page and never transmitted — privacy is structural, not a promise.

The runtime is organised in four layers, with an offline training pipeline that
produces the models the inference layer runs.

```
┌──────────────────────────────────────────────────────────────┐
│ PRESENTATION   React UI · Dashboard (charts) · Reports · Setup │
├──────────────────────────────────────────────────────────────┤
│ APPLICATION    State · Services (business logic) ·             │
│                Model orchestration · Web Workers (compute)     │
├──────────────────────────────────────────────────────────────┤
│ INFERENCE      ONNX Runtime Web:  WebGPU (primary)             │
│                                   → WASM (fallback, SIMD+threads)│
├──────────────────────────────────────────────────────────────┤
│ DATA           IndexedDB (structured) · OPFS (large files) ·   │
│                Cache Storage (models) · Service Worker (offline)│
└──────────────────────────────────────────────────────────────┘
        ▲ static assets only (HTML, JS, .onnx)
   Cloudflare Pages / Vercel — free, unmetered, no card
```

## Layer notes

- **Presentation** — React + Recharts render category breakdowns, recurring
  payments, anomaly flags, and the cash-flow forecast *band* (p10/p50/p90).
- **Application** — services coordinate parse → featurise → infer → persist.
  Heavy compute is pushed to a **Web Worker** (`src/lib/inference/worker.ts`) so
  the UI thread never blocks.
- **Inference** — **ONNX Runtime Web**, backend chain **WebGPU → WASM**. (WebGL
  is intentionally *not* used: ORT-Web's WebGL backend is limited and effectively
  deprecated; WASM with SIMD+threads is the robust fallback.)
- **Data** — **IndexedDB** for structured transactions, **OPFS** for large blobs
  (big statements / model files), **Cache Storage** + a **Service Worker** so the
  app and its models load once and then work fully offline.

## Offline training pipeline (where the ML engineering lives)

```
synthetic / real data
   → train fp32 teacher (char n-gram hashing → MLP)
   → distil to a smaller student
   → int8 dynamic quantisation
   → export ONNX  → ship ONLY the int8 model to public/models/
   → evaluate (macro-F1, per-category F1, latency) → CI regression gate
```

The featuriser is a **deterministic char n-gram hashing** scheme
(`training/src/featurize.py`) with a **byte-identical TypeScript twin**
(`src/lib/inference/featurize.ts`), verified equal to ~4e-7. Because no learned
vocabulary is needed, the exact training-time features are reproduced in the
browser with nothing extra to ship.

## Evaluation & CI

`training/src/evaluate.py` writes `eval/reports/latest.json`; `eval/check_gate.py`
fails a pull request if macro-F1 drops below threshold. See the README for the
current measured numbers (on synthetic data).

## Privacy model

No network path exists for user data to leave the device — enforced by
construction (no backend, no upload endpoint), not by policy. `.gitignore`
additionally prevents any real financial data from being committed.

## Design credits

The four-layer runtime split and the OPFS / Cache-Storage / Service-Worker data
layer were refined from an earlier whiteboard architecture; the training,
compression, and evaluation pipeline is what turns the serving diagram into a
system with measurable ML behaviour.
