/**
 * Deterministic char n-gram hashing featuriser — the TypeScript twin of
 * `training/src/featurize.py`. Produces identical vectors to the training
 * pipeline (same FNV-1a hash, same normalisation, same dim), so a model trained
 * offline runs correctly in the browser with no vocabulary file to ship.
 */
export const DIM = 4096;
const NGRAM_MIN = 3;
const NGRAM_MAX = 5;

/** FNV-1a 32-bit — matches the Python implementation exactly. */
function fnv1a(s: string): number {
  let h = 0x811c9dc5;
  for (let i = 0; i < s.length; i++) {
    // iterate UTF-8 bytes to match Python's s.encode("utf-8")
    const bytes = utf8Bytes(s[i]);
    for (const b of bytes) {
      h ^= b;
      h = Math.imul(h, 0x01000193) >>> 0;
    }
  }
  return h >>> 0;
}

function utf8Bytes(ch: string): number[] {
  return Array.from(new TextEncoder().encode(ch));
}

function normalise(text: string): string {
  const lowered = text.toLowerCase().replace(/\d/g, "#").replace(/\s+/g, " ").trim();
  return ` ${lowered} `;
}

export function featurize(text: string, dim = DIM): Float32Array {
  const vec = new Float32Array(dim);
  const s = normalise(text);
  for (let n = NGRAM_MIN; n <= NGRAM_MAX; n++) {
    for (let i = 0; i + n <= s.length; i++) {
      const idx = fnv1a(s.slice(i, i + n)) % dim;
      vec[idx] += 1.0;
    }
  }
  let norm = 0;
  for (let i = 0; i < dim; i++) norm += vec[i] * vec[i];
  norm = Math.sqrt(norm);
  if (norm > 0) for (let i = 0; i < dim; i++) vec[i] /= norm;
  return vec;
}
