"""
Deterministic char n-gram hashing featuriser.

Why hashing (not a learned vocabulary): the EXACT same featurisation must run
in the browser at inference time. A hashing vectoriser needs no vocab file —
only the hash function and the feature dimension — so the TS implementation in
`src/lib/inference/featurize.ts` reproduces these vectors bit-for-bit.

Features: lowercased char n-grams (n=3..5) hashed with FNV-1a into a fixed
`dim`-wide vector, L2-normalised. Digits are collapsed to '#' so that
"TESCO 4821" and "TESCO 9134" map together.
"""
from __future__ import annotations
import re
import numpy as np

DIM = 4096
NGRAM_MIN, NGRAM_MAX = 3, 5
_FNV_OFFSET = 0x811C9DC5
_FNV_PRIME = 0x01000193
_MASK = 0xFFFFFFFF


def fnv1a(s: str) -> int:
    h = _FNV_OFFSET
    for ch in s.encode("utf-8"):
        h ^= ch
        h = (h * _FNV_PRIME) & _MASK
    return h


def normalise(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\d", "#", text)          # collapse digits
    text = re.sub(r"\s+", " ", text).strip()
    return f" {text} "                        # pad so edge n-grams are distinct


def featurize(text: str, dim: int = DIM) -> np.ndarray:
    vec = np.zeros(dim, dtype=np.float32)
    s = normalise(text)
    for n in range(NGRAM_MIN, NGRAM_MAX + 1):
        for i in range(len(s) - n + 1):
            idx = fnv1a(s[i : i + n]) % dim
            vec[idx] += 1.0
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec /= norm
    return vec


def featurize_batch(texts, dim: int = DIM) -> np.ndarray:
    return np.vstack([featurize(t, dim) for t in texts]).astype(np.float32)
