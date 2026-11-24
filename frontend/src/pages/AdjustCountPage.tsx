import { useEffect, useMemo, useState } from "react";
import Shell from "../components/Shell";
import type { Navigate } from "../types";
import { api, formatDate, type ProductDTO } from "../api";

export default function AdjustCountPage({ navigate }: { navigate: Navigate }) {
  const [products, setProducts] = useState<ProductDTO[]>([]);
  const [selectedProductId, setSelectedProductId] = useState<string>("");
  const [selectedBatchId, setSelectedBatchId] = useState<string>("");
  const [newCount, setNewCount] = useState<string>("");
  const [reason, setReason] = useState<string>("Physical shelf count");
  const [statusMsg, setStatusMsg] = useState<{ type: "ok" | "error"; text: string } | null>(null);

  const loadProducts = async () => {
    const list = await api.getProducts();
    const withBatches = list.filter((p) => p.batches.length > 0);
    setProducts(withBatches);
    if (withBatches.length > 0 && !selectedProductId) {
      setSelectedProductId(String(withBatches[0].id));
      setSelectedBatchId(String(withBatches[0].batches[0].id));
      setNewCount(String(withBatches[0].batches[0].quantity));
    }
  };

  useEffect(() => {
    loadProducts().catch(() => {});
  }, []);

  const selectedProduct = useMemo(
    () => products.find((p) => String(p.id) === selectedProductId) ?? null,
    [products, selectedProductId],
  );

  const selectedBatch = useMemo(
    () => selectedProduct?.batches.find((b) => String(b.id) === selectedBatchId) ?? null,
    [selectedProduct, selectedBatchId],
  );

  const handleProductChange = (pid: string) => {
    setSelectedProductId(pid);
    const prod = products.find((p) => String(p.id) === pid);
    if (prod && prod.batches.length > 0) {
      setSelectedBatchId(String(prod.batches[0].id));
      setNewCount(String(prod.batches[0].quantity));
    } else {
      setSelectedBatchId("");
      setNewCount("");
    }
    setStatusMsg(null);
  };

  const handleBatchChange = (bid: string) => {
    setSelectedBatchId(bid);
    const b = selectedProduct?.batches.find((x) => String(x.id) === bid);
    if (b) setNewCount(String(b.quantity));
    setStatusMsg(null);
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!selectedBatch) return;
    try {
      const res = await api.adjustStock({
        batch_id: selectedBatch.id,
        new_quantity: parseInt(newCount, 10),
        reason: reason.trim(),
      });
      setStatusMsg({
        type: "ok",
        text: `✓ Adjusted Batch #${res.batch_id} from ${res.old_quantity} → ${res.new_quantity} (${res.difference >= 0 ? "+" : ""}${res.difference}).`,
      });
      await loadProducts();
    } catch (err) {
      setStatusMsg({
        type: "error",
        text: err instanceof Error ? err.message : "Adjustment failed.",
      });
    }
  };

  return (
    <Shell
      active="stock"
      page="adjust"
      title={`Adjust count${selectedProduct ? ` · ${selectedProduct.name}` : ""}`}
      subtitle="Update the physical count for a batch with an audit reason"
      navigate={navigate}
      action={
        <button className="purple-pill" onClick={() => navigate("stock")}>
          Back to Stock
        </button>
      }
    >
      <div className="adjust-layout">
        <form className="panel adjustment-form" onSubmit={handleSubmit}>
          <label>
            Product
            <select value={selectedProductId} onChange={(e) => handleProductChange(e.target.value)}>
              {products.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name} ({p.barcode})
                </option>
              ))}
            </select>
          </label>

          <label>
            Batch
            <select value={selectedBatchId} onChange={(e) => handleBatchChange(e.target.value)}>
              {(selectedProduct?.batches ?? []).map((b) => (
                <option key={b.id} value={b.id}>
                  Batch #{b.id} · {b.quantity} units ·{" "}
                  {b.expiry_date ? `exp ${formatDate(b.expiry_date)}` : `rcvd ${formatDate(b.received_date)}`}
                </option>
              ))}
            </select>
          </label>

          <label>
            Current count
            <input value={selectedBatch ? String(selectedBatch.quantity) : "—"} readOnly />
          </label>

          <label>
            New count (after physical check)
            <input
              type="number"
              min="0"
              required
              value={newCount}
              onChange={(e) => setNewCount(e.target.value)}
            />
          </label>

          <label>
            Reason *
            <input
              required
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="e.g. Counted 6 on shelf"
            />
          </label>

          {statusMsg && (
            <div
              style={{
                padding: "10px 14px",
                borderRadius: "12px",
                fontWeight: 600,
                background: statusMsg.type === "ok" ? "#e5efdb" : "#fee2e2",
                color: statusMsg.type === "ok" ? "#245c45" : "#991b1b",
              }}
            >
              {statusMsg.text}
            </div>
          )}

          <button className="checkout" type="submit" disabled={!selectedBatch}>
            Save adjustment
          </button>
          <small>Saved with old count, new count, and reason. History is never edited.</small>
        </form>

        <aside className="fresh-card">
          <span>◇</span>
          <strong>A fresh count.</strong>
          <p>
            Count what’s on your shelf,
            <br />
            then leave a reason to keep
            <br />
            your stock history clear.
          </p>
        </aside>
      </div>
    </Shell>
  );
}
