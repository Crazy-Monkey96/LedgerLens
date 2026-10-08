import type { Transaction } from "../../types";

/**
 * Recurring-payment detection. Largely classical signal processing: look for
 * near-constant amounts at near-constant intervals (weekly/monthly) per merchant.
 * Cheap to run, genuinely useful (surfaces forgotten subscriptions).
 * TODO: group by normalised merchant, test interval regularity + amount stability.
 */
export function detectRecurring(txns: Transaction[]): Transaction[] {
  // TODO: implement periodicity detection; return the flagged subset.
  return [];
}
