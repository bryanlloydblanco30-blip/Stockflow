import { useCallback, useEffect, useState } from "react";
import Shell from "../components/Shell";
import type { Navigate } from "../types";
import { api, formatDate, formatPHP, type TransactionRowDTO } from "../api";

function typeBadgeColor(t: string): string {
  const low = t.toLowerCase();
  if (low === "sale") return "green";
  if (low === "void" || low === "writeoff" || low === "write-off") return "red";
  return "amber";
}

export default function HistoryPage({ navigate }: { navigate: Navigate }) {
  const [filter, setFilter] = useState("All");
  const [rows, setRows] = useState<TransactionRowDTO[]>([]);
  const [loading, setLoading] = useState(true);
  const [banner, setBanner] = useState<{ type: "ok" | "error"; text: string } | null>(null);

  const loadHistory = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.getTransactions(filter);
      setRows(res.transactions);
    } finally {
      setLoading(false);
    }
  }, [filter]);

  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  const handleUndo = async () => {
    try {
      const res = await api.undoLast();
      setBanner({
        type: "ok",
        text: `✓ Voided transaction #${res.reverses_id} (${formatPHP(res.total)}). Stock restored to exact batches.`,
      });
      await loadHistory();
    } catch (err) {
      setBanner({
        type: "error",
        text: err instanceof Error ? err.message : "Could not undo transaction.",
      });
    }
  };

  return (
    <Shell
      active="reports"
      page="history"
      title="Transaction history"
      subtitle="Audit log of sales, voids, adjustments, and write-offs"
      navigate={navigate}
    >
      <div className="filter-row history-filters">
        {["All", "Sale", "Void", "Adjustment", "Writeoff"].map((item) => (
          <button
            className={filter === item ? "blue-pill" : ""}
            onClick={() => setFilter(item)}
            key={item}
          >
            {item}
          </button>
        ))}
      </div>

      {banner && (
        <div
          style={{
            padding: "10px 16px",
            borderRadius: "12px",
            marginBottom: "12px",
            fontWeight: 600,
            background: banner.type === "ok" ? "#e5efdb" : "#fee2e2",
            color: banner.type === "ok" ? "#245c45" : "#991b1b",
          }}
        >
          {banner.text}
        </div>
      )}

      <section className="panel table-panel history-table">
        <div className="table-scroll">
          {loading ? (
            <p style={{ padding: "24px", color: "#69756b" }}>Loading transaction log…</p>
          ) : rows.length === 0 ? (
            <p style={{ padding: "24px", color: "#69756b" }}>No transactions found yet.</p>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Date</th>
                  <th>Type</th>
                  <th>Details</th>
                  <th>Amount</th>
                  <th />
                </tr>
              </thead>
              <tbody>
                {rows.map((row) => (
                  <tr key={row.id}>
                    <td>#{row.id}</td>
                    <td>{formatDate(row.date_time)}</td>
                    <td>
                      <span className={`badge ${typeBadgeColor(row.type)}`}>{row.type}</span>
                    </td>
                    <td>{row.details}</td>
                    <td><strong>{formatPHP(row.total)}</strong></td>
                    <td>
                      {row.can_undo && (
                        <button className="purple-pill small" onClick={handleUndo}>
                          Void last sale
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </section>
      <p className="history-note">Undo is available only on the latest transaction (1-level Stack, Decision D2).</p>
    </Shell>
  );
}
