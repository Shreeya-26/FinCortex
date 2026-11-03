"use client";

import { useEffect, useState } from "react";
import { deleteCheck, getHistory } from "../../lib/api";
import { inr, tone, when } from "../../lib/format";

export default function HistoryPage() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [deletingId, setDeletingId] = useState(null);

  async function loadHistory() {
    setLoading(true);
    setError("");
    try {
      setItems(await getHistory());
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadHistory();
  }, []);

  async function removeCheck(id) {
    if (!window.confirm("Delete this financial check from your history?")) return;

    setDeletingId(id);
    setError("");
    try {
      await deleteCheck(id);
      setItems((current) => current.filter((item) => item.id !== id));
    } catch (e) {
      setError(e.message);
    } finally {
      setDeletingId(null);
    }
  }

  return (
    <section className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <p className="eyebrow">Your saved results</p>
          <h1 className="mt-1 text-3xl font-extrabold">My history</h1>
          <p className="mt-2 text-sm text-muted">
            Review your recent financial health checks.
          </p>
        </div>
        {!loading && (
          <button type="button" className="btn" onClick={loadHistory}>
            Refresh
          </button>
        )}
      </div>

      {error && (
        <div role="alert" className="rounded-xl border border-danger/30 bg-red-50 px-4 py-3 text-sm text-danger">
          <p>{error}</p>
          <button type="button" className="mt-2 font-bold underline" onClick={loadHistory}>
            Try again
          </button>
        </div>
      )}

      {loading ? (
        <div className="card text-center text-sm text-muted" role="status">
          Loading your history…
        </div>
      ) : items.length === 0 ? (
        <div className="card text-center">
          <h2 className="text-lg font-bold">No checks yet</h2>
          <p className="mt-1 text-sm text-muted">
            Your completed financial health checks will appear here.
          </p>
        </div>
      ) : (
        <ul className="space-y-3">
          {items.map((item) => {
            const scoreTone = tone(item.score);
            return (
              <li key={item.id} className="card flex flex-wrap items-center justify-between gap-4">
                <div className="flex min-w-0 items-center gap-4">
                  <div
                    className={`flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl bg-brand-50 text-xl font-extrabold ${scoreTone.text}`}
                    aria-label={`Score ${item.score} out of 100`}
                  >
                    {item.score}
                  </div>
                  <div>
                    <p className="font-bold">{when(item.created_at)}</p>
                    <p className="mt-1 text-sm text-muted">
                      Salary {inr(item.salary)} / month · {item.savings_rate_pct}% savings rate ·{" "}
                      {item.risk_appetite} risk
                    </p>
                  </div>
                </div>
                <button
                  type="button"
                  className="rounded-xl px-3 py-2 text-sm font-semibold text-danger hover:bg-red-50 disabled:opacity-60"
                  onClick={() => removeCheck(item.id)}
                  disabled={deletingId === item.id}
                  aria-label={`Delete check from ${when(item.created_at)}`}
                >
                  {deletingId === item.id ? "Deleting…" : "Delete"}
                </button>
              </li>
            );
          })}
        </ul>
      )}
    </section>
  );
}
