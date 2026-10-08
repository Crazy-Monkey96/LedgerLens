import type { Transaction } from "../../types";

/**
 * PDF statement parsing. TODO: integrate pdf.js (loaded locally, no network)
 * to extract the text layer, then apply bank-specific line heuristics to
 * recover date / description / amount triples.
 *
 * Kept behind the same interface as parseCsv so the UI does not care which
 * format the user dropped in.
 */
export async function parsePdf(_file: File): Promise<Transaction[]> {
  // TODO: const pdfjs = await import("pdfjs-dist");
  //       extract text per page, regex out transaction lines, map to Transaction[].
  throw new Error("PDF parsing not yet implemented — use CSV export for now.");
}
