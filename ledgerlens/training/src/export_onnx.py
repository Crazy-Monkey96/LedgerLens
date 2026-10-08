"""Export a trained sklearn MLP to ONNX for ONNX Runtime Web.

Input: a float32 feature vector of length DIM. Output: class probabilities.
Verifies the ONNX model matches the sklearn model on a few samples.
"""
from __future__ import annotations
import argparse
import os
import pickle
import numpy as np
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType
import onnxruntime as ort

from featurize import featurize_batch, DIM


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--model", default="models/categorizer.student.pkl")
    p.add_argument("--out", default="models/categorizer.fp32.onnx")
    args = p.parse_args()

    with open(args.model, "rb") as f:
        bundle = pickle.load(f)
    clf, classes = bundle["model"], bundle["classes"]

    onx = convert_sklearn(
        clf,
        initial_types=[("input", FloatTensorType([None, DIM]))],
        target_opset=17,
        options={id(clf): {"zipmap": False}},  # plain probability tensor
    )
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "wb") as f:
        f.write(onx.SerializeToString())

    # Parity check vs sklearn
    sample = featurize_batch(["TESCO LONDON", "UBER *trip", "NETFLIX", "SALARY CREDIT"], DIM)
    sess = ort.InferenceSession(args.out, providers=["CPUExecutionProvider"])
    outs = sess.run(None, {"input": sample.astype(np.float32)})
    onnx_out = next(o for o in outs if getattr(o, "ndim", 0) == 2)  # probabilities
    skl_out = clf.predict_proba(sample)
    max_diff = float(np.abs(onnx_out - skl_out).max())
    print(f"ONNX vs sklearn max prob diff: {max_diff:.2e}  (want < 1e-4)")
    for desc, probs in zip(["TESCO LONDON", "UBER *trip", "NETFLIX", "SALARY CREDIT"], onnx_out):
        print(f"  {desc:16} -> {classes[int(probs.argmax())]}")
    print(f"fp32 ONNX size: {os.path.getsize(args.out)/1024:.1f} KB -> {args.out}")


if __name__ == "__main__":
    main()
