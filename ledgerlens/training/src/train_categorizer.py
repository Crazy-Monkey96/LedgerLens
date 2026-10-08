"""Train the transaction categoriser: char n-gram hashing features -> MLP.

Fully implemented. Produces a trained scikit-learn MLPClassifier, reports
macro-F1 on a held-out split, and saves the model for ONNX export.
"""
from __future__ import annotations
import argparse
import json
import os
import pickle
import numpy as np
import pandas as pd
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, classification_report

from featurize import featurize_batch, DIM


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--data", required=True)
    p.add_argument("--out", default="models/categorizer.pkl")
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args()

    df = pd.read_csv(args.data).dropna(subset=["description", "category"])
    print(f"Loaded {len(df)} rows, {df['category'].nunique()} categories")

    X = featurize_batch(df["description"].astype(str).tolist(), DIM)
    classes = sorted(df["category"].unique())
    cls_to_idx = {c: i for i, c in enumerate(classes)}
    y = np.array([cls_to_idx[c] for c in df["category"]])

    Xtr, Xva, ytr, yva = train_test_split(
        X, y, test_size=0.2, random_state=args.seed, stratify=y
    )

    clf = MLPClassifier(
        hidden_layer_sizes=(128,),
        activation="relu",
        alpha=1e-4,
        batch_size=256,
        max_iter=60,
        early_stopping=True,
        n_iter_no_change=6,
        random_state=args.seed,
    )
    print("Training MLP (teacher)…")
    clf.fit(Xtr, ytr)

    pred = clf.predict(Xva)
    macro = f1_score(yva, pred, average="macro")
    print(f"\nValidation macro-F1: {macro:.4f}\n")
    print(classification_report(yva, pred, target_names=classes, digits=3, zero_division=0))

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "wb") as f:
        pickle.dump({"model": clf, "classes": classes, "dim": DIM}, f)
    with open(os.path.join(os.path.dirname(args.out), "classes.json"), "w") as f:
        json.dump({"classes": classes, "dim": DIM}, f, indent=2)
    print(f"Saved teacher -> {args.out}")


if __name__ == "__main__":
    main()
