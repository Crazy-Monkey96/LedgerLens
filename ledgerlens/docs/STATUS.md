# Status & honest scope

Scaffolded end-to-end, with the **transaction categoriser fully built and measured**.

**Working today**
- Web app shell (`npm run dev`), CSV parsing, IndexedDB storage.
- Synthetic data generator with realistic ambiguity + label noise.
- **Full categoriser pipeline**: train → distil → int8 quantise → ONNX export → evaluate.
- Deterministic hashing featuriser with a **byte-identical Python ↔ TypeScript** pair
  (verified to 4e-7), so the shipped int8 model runs in-browser and matches offline eval.
- CI regression gate on macro-F1.

**Still TODO (clearly marked in code)**
- Recurring-payment, anomaly, and forecasting models.
- Moving categoriser inference into the Web Worker (currently runs on the main thread).
- PDF statement parsing.
- OPFS / Service-Worker offline caching of models.

**Reported numbers** are on **synthetic** data and labelled as such everywhere. Any
figure must come from a real measured run — never estimated. Real-data evaluation
awaits a small hand-labelled anonymised set.
