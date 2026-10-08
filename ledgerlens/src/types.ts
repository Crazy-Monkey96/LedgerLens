/** Canonical transaction shape used across parsing, inference and UI. */
export interface Transaction {
  id: string;
  date: string;        // ISO yyyy-mm-dd
  description: string; // raw merchant / narration string
  amount: number;      // signed: negative = debit, positive = credit
  category?: Category; // filled by the categoriser
  isRecurring?: boolean;
  anomalyScore?: number; // 0..1, higher = more unusual for this user
}

export type Category =
  | "groceries" | "dining" | "transport" | "utilities" | "rent"
  | "entertainment" | "health" | "shopping" | "income" | "transfer" | "other";

export const CATEGORIES: Category[] = [
  "groceries", "dining", "transport", "utilities", "rent",
  "entertainment", "health", "shopping", "income", "transfer", "other",
];

/** A forecast point with a quantile band, never a single line. */
export interface ForecastPoint {
  date: string;
  p10: number;
  p50: number;
  p90: number;
}

export interface AnalysisResult {
  transactions: Transaction[];
  recurring: Transaction[];
  anomalies: Transaction[];
  forecast: ForecastPoint[];
  categoryTotals: Record<Category, number>;
}
