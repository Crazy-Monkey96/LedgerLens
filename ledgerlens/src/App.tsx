import { useState } from "react";
import { parseCsv } from "./lib/parse/csv";
import { categorize } from "./lib/inference/categorizer";
import { detectRecurring } from "./lib/analysis/recurring";
import { scoreAnomalies } from "./lib/analysis/anomaly";
import { forecastCashflow } from "./lib/analysis/forecast";
import type { Transaction } from "./types";

export function App() {
  const [txns, setTxns] = useState<Transaction[]>([]);
  const [busy, setBusy] = useState(false);

  async function onFile(file: File) {
    setBusy(true);
    try {
      const text = await file.text();
      // NOTE: the file is read in-page. It is never uploaded anywhere.
      let parsed = parseCsv(text);
      parsed = await categorize(parsed);
      parsed = scoreAnomalies(parsed);
      setTxns(parsed);
      // recurring + forecast are computed for display downstream
      void detectRecurring(parsed);
      void forecastCashflow(parsed);
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="app">
      <header>
        <h1>LedgerLens</h1>
        <p className="tagline">Your financial data never leaves your browser.</p>
      </header>

      <label className="dropzone">
        <input
          type="file"
          accept=".csv"
          onChange={(e) => e.target.files?.[0] && onFile(e.target.files[0])}
        />
        {busy ? "Analysing locally…" : "Drop a bank statement CSV, or click to choose"}
      </label>

      {txns.length > 0 && (
        <section className="results">
          <p>{txns.length} transactions parsed on-device.</p>
          {/* TODO: category breakdown, recurring list, anomaly flags, forecast chart */}
        </section>
      )}
    </main>
  );
}
