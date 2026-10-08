import type { Transaction, ForecastPoint } from "../../types";

/**
 * Cash-flow forecasting. Project the next 30 days as a BAND (p10/p50/p90),
 * never a single line — being explicit about uncertainty is the right call in
 * a financial tool. TODO: quantile regression over daily net-flow history.
 */
export function forecastCashflow(_txns: Transaction[], _horizon = 30): ForecastPoint[] {
  // TODO: implement quantile forecaster; return one ForecastPoint per day.
  return [];
}
