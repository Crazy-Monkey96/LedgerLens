import type { Transaction } from "../../types";

/**
 * Local-only persistence. Everything stays in IndexedDB on the device; nothing
 * is ever sent anywhere. Used to remember the last parsed statement between
 * visits so the app works offline.
 */
const DB_NAME = "ledgerlens";
const STORE = "transactions";

function open(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(DB_NAME, 1);
    req.onupgradeneeded = () => req.result.createObjectStore(STORE, { keyPath: "id" });
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
}

export async function saveTransactions(txns: Transaction[]): Promise<void> {
  const db = await open();
  const tx = db.transaction(STORE, "readwrite");
  for (const t of txns) tx.objectStore(STORE).put(t);
  return new Promise((res, rej) => {
    tx.oncomplete = () => res();
    tx.onerror = () => rej(tx.error);
  });
}

export async function loadTransactions(): Promise<Transaction[]> {
  const db = await open();
  return new Promise((res, rej) => {
    const req = db.transaction(STORE, "readonly").objectStore(STORE).getAll();
    req.onsuccess = () => res(req.result as Transaction[]);
    req.onerror = () => rej(req.error);
  });
}
