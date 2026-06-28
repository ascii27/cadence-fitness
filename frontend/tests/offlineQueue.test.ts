import { beforeEach, describe, expect, it } from "vitest";
import * as queue from "../src/lib/offlineQueue";
import type { LogCreate } from "../src/lib/types";

const sample: LogCreate = { status: "completed", duration_minutes: 30 };

beforeEach(async () => {
  await queue._reset();
});

describe("offlineQueue", () => {
  it("enqueues and lists items in created order", async () => {
    await queue.enqueue({ kind: "create", payload: sample });
    await queue.enqueue({ kind: "create", payload: { ...sample, duration_minutes: 45 } });
    const items = await queue.list();
    expect(items).toHaveLength(2);
    expect(items[0].created_at).toBeLessThanOrEqual(items[1].created_at);
    expect(await queue.count()).toBe(2);
  });

  it("assigns a unique client_id to each item", async () => {
    const a = await queue.enqueue({ kind: "create", payload: sample });
    const b = await queue.enqueue({ kind: "create", payload: sample });
    expect(a.client_id).not.toEqual(b.client_id);
  });

  it("flushes all items when the sender succeeds", async () => {
    await queue.enqueue({ kind: "create", payload: sample });
    await queue.enqueue({ kind: "patch", log_id: "x", payload: { rating: 5 } });
    const sent: queue.QueuedLog[] = [];
    const result = await queue.flush(async (item) => {
      sent.push(item);
    });
    expect(result.sent).toBe(2);
    expect(result.remaining).toBe(0);
    expect(await queue.count()).toBe(0);
  });

  it("retains items and stops when the sender fails", async () => {
    await queue.enqueue({ kind: "create", payload: sample });
    await queue.enqueue({ kind: "create", payload: sample });
    const result = await queue.flush(async () => {
      throw new Error("offline");
    });
    expect(result.sent).toBe(0);
    expect(result.remaining).toBe(2);
    expect(await queue.count()).toBe(2);
  });

  it("removes only the succeeded item before a failure (preserves order)", async () => {
    await queue.enqueue({ kind: "create", payload: { ...sample, duration_minutes: 1 } });
    await queue.enqueue({ kind: "create", payload: { ...sample, duration_minutes: 2 } });
    let calls = 0;
    const result = await queue.flush(async () => {
      calls += 1;
      if (calls === 2) throw new Error("offline");
    });
    expect(result.sent).toBe(1);
    expect(result.remaining).toBe(1);
    const remaining = await queue.list();
    expect((remaining[0].payload as LogCreate).duration_minutes).toBe(2);
  });
});
