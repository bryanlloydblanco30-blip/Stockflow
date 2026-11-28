import { useCallback, useEffect, useState } from "react";
import Shell from "../components/Shell";
import type { Navigate } from "../types";
import { api, formatDate, formatPHP, type RestockDTO, type RestockItemDTO } from "../api";

export default function RestockPage({ navigate }: { navigate: Navigate }) {
  const [data, setData] = useState<RestockDTO | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"priority" | "urgent" | "fast" | "slow">("priority");
  const [selectedItem, setSelectedItem] = useState<RestockItemDTO | null>(null);
  const [restockQty, setRestockQty] = useState<number>(20);
  const [expiryDate, setExpiryDate] = useState<string>("");
  const [olderWarning, setOlderWarning] = useState<
    { batch_id: number; expiry_date: string; units: number; level: string }[]
  >([]);
  const [banner, setBanner] = useState<string | null>(null);
  const [errorBanner, setErrorBanner] = useState<string | null>(null);

  const loadRestock = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.getRestock();
      setData(res);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadRestock();
  }, [loadRestock]);

  const queue = data?.queue ?? [];
  const urgentCount = queue.filter((x) => x.urgency === "Urgent").length;
  const totalSuggestedUnits = queue.reduce((sum, x) => sum + x.suggested_reorder, 0);
  const totalEstCost = queue.reduce((sum, x) => sum + x.suggested_reorder * x.cost_price, 0);

  const displayedItems = queue.filter((item) => {
    if (activeTab === "urgent") return item.urgency === "Urgent";
    return true;
  });

  const openRestockModal = (item: RestockItemDTO) => {
    setSelectedItem(item);
    setRestockQty(item.suggested_reorder > 0 ? item.suggested_reorder : 20);
    setExpiryDate("");
    setOlderWarning([]);
  };

  const handleRestockSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedItem) return;
    try {
      const res = await api.receiveStock({
        product_id: selectedItem.product_id,
        quantity: Number(restockQty),
        cost_price: selectedItem.cost_price,
        expiry_date: selectedItem.tracks_expiry ? expiryDate || null : null,
      });
      if (res.older_batches_warning.length > 0) {
        setOlderWarning(res.older_batches_warning);
      } else {
        setSelectedItem(null);
      }
      setErrorBanner(null);
      setBanner(`✓ Received +${restockQty} units of "${selectedItem.product_name}".`);
      setTimeout(() => setBanner(null), 4000);
      await loadRestock();
    } catch (err) {
      setErrorBanner(err instanceof Error ? err.message : "Failed to receive stock.");
      setTimeout(() => setErrorBanner(null), 5000);
    }
  };

  return (
    <>
      <Shell
        active="restock"
        page="restock"
        title="Restock"
        subtitle="Prioritized by days of cover and 14-day selling speed"
        navigate={navigate}
        action={
          <button
            className="primary blue"
            disabled={queue.length === 0}
            onClick={() => queue[0] && openRestockModal(queue[0])}
          >
            + Receive Stock
          </button>
        }
      >
        <div className="filter-row restock-filters" style={{ justifyContent: "space-between", alignItems: "center" }}>
          <div style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
            <button className={activeTab === "priority" ? "blue-pill" : ""} onClick={() => setActiveTab("priority")}>
              Priority Queue
            </button>
            <button className={activeTab === "urgent" ? "blue-pill" : ""} onClick={() => setActiveTab("urgent")}>
              Urgent Only ({urgentCount})
            </button>
            <button className={activeTab === "fast" ? "blue-pill" : ""} onClick={() => setActiveTab("fast")}>
              Fast Movers
            </button>
            <button className={activeTab === "slow" ? "blue-pill" : ""} onClick={() => setActiveTab("slow")}>
              Slow Movers
            </button>
          </div>

          <div style={{ fontSize: "14px", color: "#53605c", display: "flex", gap: "16px" }}>
            <span>Suggested Units: <strong>{totalSuggestedUnits}</strong></span>
            <span>Est. Cost: <strong>{formatPHP(totalEstCost)}</strong></span>
          </div>
        </div>

        {errorBanner && (
          <div style={{ background: "#fee2e2", color: "#991b1b", padding: "12px 20px", borderRadius: "16px", marginBottom: "14px", fontWeight: 600 }}>
            {errorBanner}
          </div>
        )}
        {banner && (
          <div style={{ background: "#e5efdb", color: "#245c45", padding: "12px 20px", borderRadius: "16px", marginBottom: "14px", fontWeight: 600 }}>
            {banner}
          </div>
        )}

        <section className="panel table-panel">
          <div className="table-scroll">
            {loading ? (
              <p style={{ padding: "24px", color: "#69756b" }}>Loading restock queue…</p>
            ) : activeTab === "fast" || activeTab === "slow" ? (
              <table>
                <thead>
                  <tr>
                    <th>Rank</th>
                    <th>Product</th>
                    <th>Units Sold</th>
                  </tr>
                </thead>
                <tbody>
                  {(activeTab === "fast" ? data?.top_sellers : data?.bottom_sellers)?.length ? (
                    (activeTab === "fast" ? data!.top_sellers : data!.bottom_sellers).map((s, idx) => (
                      <tr key={s.product_id}>
                        <td><strong>#{idx + 1}</strong></td>
                        <td><strong>{s.product_name}</strong></td>
                        <td>{s.score} units</td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={3} style={{ padding: "24px", color: "#69756b", textAlign: "center" }}>
                        No sales recorded yet. Complete a sale on the Sell page to populate mover rankings.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            ) : (
              <table>
                <thead>
                  <tr>
                    <th>Rank</th>
                    <th>Product</th>
                    <th>Sellable Stock</th>
                    <th>Days of Cover</th>
                    <th>14-Day Speed</th>
                    <th>Suggested Qty</th>
                    <th>Status & Reason</th>
                    <th style={{ textAlign: "right" }}>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {displayedItems.map((item) => (
                    <tr key={item.product_id}>
                      <td>
                        <strong style={{ color: item.color === "red" ? "#b91c1c" : item.color === "amber" ? "#b45309" : "#15803d" }}>
                          #{item.rank}
                        </strong>
                      </td>
                      <td>
                        <div>
                          <strong>{item.product_name}</strong>
                          <div style={{ fontSize: "12px", color: "#69756b" }}>{item.category_name}</div>
                        </div>
                      </td>
                      <td>{item.sellable_stock} units</td>
                      <td>
                        <span style={{ fontWeight: 600 }}>
                          {item.days_of_cover === null ? "∞" : `${item.days_of_cover} days`}
                        </span>
                      </td>
                      <td>{item.selling_speed.toFixed(2)} / day</td>
                      <td>
                        <strong style={{ color: item.suggested_reorder > 0 ? "#1e3a8a" : "#69756b" }}>
                          {item.suggested_reorder > 0 ? `${item.suggested_reorder} units` : "None needed"}
                        </strong>
                      </td>
                      <td>
                        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                          <span className={`badge ${item.color}`}>{item.urgency}</span>
                          <small style={{ color: "#69756b" }}>{item.reason}</small>
                        </div>
                      </td>
                      <td style={{ textAlign: "right" }}>
                        <button className="restock-row-btn" onClick={() => openRestockModal(item)}>
                          Restock
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </section>

        <div className="restock-callout">
          <span className="truck">▭</span>
          <span>
            <strong>Keep your favorites on the shelf.</strong>
            <small>
              Target cover buffer: {data?.target_cover_days ?? 14} days (configurable in Settings).
            </small>
          </span>
        </div>
      </Shell>

      {selectedItem && (
        <div className="modal-overlay" onClick={() => setSelectedItem(null)}>
          <div className="modal-dialog" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div>
                <h2>Receive Stock · {selectedItem.product_name}</h2>
                <p>Add a new batch to replenish inventory and update cover days.</p>
              </div>
              <button type="button" className="modal-close-btn" onClick={() => setSelectedItem(null)}>
                ✕
              </button>
            </div>

            {olderWarning.length > 0 ? (
              <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
                <div style={{ background: "#fff3cd", color: "#856404", padding: "14px 16px", borderRadius: "14px" }}>
                  <strong>⚠ Older stock on shelf — place new batch behind older units!</strong>
                  <ul style={{ margin: "8px 0 0 18px", fontSize: "14px" }}>
                    {olderWarning.map((w) => (
                      <li key={w.batch_id}>
                        Batch #{w.batch_id}: {w.units} units · expires {formatDate(w.expiry_date)} ({w.level})
                      </li>
                    ))}
                  </ul>
                </div>
                <div className="modal-actions">
                  <button className="btn-submit" onClick={() => setSelectedItem(null)}>
                    Got it
                  </button>
                </div>
              </div>
            ) : (
              <form onSubmit={handleRestockSubmit} className="modal-form">
                <div className="form-grid">
                  <div className="form-field">
                    <label>Current Sellable Stock</label>
                    <input
                      type="text"
                      readOnly
                      value={`${selectedItem.sellable_stock} units`}
                      style={{ background: "#f5f4ee" }}
                    />
                  </div>
                  <div className="form-field">
                    <label>Suggested Reorder Qty</label>
                    <input
                      type="text"
                      readOnly
                      value={`${selectedItem.suggested_reorder} units`}
                      style={{ background: "#f5f4ee" }}
                    />
                  </div>
                  <div className="form-field">
                    <label htmlFor="restock-qty">Units to Receive *</label>
                    <input
                      id="restock-qty"
                      type="number"
                      min="1"
                      required
                      value={restockQty}
                      onChange={(e) => setRestockQty(Number(e.target.value))}
                      autoFocus
                    />
                  </div>
                  {selectedItem.tracks_expiry && (
                    <div className="form-field">
                      <label htmlFor="expiry-date">Expiry Date *</label>
                      <input
                        id="expiry-date"
                        type="date"
                        required
                        value={expiryDate}
                        onChange={(e) => setExpiryDate(e.target.value)}
                      />
                    </div>
                  )}
                  <div className="form-field full-width">
                    <label>Estimated Cost</label>
                    <input
                      type="text"
                      readOnly
                      value={`${formatPHP(selectedItem.cost_price)} / unit (Total: ${formatPHP(selectedItem.cost_price * (restockQty || 0))})`}
                      style={{ background: "#f5f4ee" }}
                    />
                  </div>
                </div>
                <div className="modal-actions">
                  <button type="button" className="btn-cancel" onClick={() => setSelectedItem(null)}>
                    Cancel
                  </button>
                  <button type="submit" className="btn-submit">
                    Confirm Restock (+{restockQty} units)
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}
    </>
  );
}
