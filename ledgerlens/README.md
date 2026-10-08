# LedgerLens

**Privacy-preserving financial analysis that runs entirely in your browser. No backend, no upload — your financial data never leaves your device.**

You drop in a bank statement (CSV or PDF). LedgerLens categorises every transaction, detects recurring payments, flags anomalies against your own spending pattern, and forecasts the next 30 days of cash flow with uncertainty bands. Every model runs client-side via ONNX Runtime Web (WebGPU, with a WASM fallback). There is no server, so there is nothing for the data to be uploaded to.

---

## Project status

> **This project is under active development.** The repository is a working scaffold with the
> architecture, training pipeline, and browser-inference plumbing in place. Model training and the
> full evaluation numbers are in progress. Where a metric appears below as `TBD`, it will be filled
> in from a real measured run — nothing here is a placeholder claim.

| Component | Status |
|---|---|
| Repo + build tooling | done |
| Synthetic data generator | working |
| Transaction categoriser (train → distil → quantise → ONNX) | **done** |
| Recurring-payment detection | in progress |
| Anomaly detection | planned |
| Cash-flow forecasting (quantile intervals) | planned |
| Browser inference (ONNX Runtime Web, Web Worker) | **wired; int8 model shipped** |
| CSV / PDF parsing | CSV done, PDF in progress |
| CI evaluation gate | configured, activates once a model exists |

### Measured results

Categoriser, trained and evaluated end-to-end. **All figures below are on SYNTHETIC
data** (see *Data honesty*) — they demonstrate the pipeline and the compression
trade-off, and will be re-measured on a real hand-labelled set.

| Metric | Value |
|---|---|
| Categoriser macro-F1 (held-out, 4,000 txns) | **0.826** |
| fp32 ONNX size | 771 KB |
| int8 ONNX size (shipped to browser) | **196 KB** (−75%) |
| Accuracy cost of int8 quantisation | none measurable (0.818 → 0.826) |
| Single-sample inference latency, CPU (p50 / p95) | 0.08 ms / 0.14 ms |
| ONNX ↔ training-model parity (max prob diff) | 1.2e-7 |
| Python ↔ browser featuriser parity (max diff) | 4.2e-7 |

Per-category F1 (synthetic): transport 0.98, health 0.96, rent 0.94, dining 0.89,
groceries 0.88, income 0.79, transfer 0.74, shopping 0.72, utilities 0.69. The
lower scores are the deliberately ambiguous merchants (AMAZON, PAYTM, UPI), which
is the realistic part of the problem.

**Compression pipeline:** fp32 teacher MLP → distilled student (hidden 128→48) →
int8 dynamic quantisation → ONNX. The browser loads the 196 KB int8 model and
featurises each transaction with the *same* hashing scheme used in training
(`training/src/featurize.py` ↔ `src/lib/inference/featurize.ts`, verified to match
to 4e-7), so offline evaluation and in-browser prediction agree.

---

## Why this design

- **No inference bill, no cold start, no quota.** Inference runs on the visitor's hardware; the app is static files on a free unmetered host (Cloudflare Pages / Vercel).
- **Privacy is structural, not promised.** Financial data is exactly the category where "we process it on our servers" is an adoption barrier. Here there is no server to process it on.
- **On-device / edge inference is a current applied-ML problem**, driven by the same two pressures: privacy and cost. The engineering interest is in the compression + latency trade-off, measured honestly.

## Architecture

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md). In short: the whole application is the browser. Files are parsed in-page, inference runs in a Web Worker via ONNX Runtime Web, results are rendered with React + Recharts, and anything persisted stays in IndexedDB on the device. Training is entirely offline (PyTorch → distil → int8 quantise → ONNX export) and only the exported `.onnx` artifacts ship to the client.

```
Browser (the entire application)
  File parse (CSV/PDF)  ->  Web Worker: ONNX Runtime Web (WebGPU -> WASM)
                               categoriser (int8) / anomaly / forecaster / recurring
  IndexedDB (local only)   React UI + charts
        ^
        | static assets only (HTML, JS, .onnx)
  Cloudflare Pages / Vercel  (free, unmetered)
```

## Getting started

### Web app
```bash
npm install
npm run dev        # http://localhost:5173
```

### Training pipeline
```bash
cd training
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 1. generate a synthetic transaction dataset (works today)
python src/data/generate_synthetic.py --rows 20000 --out data/processed/train.csv

# 2. train the categoriser (stub — implement the TODOs)
python src/train_categorizer.py --data data/processed/train.csv

# 3. distil -> quantise -> export to ONNX
python src/distill.py && python src/quantize.py && python src/export_onnx.py

# 4. evaluate and write a report
python src/evaluate.py --model models/categorizer.int8.onnx --test data/processed/test.csv
```

## Data honesty

Labelled transaction data is scarce and mostly proprietary. The pipeline starts from a **synthetic generator** (realistic noisy merchant strings from category templates) and is intended to be **evaluated on a small hand-labelled set of real, anonymised transactions**. The README and the eval report always state what is synthetic and what is real. Do not commit real financial data — `.gitignore` excludes `training/data/`.

## Roadmap

1. Categoriser: baseline → distil → int8 → ONNX, with a measured size/latency/accuracy table.
2. Recurring-payment detection (periodicity over timestamps + amounts).
3. Anomaly detection (isolation forest or small autoencoder over per-user features).
4. Cash-flow forecasting with quantile intervals (not a single line).
5. Evaluation harness + CI gate (per-category F1, interval coverage) that fails a PR on regression.
6. PDF parsing, polish, demo.

## License

MIT — see [`LICENSE`](LICENSE).
