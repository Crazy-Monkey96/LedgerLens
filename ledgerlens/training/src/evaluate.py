"""Evaluate an ONNX categoriser on a held-out set; write JSON + print table.

Computes macro-F1, per-category F1, model size, and p50/p95 single-sample
latency. The CI gate (eval/check_gate.py) reads the JSON.
"""
from __future__ import annotations
import argparse
import json
import os
import time
import numpy as np
import pandas as pd
import onnxruntime as ort
from sklearn.metrics import f1_score, classification_report

from featurize import featurize_batch, featurize, DIM


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=True)
    p.add_argument("--test", required=True)
    p.add_argument("--classes", default="models/classes.json")
    p.add_argument("--report", default="../eval/reports/latest.json")
    args = p.parse_args()

    with open(args.classes) as f:
        classes = json.load(f)["classes"]
    cls_to_idx = {c: i for i, c in enumerate(classes)}

    df = pd.read_csv(args.test).dropna(subset=["description", "category"])
    X = featurize_batch(df["description"].astype(str).tolist(), DIM)
    y = np.array([cls_to_idx[c] for c in df["category"]])

    sess = ort.InferenceSession(args.model, providers=["CPUExecutionProvider"])
    outs = sess.run(None, {"input": X.astype(np.float32)})
    probs = next(o for o in outs if getattr(o, "ndim", 0) == 2)
    pred = probs.argmax(axis=1)

    macro = float(f1_score(y, pred, average="macro"))
    per = f1_score(y, pred, average=None, labels=list(range(len(classes))), zero_division=0)
    per_cat = {classes[i]: round(float(per[i]), 3) for i in range(len(classes))}

    # single-sample latency (what runs per transaction in the browser)
    lat = []
    for d in df["description"].astype(str).tolist()[:500]:
        v = featurize(d, DIM)[None, :].astype(np.float32)
        t0 = time.perf_counter()
        sess.run(None, {"input": v})
        lat.append((time.perf_counter() - t0) * 1000)
    lat.sort()
    p50 = lat[len(lat)//2]; p95 = lat[int(len(lat)*0.95)]

    size_kb = os.path.getsize(args.model) / 1024
    metrics = {
        "macro_f1": round(macro, 4),
        "per_category_f1": per_cat,
        "model_size_kb": round(size_kb, 1),
        "latency_ms_p50_cpu": round(p50, 3),
        "latency_ms_p95_cpu": round(p95, 3),
        "n": int(len(df)),
        "synthetic": True,
    }
    os.makedirs(os.path.dirname(args.report), exist_ok=True)
    with open(args.report, "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"\nmacro-F1: {macro:.4f}   size: {size_kb:.1f} KB   "
          f"latency p50/p95: {p50:.2f}/{p95:.2f} ms (CPU)\n")
    print(classification_report(y, pred, target_names=classes, digits=3, zero_division=0))
    print(f"Report -> {args.report}  (NOTE: metrics are on SYNTHETIC data)")


if __name__ == "__main__":
    main()
