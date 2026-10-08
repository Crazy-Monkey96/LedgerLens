"""Dynamic int8 quantisation of the fp32 ONNX categoriser.

Prints the size before/after so the README table gets a REAL number.
"""
from __future__ import annotations
import argparse
import os
from onnxruntime.quantization import quantize_dynamic, QuantType


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--inp", default="models/categorizer.fp32.onnx")
    p.add_argument("--out", default="models/categorizer.int8.onnx")
    args = p.parse_args()

    quantize_dynamic(args.inp, args.out, weight_type=QuantType.QInt8)
    before = os.path.getsize(args.inp) / 1024
    after = os.path.getsize(args.out) / 1024
    print(f"int8 quantisation: {before:.1f} KB -> {after:.1f} KB "
          f"({100*(1-after/before):.0f}% smaller)  -> {args.out}")


if __name__ == "__main__":
    main()
