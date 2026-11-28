import { useEffect, useState } from "react";
import Shell from "../components/Shell";
import type { Navigate } from "../types";
import { api, formatDate, formatPHP, type ReportsDTO } from "../api";

type PeriodType = "Day" | "Week" | "Month" | "Custom";
type SubReportType = "sellers" | "profit" | "spoilage" | "inventory" | null;

export default function ReportsPage({ navigate }: { navigate: Navigate }) {
  const [period, setPeriod] = useState<PeriodType>("Week");
  const [customStart, setCustomStart] = useState(() => {
    const d = new Date();
    d.setDate(d.getDate() - 13);
    return d.toISOString().slice(0, 10);
  });
  const [customEnd, setCustomEnd] = useState(() => new Date().toISOString().slice(0, 10));
  const [data, setData] = useState<ReportsDTO | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeSubReport, setActiveSubReport] = useState<SubReportType>(null);
  const [selectedBarIndex, setSelectedBarIndex] = useState<number | null>(null);

  useEffect(() => {
    let active = true;
    setLoading(true);
    api
      .getReports(period, period === "Custom" ? customStart : undefined, period === "Custom" ? customEnd : undefined)
      .then((res) => {
        if (active) {
          setData(res);
          setSelectedBarIndex(null);
        }
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [period, customStart, customEnd]);

  const summary = data?.summary;
  const series = data?.daily_series ?? [];
  const maxRev = Math.max(1, ...series.map((s) => s.revenue));

  return (
    <>
      <Shell
        active="reports"
        page="reports"
        title="Reports"
        subtitle="Financial performance summary (voided sales excluded)"
        navigate={navigate}
        action={
          <button className="primary blue" onClick={() => setActiveSubReport("inventory")}>
            Inventory Summary
          </button>
        }
      >
        <div className="period-row" style={{ alignItems: "center", flexWrap: "wrap" }}>
          {(["Day", "Week", "Month", "Custom"] as PeriodType[]).map((item) => (
            <button
              key={item}
              className={period === item ? "selected" : ""}
              onClick={() => setPeriod(item)}
            >
              {item}
            </button>
          ))}
          {period === "Custom" && (
            <div style={{ display: "flex", gap: "8px", alignItems: "center", marginLeft: "8px" }}>
              <input type="date" value={customStart} onChange={(e) => setCustomStart(e.target.value)} />
              <span>to</span>
              <input type="date" value={customEnd} onChange={(e) => setCustomEnd(e.target.value)} />
            </div>
          )}
        </div>

        <div className="stat-grid report-stats">
          <article className="stat white">
            <span>Revenue</span>
            <strong>{loading ? "…" : formatPHP(summary?.revenue ?? 0)}</strong>
            <small style={{ color: "#69756b", marginTop: "4px" }}>Net sales excluding voids</small>
          </article>
          <article className="stat green">
            <span>Gross Profit</span>
            <strong>{loading ? "…" : formatPHP(summary?.gross_profit ?? 0)}</strong>
            <small style={{ color: "#245c45", marginTop: "4px" }}>Revenue minus COGS</small>
          </article>
          <article className="stat yellow">
            <span>Gross Margin</span>
            <strong>{loading ? "…" : `${(summary?.margin_pct ?? 0).toFixed(1)}%`}</strong>
            <small style={{ color: "#854d0e", marginTop: "4px" }}>0% when revenue is 0</small>
          </article>
          <article className="stat blush">
            <span>COGS</span>
            <strong>{loading ? "…" : formatPHP(summary?.cogs ?? 0)}</strong>
            <small style={{ color: "#991b1b", marginTop: "4px" }}>Historical batch cost</small>
          </article>
        </div>

        <section className="panel chart-panel">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <h2>
              Daily revenue trend ({data ? `${formatDate(data.start_date)} – ${formatDate(data.end_date)}` : period})
            </h2>
            {selectedBarIndex !== null && series[selectedBarIndex] && (
              <div style={{ background: "#e5efdb", color: "#245c45", padding: "6px 14px", borderRadius: "14px", fontSize: "14px", fontWeight: 600 }}>
                {series[selectedBarIndex].label}: {formatPHP(series[selectedBarIndex].revenue)} ({series[selectedBarIndex].units} units)
              </div>
            )}
          </div>

          <div className="chart" style={{ cursor: "pointer" }}>
            {series.slice(-14).map((pt, index) => {
              const actualIdx = series.length - Math.min(series.length, 14) + index;
              const pct = pt.revenue > 0 ? Math.max(10, Math.round((pt.revenue / maxRev) * 100)) : 4;
              return (
                <div
                  key={pt.date}
                  onClick={() => setSelectedBarIndex(actualIdx)}
                  style={{ textAlign: "center", transition: "transform 0.15s" }}
                >
                  <span
                    style={{
                      height: `${pct}%`,
                      background: selectedBarIndex === actualIdx ? "#245c45" : undefined,
                    }}
                    className={`bar bar-${index % 7}`}
                  />
                  <small>{pt.label}</small>
                </div>
              );
            })}
          </div>
          <small style={{ color: "#69756b", display: "block", marginTop: "12px", textAlign: "right" }}>
            * Click any bar to inspect daily sales breakdown
          </small>
        </section>

        <div className="report-links">
          <button onClick={() => setActiveSubReport("sellers")}>Best and worst sellers ›</button>
          <button onClick={() => setActiveSubReport("profit")}>Profit per item ›</button>
          <button onClick={() => setActiveSubReport("spoilage")}>Spoilage loss ({formatPHP(summary?.spoilage ?? 0)}) ›</button>
          <button onClick={() => setActiveSubReport("inventory")}>Inventory value ({formatPHP(summary?.inventory_value ?? 0)}) ›</button>
        </div>
      </Shell>

      {activeSubReport && data && (
        <div className="modal-overlay" onClick={() => setActiveSubReport(null)}>
          <div className="modal-dialog wide" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div>
                <h2>
                  {activeSubReport === "sellers" && "Best and Worst Sellers"}
                  {activeSubReport === "profit" && "Profit per Item Report"}
                  {activeSubReport === "spoilage" && "Spoilage & Expiry Losses"}
                  {activeSubReport === "inventory" && "Total Sellable Inventory Valuation"}
                </h2>
              </div>
              <button type="button" className="modal-close-btn" onClick={() => setActiveSubReport(null)}>
                ✕
              </button>
            </div>

            {activeSubReport === "sellers" && (
              <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
                <div>
                  <h3 style={{ color: "#166534", marginBottom: "8px", fontSize: "16px" }}>▲ Top Sellers</h3>
                  {data.top_sellers.length === 0 ? (
                    <p style={{ color: "#69756b" }}>No sales recorded yet.</p>
                  ) : (
                    <table style={{ width: "100%" }}>
                      <thead>
                        <tr><th>Product</th><th>Units Sold</th></tr>
                      </thead>
                      <tbody>
                        {data.top_sellers.map((s) => (
                          <tr key={s.product_id}>
                            <td><strong>{s.product_name}</strong></td>
                            <td>{s.score} units</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  )}
                </div>
                <div>
                  <h3 style={{ color: "#991b1b", marginBottom: "8px", fontSize: "16px" }}>▼ Bottom Sellers</h3>
                  {data.bottom_sellers.length === 0 ? (
                    <p style={{ color: "#69756b" }}>No sales recorded yet.</p>
                  ) : (
                    <table style={{ width: "100%" }}>
                      <thead>
                        <tr><th>Product</th><th>Units Sold</th></tr>
                      </thead>
                      <tbody>
                        {data.bottom_sellers.map((s) => (
                          <tr key={s.product_id}>
                            <td><strong>{s.product_name}</strong></td>
                            <td>{s.score} units</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  )}
                </div>
              </div>
            )}

            {activeSubReport === "profit" && (
              <div className="table-scroll">
                {data.profit_per_item.length === 0 ? (
                  <p style={{ color: "#69756b" }}>No non-voided sales in this period.</p>
                ) : (
                  <table style={{ width: "100%" }}>
                    <thead>
                      <tr>
                        <th>Product</th>
                        <th>Units Sold</th>
                        <th>Revenue</th>
                        <th>Total Profit</th>
                        <th>Margin %</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.profit_per_item.map((item) => (
                        <tr key={item.product_id}>
                          <td><strong>{item.product_name}</strong></td>
                          <td>{item.units_sold}</td>
                          <td>{formatPHP(item.revenue)}</td>
                          <td><strong style={{ color: "#166534" }}>{formatPHP(item.total_profit)}</strong></td>
                          <td>{item.margin_pct.toFixed(1)}%</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            )}

            {activeSubReport === "spoilage" && (
              <div style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
                <div style={{ background: "#fee2e2", padding: "14px 18px", borderRadius: "16px", color: "#991b1b" }}>
                  <span style={{ fontSize: "13px" }}>Total Spoilage Losses (Write-offs)</span>
                  <h3 style={{ fontSize: "24px", margin: "4px 0" }}>{formatPHP(data.summary.spoilage)}</h3>
                </div>
                <div className="table-scroll">
                  {data.spoilage_items.length === 0 ? (
                    <p style={{ color: "#245c45", fontWeight: 600 }}>✓ Zero spoilage write-offs in this period.</p>
                  ) : (
                    <table style={{ width: "100%" }}>
                      <thead>
                        <tr>
                          <th>Batch</th>
                          <th>Product</th>
                          <th>Category</th>
                          <th>Units</th>
                          <th>Unit Cost</th>
                          <th>Total Loss</th>
                        </tr>
                      </thead>
                      <tbody>
                        {data.spoilage_items.map((sp, idx) => (
                          <tr key={`${sp.batch_id}-${idx}`}>
                            <td>#{sp.batch_id}</td>
                            <td><strong>{sp.product_name}</strong></td>
                            <td>{sp.category_name}</td>
                            <td>{sp.quantity}</td>
                            <td>{formatPHP(sp.unit_cost)}</td>
                            <td><strong style={{ color: "#991b1b" }}>{formatPHP(sp.total_loss)}</strong></td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  )}
                </div>
              </div>
            )}

            {activeSubReport === "inventory" && (
              <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "14px" }}>
                  <div style={{ background: "#dbeafe", padding: "14px", borderRadius: "16px", color: "#1e40af" }}>
                    <span style={{ fontSize: "13px" }}>Total Retail Value</span>
                    <h3 style={{ fontSize: "20px", margin: "4px 0" }}>{formatPHP(data.inventory_valuation.total_retail_value)}</h3>
                  </div>
                  <div style={{ background: "#e5efdb", padding: "14px", borderRadius: "16px", color: "#166534" }}>
                    <span style={{ fontSize: "13px" }}>Total Cost Value</span>
                    <h3 style={{ fontSize: "20px", margin: "4px 0" }}>{formatPHP(data.inventory_valuation.total_cost_value)}</h3>
                  </div>
                  <div style={{ background: "#fef3c7", padding: "14px", borderRadius: "16px", color: "#92400e" }}>
                    <span style={{ fontSize: "13px" }}>Potential Profit</span>
                    <h3 style={{ fontSize: "20px", margin: "4px 0" }}>{formatPHP(data.inventory_valuation.potential_profit)}</h3>
                  </div>
                </div>
                <div className="table-scroll">
                  <table style={{ width: "100%" }}>
                    <thead>
                      <tr>
                        <th>Category</th>
                        <th>Sellable Units</th>
                        <th>Cost Value</th>
                        <th>Retail Value</th>
                        <th>Est. Margin</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.inventory_valuation.by_category.map((cv) => (
                        <tr key={cv.category}>
                          <td><strong>{cv.category}</strong></td>
                          <td>{cv.units}</td>
                          <td>{formatPHP(cv.cost_value)}</td>
                          <td>{formatPHP(cv.retail_value)}</td>
                          <td><span className="badge green">{cv.margin_pct.toFixed(1)}%</span></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            <div className="modal-actions">
              <button type="button" className="btn-cancel" onClick={() => setActiveSubReport(null)}>
                Close Report
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
