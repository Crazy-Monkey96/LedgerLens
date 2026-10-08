# LedgerLens — training pipeline

Entirely offline. Trains the transaction categoriser, compresses it
(distil → int8 quantise), exports to ONNX, and evaluates it. Only the exported
`.onnx` artifacts are copied into `../public/models/` to ship to the browser.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python src/data/generate_synthetic.py --rows 20000 --out data/processed/train.csv
python src/data/generate_synthetic.py --rows 4000  --out data/processed/test.csv --seed 7
python src/train_categorizer.py --data data/processed/train.csv   # ~0.82 macro-F1 (synthetic)
python src/distill.py
python src/quantize.py
python src/export_onnx.py
python src/distill.py --data data/processed/train.csv
python src/export_onnx.py
python src/quantize.py
python src/evaluate.py --model models/categorizer.int8.onnx --test data/processed/test.csv
```

**Data honesty:** training starts from synthetic data; the real evaluation set
should be a small hand-labelled sample of real, anonymised transactions. Never
commit real financial data — `data/` is gitignored.


Scripts import `featurize` from this `src/` dir automatically (it is on the
script path) — no `PYTHONPATH` needed. The shipped browser model lives at
`../public/models/categorizer.int8.onnx` after `quantize.py`.
