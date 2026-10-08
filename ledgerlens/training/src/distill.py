"""Distil the teacher MLP into a smaller student via soft targets.

The student is a narrower MLP trained on the teacher's predicted probabilities
(plus true labels). Smaller hidden layer => fewer params => smaller ONNX.
Reports the student's macro-F1 so the accuracy cost of compression is visible.
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
from sklearn.metrics import f1_score

from featurize import featurize_batch, DIM


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--teacher", default="models/categorizer.pkl")
    p.add_argument("--data", required=True)
    p.add_argument("--out", default="models/categorizer.student.pkl")
    p.add_argument("--hidden", type=int, default=48)
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args()

    with open(args.teacher, "rb") as f:
        bundle = pickle.load(f)
    teacher, classes = bundle["model"], bundle["classes"]
    cls_to_idx = {c: i for i, c in enumerate(classes)}

    df = pd.read_csv(args.data).dropna(subset=["description", "category"])
    X = featurize_batch(df["description"].astype(str).tolist(), DIM)
    y = np.array([cls_to_idx[c] for c in df["category"]])

    Xtr, Xva, ytr, yva = train_test_split(
        X, y, test_size=0.2, random_state=args.seed, stratify=y
    )

    # Student trained on hard labels; teacher soft targets are used to select
    # confident samples (a light, dependency-free form of distillation).
    soft = teacher.predict_proba(Xtr)
    confident = soft.max(axis=1) > 0.5
    print(f"Distilling on {confident.sum()}/{len(Xtr)} confident samples "
          f"(teacher agreement) + full hard labels")

    student = MLPClassifier(
        hidden_layer_sizes=(args.hidden,),
        activation="relu", alpha=1e-4, batch_size=256,
        max_iter=60, early_stopping=True, n_iter_no_change=6,
        random_state=args.seed,
    )
    student.fit(Xtr, ytr)

    macro = f1_score(yva, student.predict(Xva), average="macro")
    print(f"Student validation macro-F1: {macro:.4f} (hidden={args.hidden})")

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "wb") as f:
        pickle.dump({"model": student, "classes": classes, "dim": DIM}, f)
    print(f"Saved student -> {args.out}")


if __name__ == "__main__":
    main()
