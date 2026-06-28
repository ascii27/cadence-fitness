import { openDB, type IDBPDatabase } from "idb";
import type { LogCreate } from "./types";

const DB_NAME = "cadence";
const STORE = "log_outbox";

export interface QueuedLog {
  client_id: string;
  kind: "create" | "patch";
  created_at: number;
  seq: number; // monotonic tiebreaker for same-millisecond enqueues
  payload: LogCreate | Record<string, unknown>;
  log_id?: string; // for patch
}

let _seq = 0;

let _dbPromise: Promise<IDBPDatabase> | null = null;

function db(): Promise<IDBPDatabase> {
  if (!_dbPromise) {
    _dbPromise = openDB(DB_NAME, 1, {
      upgrade(database) {
        if (!database.objectStoreNames.contains(STORE)) {
          database.createObjectStore(STORE, { keyPath: "client_id" });
        }
      },
    });
  }
  return _dbPromise;
}

function uuid(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) return crypto.randomUUID();
  return `q_${Date.now()}_${Math.random().toString(16).slice(2)}`;
}

export async function enqueue(
  item: Omit<QueuedLog, "client_id" | "created_at" | "seq">,
): Promise<QueuedLog> {
  const full: QueuedLog = { ...item, client_id: uuid(), created_at: Date.now(), seq: _seq++ };
  const d = await db();
  await d.put(STORE, full);
  return full;
}

export async function list(): Promise<QueuedLog[]> {
  const d = await db();
  const items = (await d.getAll(STORE)) as QueuedLog[];
  return items.sort((a, b) => a.created_at - b.created_at || a.seq - b.seq);
}

export async function remove(client_id: string): Promise<void> {
  const d = await db();
  await d.delete(STORE, client_id);
}

export async function count(): Promise<number> {
  const d = await db();
  return d.count(STORE);
}

export interface FlushResult {
  sent: number;
  remaining: number;
}

/**
 * Drain the queue. `sender` should throw on failure; failed items are retained
 * (and stop the drain so ordering is preserved), succeeded items are removed.
 */
export async function flush(sender: (item: QueuedLog) => Promise<void>): Promise<FlushResult> {
  const items = await list();
  let sent = 0;
  for (const item of items) {
    try {
      await sender(item);
      await remove(item.client_id);
      sent += 1;
    } catch {
      break; // keep this and later items for the next attempt
    }
  }
  return { sent, remaining: await count() };
}

// Test helper: wipe the store.
export async function _reset(): Promise<void> {
  const d = await db();
  await d.clear(STORE);
}
