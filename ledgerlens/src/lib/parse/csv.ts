import type { Transaction } from "../../types";

/**
 * Minimal, dependency-free CSV parser for bank exports.
 * Handles quoted fields and commas inside quotes. Column mapping is
 * heuristic — real bank exports vary, so this is intentionally lenient.
 */
export function parseCsv(text: string): Transaction[] {
  const rows = splitRows(text);
  if (rows.length === 0) return [];

  const header = rows[0].map((h) => h.trim().toLowerCase());
  const dateIdx = findCol(header, ["date", "transaction date", "posted"]);
  const descIdx = findCol(header, ["description", "narration", "details", "merchant"]);
  const amtIdx = findCol(header, ["amount", "value"]);
  const debitIdx = findCol(header, ["debit", "withdrawal"]);
  const creditIdx = findCol(header, ["credit", "deposit"]);

  const out: Transaction[] = [];
  for (let i = 1; i < rows.length; i++) {
    const r = rows[i];
    if (r.length === 0 || r.every((c) => c.trim() === "")) continue;

    const amount =
      amtIdx >= 0
        ? parseAmount(r[amtIdx])
        : parseAmount(r[creditIdx]) - parseAmount(r[debitIdx]);

    out.push({
      id: `${i}-${r[dateIdx] ?? ""}`,
      date: normaliseDate(r[dateIdx] ?? ""),
      description: (r[descIdx] ?? "").trim(),
      amount,
    });
  }
  return out;
}

function findCol(header: string[], names: string[]): number {
  for (const n of names) {
    const idx = header.indexOf(n);
    if (idx >= 0) return idx;
  }
  return -1;
}

function parseAmount(s?: string): number {
  if (!s) return 0;
  const n = parseFloat(s.replace(/[^0-9.-]/g, ""));
  return Number.isFinite(n) ? n : 0;
}

function normaliseDate(s: string): string {
  const d = new Date(s);
  return Number.isNaN(d.getTime()) ? s.trim() : d.toISOString().slice(0, 10);
}

/** Split CSV text into rows of cells, respecting quoted fields. */
function splitRows(text: string): string[][] {
  const rows: string[][] = [];
  let cell = "";
  let row: string[] = [];
  let inQuotes = false;

  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (inQuotes) {
      if (c === '"' && text[i + 1] === '"') { cell += '"'; i++; }
      else if (c === '"') inQuotes = false;
      else cell += c;
    } else if (c === '"') inQuotes = true;
    else if (c === ",") { row.push(cell); cell = ""; }
    else if (c === "\n" || c === "\r") {
      if (c === "\r" && text[i + 1] === "\n") i++;
      row.push(cell); rows.push(row); cell = ""; row = [];
    } else cell += c;
  }
  if (cell.length > 0 || row.length > 0) { row.push(cell); rows.push(row); }
  return rows;
}
