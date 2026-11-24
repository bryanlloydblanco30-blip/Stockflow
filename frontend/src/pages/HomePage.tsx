import { useEffect, useState } from "react";
import Shell from "../components/Shell";
import type { Navigate } from "../types";
import { api, formatPHP, type DashboardDTO } from "../api";

export default function HomePage({ navigate }: { navigate: Navigate }) {
  const [data, setData] = useState<DashboardDTO | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    setLoading(true);
    api
      .getDashboard()
      .then((res) => {
        if (active) {
          setData(res);
          setError(null);
        }
      })
      .catch((err) => {
        if (active) setError(err instanceof Error ? err.message : "Failed to load dashboard.");
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);

  const kpis = data?.kpis;
  const attention = data?.attention ?? [];

  return (
    <Shell
      active="home"
      page="home"
      title="Home"
      subtitle="Your store at a glance"
      navigate={navigate}
      action={
        <button className="primary peach" onClick={() => navigate("sell")}>
          START SALE
        </button>
      }
    >
      {error && (
        <div
          style={{
            background: "#fee2e2",
            color: "#991b1b",
            padding: "12px 18px",
            borderRadius: "14px",
            marginBottom: "14px",
            fontWeight: 600,
          }}
        >
          ⚠ {error} — Make sure the Python backend is running (`python main.py`).
        </div>
      )}

      <div className="stat-grid">
        <article className="stat yellow">
          <span>Today's Sales</span>
          <strong>{loading ? "…" : formatPHP(kpis?.today_sales ?? 0)}</strong>
        </article>
        <article className="stat green">
          <span>Today’s Profit</span>
          <strong>{loading ? "…" : formatPHP(kpis?.today_profit ?? 0)}</strong>
        </article>
        <article className="stat peach" style={{ cursor: "pointer" }} onClick={() => navigate("restock")}>
          <span>Low Stock Items</span>
          <strong>{loading ? "…" : kpis?.low_stock_count ?? 0}</strong>
        </article>
        <article className="stat purple" style={{ cursor: "pointer" }} onClick={() => navigate("alerts")}>
          <span>Near Expiry Batches</span>
          <strong>{loading ? "…" : kpis?.near_expiry_count ?? 0}</strong>
        </article>
      </div>

      <section className="panel table-panel">
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
          <h2 style={{ margin: 0 }}>Needs attention</h2>
          <button className="purple-pill small" onClick={() => navigate("alerts")}>
            Open Alerts & Checklist ›
          </button>
        </div>
        <div className="table-scroll">
          {loading ? (
            <p style={{ padding: "24px", color: "#69756b" }}>Loading store status…</p>
          ) : attention.length === 0 ? (
            <p style={{ padding: "24px", color: "#245c45", fontWeight: 600 }}>
              ✓ All shelves look healthy. No urgent expiry or low-stock alerts.
            </p>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>Product</th>
                  <th>Issue</th>
                  <th>Urgency</th>
                </tr>
              </thead>
              <tbody>
                {attention.map((row) => (
                  <tr key={`${row.product_id}-${row.urgency}`}>
                    <td><strong>{row.product_name}</strong></td>
                    <td>{row.issue}</td>
                    <td>
                      <span className={`badge ${row.color}`}>
                        {row.color === "red" ? "⚠ " : "● "}
                        {row.urgency}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </section>

      <button className="wide-callout" onClick={() => navigate("sell")}>
        <span>
          <strong>Ready for your next customer?</strong>
          <small>Start a sale, check your shelves, and keep things moving.</small>
        </span>
        <span className="cart-symbol">⌑</span>
      </button>
    </Shell>
  );
}
