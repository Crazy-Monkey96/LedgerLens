"""Fail the CI build if categoriser macro-F1 regresses below a threshold.

While no model exists yet, a null macro_f1 is treated as 'not built' and does
not fail the build. Once evaluate.py produces a real number, the gate enforces it.
"""
from __future__ import annotations
import argparse
import json
import sys


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--report", required=True)
    p.add_argument("--min-macro-f1", type=float, default=0.75)
    args = p.parse_args()

    try:
        with open(args.report) as f:
            m = json.load(f)
    except FileNotFoundError:
        print("No eval report yet — gate inactive.")
        return 0

    f1 = m.get("macro_f1")
    if f1 is None:
        print("macro_f1 not measured yet — gate inactive.")
        return 0
    if f1 < args.min_macro_f1:
        print(f"FAIL: macro-F1 {f1:.3f} < threshold {args.min_macro_f1}")
        return 1
    print(f"PASS: macro-F1 {f1:.3f} >= {args.min_macro_f1}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
