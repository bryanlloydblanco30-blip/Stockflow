import { useCallback, useEffect, useState } from "react";
import Shell from "../components/Shell";
import type { Navigate } from "../types";
import { api, formatDate, formatPHP, type AlertsDTO } from "../api";

export default function AlertsPage({ navigate }: { navigate: Navigate }) {
  const [data, setData] = useState<AlertsDTO | null>(null);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState<"near" | "checklist" | "writeoff">("near");
  const [banner, setBanner] = useState<{ type: "ok" | "error"; text: string } | null>(null);

  const loadAlerts = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.getAlerts();
      setData(res);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadAlerts();
  }, [loadAlerts]);

  const handleRotate = async (batchId: number, productName: string) => {
    try {
      await api.markShelfRotated(batchId);
      setBanner({ type: "ok", text: `✓ Marked Batch #${batchId} (${productName}) as moved to front of shelf.` });
      await loadAlerts();
    } catch (err) {
      setBanner({ type: "error", text: err instanceof Error ? err.message : "Failed to update shelf flag." });
    }
  };

  const handleWriteOff = async (batchId: number, productName: string) => {
    try {
      const res = await api.writeOffExpired({ batch_id: batchId, reason: "Expired on shelf" });
      setBanner({
        type: "ok",
        text: `✓ Wrote off ${res.units_lost} expired units of "${productName}" (${formatPHP(res.loss_amount)} spoilage logged).`,
      });
      await loadAlerts();
    } catch (err) {
      setBanner({ type: "error", text: err instanceof Error ? err.message : "Write-off failed." });
    }
  };

  const nearList = data?.near_expiry ?? [];
  const checklist = data?.checklist ?? [];
  const expiredList = data?.expired ?? [];
  const unresolved = data?.unresolved_expiry ?? [];

  return (
    <Shell
      active="stock"
      page="alerts"
      title="Alerts, Rotation & Write-Offs"
      subtitle="Near-expiry batches, shelf-rotation checklist, and expired write-offs"
      navigate={navigate}
      action={
        <button className="purple-pill" onClick={() => navigate("stock")}>
          Back to Stock
        </button>
      }
    >
      <div className="filter-row" style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
        <button className={tab === "near" ? "blue-pill" : ""} onClick={() => setTab("near")}>
          Near Expiry ({nearList.length})
        </button>
        <button className={tab === "checklist" ? "blue-pill" : ""} onClick={() => setTab("checklist")}>
          Shelf Rotation Checklist ({checklist.filter((c) => !c.moved_to_front).length} pending)
        </button>
        <button className={tab === "writeoff" ? "blue-pill" : ""} onClick={() => setTab("writeoff")}>
          Expired Write-Offs ({expiredList.length})
        </button>
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

      {unresolved.length > 0 && (
        <div
          style={{
            padding: "12px 16px",
            borderRadius: "14px",
            marginBottom: "12px",
            background: "#fff3cd",
            color: "#856404",
            fontWeight: 600,
          }}
        >
          ⚠ {unresolved.length} batch(es) need an expiry date after category tracking was enabled.
        </div>
      )}

      <section className="panel table-panel">
        <div className="table-scroll">
          {loading ? (
            <p style={{ padding: "24px", color: "#69756b" }}>Scanning expiring batches…</p>
          ) : tab === "near" ? (
            nearList.length === 0 ? (
              <p style={{ padding: "24px", color: "#245c45", fontWeight: 600 }}>
                ✓ No near-expiry batches within category warning windows.
              </p>
            ) : (
              <table>
                <thead>
                  <tr>
                    <th>Batch</th>
                    <th>Product</th>
                    <th>Category</th>
                    <th>Units</th>
                    <th>Expiry Date</th>
                    <th>Days Left</th>
                    <th>Level</th>
                  </tr>
                </thead>
                <tbody>
                  {nearList.map((row) => (
                    <tr key={row.batch_id}>
                      <td>#{row.batch_id}</td>
                      <td><strong>{row.product_name}</strong></td>
                      <td>{row.category_name}</td>
                      <td>{row.quantity}</td>
                      <td>{formatDate(row.expiry_date)}</td>
                      <td>{row.days_left === 0 ? "Today" : `${row.days_left}d`}</td>
                      <td>
                        <span className={`badge ${row.level === "RED" ? "red" : "amber"}`}>
                          {row.level === "RED" ? "⚠ Red" : "● Amber"}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )
          ) : tab === "checklist" ? (
            checklist.length === 0 ? (
              <p style={{ padding: "24px", color: "#245c45", fontWeight: 600 }}>
                ✓ Nothing to rotate on shelves right now.
              </p>
            ) : (
              <table>
                <thead>
                  <tr>
                    <th>Batch</th>
                    <th>Product</th>
                    <th>Units</th>
                    <th>Expiry</th>
                    <th>Level</th>
                    <th style={{ textAlign: "right" }}>Shelf Status</th>
                  </tr>
                </thead>
                <tbody>
                  {checklist.map((row) => (
                    <tr key={row.batch_id}>
                      <td>#{row.batch_id}</td>
                      <td><strong>{row.product_name}</strong></td>
                      <td>{row.quantity}</td>
                      <td>{formatDate(row.expiry_date)}</td>
                      <td>
                        <span className={`badge ${row.level === "RED" ? "red" : "amber"}`}>{row.level}</span>
                      </td>
                      <td style={{ textAlign: "right" }}>
                        {row.moved_to_front ? (
                          <span className="badge green">✓ Moved to front</span>
                        ) : (
                          <button
                            className="restock-row-btn"
                            onClick={() => handleRotate(row.batch_id, row.product_name)}
                          >
                            Mark Moved to Front
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )
          ) : expiredList.length === 0 ? (
            <p style={{ padding: "24px", color: "#245c45", fontWeight: 600 }}>
              ✓ No expired batches waiting for write-off.
            </p>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>Batch</th>
                  <th>Product</th>
                  <th>Units</th>
                  <th>Expired On</th>
                  <th>Loss Value</th>
                  <th style={{ textAlign: "right" }}>Action</th>
                </tr>
              </thead>
              <tbody>
                {expiredList.map((row) => (
                  <tr key={row.batch_id}>
                    <td>#{row.batch_id}</td>
                    <td><strong>{row.product_name}</strong></td>
                    <td>{row.quantity}</td>
                    <td>{formatDate(row.expiry_date)}</td>
                    <td><strong style={{ color: "#991b1b" }}>{formatPHP(row.loss_value)}</strong></td>
                    <td style={{ textAlign: "right" }}>
                      <button
                        className="purple-pill small"
                        onClick={() => handleWriteOff(row.batch_id, row.product_name)}
                      >
                        Write Off Expired
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </section>
    </Shell>
  );
}
