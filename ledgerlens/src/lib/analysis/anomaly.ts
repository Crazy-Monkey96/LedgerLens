import type { Transaction } from "../../types";

/**
 * Anomaly detection: flag transactions unusual for THIS user's own pattern,
 * not against a global notion of unusual.
 * TODO: isolation forest or a small autoencoder over per-user features
 * (amount z-score within category, time-of-month, merchant novelty).
 */
export function scoreAnomalies(txns: Transaction[]): Transaction[] {
  // TODO: assign anomalyScore in [0,1]; return txns with scores set.
  return txns;
}
