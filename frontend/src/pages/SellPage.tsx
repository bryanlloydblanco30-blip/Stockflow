import { useCallback, useEffect, useRef, useState } from "react";
import Shell from "../components/Shell";
import BarcodeScanner from "../components/BarcodeScanner";
import type { Navigate } from "../types";
import { api, formatDate, formatPHP, type CartDTO, type ProductDTO, type ReceiptDTO } from "../api";

type ScanFeedback = {
  type: "ok" | "warn" | "error";
  msg: string;
  unknownBarcode?: string;
} | null;

export default function SellPage({ navigate }: { navigate: Navigate }) {
  const [cart, setCart] = useState<CartDTO>({ lines: [], item_count: 0, total: 0 });
  const [sampleProducts, setSampleProducts] = useState<ProductDTO[]>([]);
  const [barcodeInput, setBarcodeInput] = useState("");
  const [isScannerOpen, setIsScannerOpen] = useState(false);
  const [feedback, setFeedback] = useState<ScanFeedback>(null);
  const [isCheckoutOpen, setIsCheckoutOpen] = useState(false);
  const [cashTendered, setCashTendered] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [receipt, setReceipt] = useState<ReceiptDTO | null>(null);
  const barcodeRef = useRef<HTMLInputElement>(null);

  const showFeedback = (fb: ScanFeedback) => {
    setFeedback(fb);
    if (fb && !fb.unknownBarcode) {
      setTimeout(() => setFeedback(null), 3200);
    }
  };

  const refreshCart = useCallback(async () => {
    try {
      const c = await api.getCart();
      setCart(c);
    } catch (err) {
      showFeedback({
        type: "error",
        msg: err instanceof Error ? err.message : "Failed to sync cart with backend.",
      });
    }
  }, []);

  useEffect(() => {
    refreshCart();
    api
      .getProducts()
      .then((list) => setSampleProducts(list.filter((p) => p.sellable_stock > 0)))
      .catch(() => {});
  }, [refreshCart]);

  // Global keyboard shortcuts: Esc closes modals, F2 focuses barcode input
  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setIsCheckoutOpen(false);
        setIsScannerOpen(false);
        setReceipt(null);
      } else if (e.key === "F2") {
        e.preventDefault();
        barcodeRef.current?.focus();
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, []);

  const subtotal = cart.total;
  const cashNum = parseFloat(cashTendered) || 0;
  const change = cashNum - subtotal;

  const addByBarcode = async (raw: string) => {
    const code = raw.trim();
    if (!code) return;
    try {
      const res = await api.addToCart({ barcode: code, quantity: 1 });
      if (res.status === "UNKNOWN") {
        showFeedback({
          type: "error",
          msg: `Unknown barcode: ${code}.`,
          unknownBarcode: code,
        });
        return;
      }
      setCart(res.cart);
      showFeedback({
        type: "ok",
        msg: `Added "${res.product?.name ?? code}" to cart`,
      });
      setBarcodeInput("");
      barcodeRef.current?.focus();
    } catch (err) {
      showFeedback({
        type: "warn",
        msg: err instanceof Error ? err.message : "Could not add item.",
      });
    }
  };

  const handleSimulateScan = () => {
    if (sampleProducts.length === 0) {
      showFeedback({ type: "warn", msg: "No sellable products available to simulate." });
      return;
    }
    const randomProd = sampleProducts[Math.floor(Math.random() * sampleProducts.length)];
    addByBarcode(randomProd.barcode);
  };

  const changeQty = async (productId: number, newQty: number) => {
    try {
      const updated = await api.updateCartItem(productId, newQty);
      setCart(updated);
    } catch (err) {
      showFeedback({
        type: "warn",
        msg: err instanceof Error ? err.message : "Could not update quantity.",
      });
    }
  };

  const removeItem = async (productId: number) => {
    try {
      const updated = await api.removeCartItem(productId);
      setCart(updated);
    } catch (err) {
      showFeedback({
        type: "error",
        msg: err instanceof Error ? err.message : "Could not remove item.",
      });
    }
  };

  const handleBarcodeKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      e.preventDefault();
      if (barcodeInput.trim()) {
        addByBarcode(barcodeInput);
      } else if (cart.lines.length > 0) {
        setIsCheckoutOpen(true);
      }
    }
  };

  const handleScanDetected = (code: string) => {
    setIsScannerOpen(false);
    setBarcodeInput(code);
    addByBarcode(code);
  };

  const handleCheckout = async (e: React.FormEvent) => {
    e.preventDefault();
    if (cashNum < subtotal || submitting) return;
    setSubmitting(true);
    try {
      const rec = await api.checkout(cashNum);
      setReceipt(rec);
      setCart({ lines: [], item_count: 0, total: 0 });
      setBarcodeInput("");
      setIsCheckoutOpen(false);
      setCashTendered("");
    } catch (err) {
      showFeedback({
        type: "error",
        msg: err instanceof Error ? err.message : "Checkout failed.",
      });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <>
      <Shell
        active="sell"
        page="sell"
        title="Sell"
        subtitle="Scan items or enter barcode to build a sale (F2 to focus barcode)"
        navigate={navigate}
      >
        <div className="sell-layout">
          <section className="panel sale-panel">
            <div className="scan-row">
              <input
                ref={barcodeRef}
                aria-label="Barcode"
                placeholder="Scan or type barcode, then press Enter"
                value={barcodeInput}
                onChange={(e) => setBarcodeInput(e.target.value)}
                onKeyDown={handleBarcodeKeyDown}
                autoFocus
              />
              <button
                className="blue-pill"
                onClick={() => setIsScannerOpen(true)}
                title="Open camera barcode scanner"
              >
                📷 Scan
              </button>
              <button
                className="purple-pill"
                onClick={handleSimulateScan}
                title="Simulate scanning a sample barcode"
              >
                Simulate Scan
              </button>
            </div>

            {feedback && (
              <div
                style={{
                  padding: "10px 16px",
                  borderRadius: "12px",
                  fontSize: "14px",
                  fontWeight: 600,
                  marginBottom: "8px",
                  background:
                    feedback.type === "ok"
                      ? "#e5efdb"
                      : feedback.type === "warn"
                      ? "#fff3cd"
                      : "#fee2e2",
                  color:
                    feedback.type === "ok"
                      ? "#245c45"
                      : feedback.type === "warn"
                      ? "#856404"
                      : "#991b1b",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  gap: "10px",
                }}
              >
                <span>
                  {feedback.type === "ok" ? "✓ " : feedback.type === "warn" ? "⚠ " : "✗ "}
                  {feedback.msg}
                </span>
                {feedback.unknownBarcode && (
                  <button
                    className="blue-pill"
                    style={{ height: "34px", padding: "0 14px", fontSize: "13px" }}
                    onClick={() => navigate("stock")}
                  >
                    + Register product
                  </button>
                )}
              </div>
            )}

            <div className="table-scroll">
              {cart.lines.length === 0 ? (
                <div style={{ textAlign: "center", padding: "48px 24px", color: "#69756b" }}>
                  <div style={{ fontSize: "36px", marginBottom: "12px" }}>🛒</div>
                  <strong style={{ display: "block", marginBottom: "6px" }}>Cart is empty</strong>
                  <span style={{ fontSize: "14px" }}>
                    Scan a barcode, click Simulate Scan, or type a barcode and press Enter.
                  </span>
                </div>
              ) : (
                <table>
                  <thead>
                    <tr>
                      <th>Item</th>
                      <th>Qty</th>
                      <th>Unit price</th>
                      <th>Line total</th>
                      <th />
                    </tr>
                  </thead>
                  <tbody>
                    {cart.lines.map((item) => (
                      <tr key={item.product_id}>
                        <td>
                          <div>
                            <strong>{item.product_name}</strong>
                            <div style={{ fontSize: "11px", color: "#69756b" }}>
                              {item.barcode} · {item.sellable_stock} sellable
                            </div>
                          </div>
                        </td>
                        <td>
                          <div className="quantity">
                            <button onClick={() => changeQty(item.product_id, item.quantity - 1)}>−</button>
                            <span>{item.quantity}</span>
                            <button
                              onClick={() => changeQty(item.product_id, item.quantity + 1)}
                              disabled={item.quantity >= item.sellable_stock}
                              style={item.quantity >= item.sellable_stock ? { opacity: 0.4 } : {}}
                            >
                              +
                            </button>
                          </div>
                        </td>
                        <td>{formatPHP(item.unit_price)}</td>
                        <td>
                          <strong>{formatPHP(item.subtotal)}</strong>
                        </td>
                        <td>
                          <button
                            className="purple-pill small"
                            onClick={() => removeItem(item.product_id)}
                          >
                            Remove
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </section>

          <aside className="sale-summary">
            <section className="panel summary-card">
              <h3>Summary</h3>
              <p>
                <span>Items</span>
                <strong>{cart.item_count}</strong>
              </p>
              <p>
                <span>Subtotal</span>
                <strong>{formatPHP(subtotal)}</strong>
              </p>
              <p>
                <span>Payment</span>
                <strong>Cash only</strong>
              </p>
              <hr />
              <p className="total">
                <span>Total</span>
                <strong>{formatPHP(subtotal)}</strong>
              </p>
              <button
                className="checkout"
                onClick={() => cart.lines.length > 0 && setIsCheckoutOpen(true)}
                disabled={cart.lines.length === 0}
                style={cart.lines.length === 0 ? { opacity: 0.5, cursor: "not-allowed" } : {}}
              >
                Checkout (Enter)
              </button>
            </section>
            <section className="green-message">
              <strong>
                Sorted by earliest expiry,
                <br />
                expired stock blocked.
              </strong>
              <span>Older stock sells first automatically.</span>
            </section>
          </aside>
        </div>
      </Shell>

      {isScannerOpen && (
        <BarcodeScanner onDetected={handleScanDetected} onClose={() => setIsScannerOpen(false)} />
      )}

      {isCheckoutOpen && (
        <div className="modal-overlay" onClick={() => setIsCheckoutOpen(false)}>
          <div className="modal-dialog" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div>
                <h2>Checkout (Cash Only)</h2>
                <p>Confirm cash tendered to deduct stock and complete sale.</p>
              </div>
              <button
                type="button"
                className="modal-close-btn"
                onClick={() => setIsCheckoutOpen(false)}
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleCheckout} className="modal-form">
              <div
                style={{
                  background: "#f4f1e8",
                  borderRadius: "16px",
                  padding: "16px",
                  display: "flex",
                  flexDirection: "column",
                  gap: "6px",
                }}
              >
                {cart.lines.map((item) => (
                  <div
                    key={item.product_id}
                    style={{ display: "flex", justifyContent: "space-between", fontSize: "14px" }}
                  >
                    <span>
                      {item.product_name} × {item.quantity}
                    </span>
                    <strong>{formatPHP(item.subtotal)}</strong>
                  </div>
                ))}
                <hr style={{ borderColor: "#e0dec4", margin: "8px 0" }} />
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    fontWeight: 700,
                    fontSize: "16px",
                  }}
                >
                  <span>Total</span>
                  <span style={{ color: "#245c45" }}>{formatPHP(subtotal)}</span>
                </div>
              </div>

              <div className="form-field">
                <label htmlFor="cash-tendered">Cash Tendered (PHP)</label>
                <input
                  id="cash-tendered"
                  type="number"
                  step="0.01"
                  min={subtotal}
                  required
                  autoFocus
                  value={cashTendered}
                  onChange={(e) => setCashTendered(e.target.value)}
                  placeholder={`Min ${formatPHP(subtotal)}`}
                />
              </div>

              {cashNum >= subtotal && cashTendered !== "" && (
                <div
                  style={{
                    background: "#e5efdb",
                    borderRadius: "14px",
                    padding: "12px 16px",
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    color: "#245c45",
                    fontWeight: 700,
                    fontSize: "16px",
                  }}
                >
                  <span>Change</span>
                  <span>{formatPHP(change)}</span>
                </div>
              )}

              {cashNum > 0 && cashNum < subtotal && (
                <div
                  style={{
                    background: "#fee2e2",
                    borderRadius: "14px",
                    padding: "10px 16px",
                    color: "#991b1b",
                    fontSize: "14px",
                    fontWeight: 600,
                  }}
                >
                  ✗ Cash is {formatPHP(subtotal - cashNum)} short.
                </div>
              )}

              <div className="modal-actions">
                <button
                  type="button"
                  className="btn-cancel"
                  onClick={() => setIsCheckoutOpen(false)}
                >
                  Cancel (Esc)
                </button>
                <button
                  type="submit"
                  className="btn-submit"
                  disabled={submitting || cashNum < subtotal || cashTendered === ""}
                >
                  {submitting ? "Processing…" : "Confirm Sale ✓"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {receipt && (
        <div className="modal-overlay" onClick={() => setReceipt(null)}>
          <div className="modal-dialog" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div>
                <h2 style={{ color: "#245c45" }}>✓ Sale Complete (#{receipt.transaction_id})</h2>
                <p>Receipt — {formatDate(receipt.date_time)}</p>
              </div>
              <button type="button" className="modal-close-btn" onClick={() => setReceipt(null)}>
                ✕
              </button>
            </div>

            <div
              style={{
                background: "#f4f1e8",
                borderRadius: "16px",
                padding: "20px",
                display: "flex",
                flexDirection: "column",
                gap: "8px",
                fontFamily: "monospace",
              }}
            >
              <div style={{ textAlign: "center", fontWeight: 700, fontSize: "16px", marginBottom: "4px" }}>
                StockFlow — Point of Sale
              </div>
              <div style={{ textAlign: "center", fontSize: "12px", color: "#69756b", marginBottom: "8px" }}>
                Tx #{receipt.transaction_id} · {formatDate(receipt.date_time)}
              </div>
              {receipt.lines.map((line) => (
                <div
                  key={line.product_id}
                  style={{ display: "flex", justifyContent: "space-between", fontSize: "14px" }}
                >
                  <span>
                    {line.product_name} × {line.quantity}
                  </span>
                  <span>{formatPHP(line.subtotal)}</span>
                </div>
              ))}
              <hr style={{ borderColor: "#c5c2b0", margin: "8px 0" }} />
              <div style={{ display: "flex", justifyContent: "space-between", fontWeight: 700 }}>
                <span>TOTAL</span>
                <span>{formatPHP(receipt.total)}</span>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "13px", color: "#69756b" }}>
                <span>Cash</span>
                <span>{formatPHP(receipt.cash_given)}</span>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", fontWeight: 700, color: "#245c45" }}>
                <span>CHANGE</span>
                <span>{formatPHP(receipt.change)}</span>
              </div>
            </div>

            {receipt.low_stock_alerts.length > 0 && (
              <div
                style={{
                  background: "#fff3cd",
                  color: "#856404",
                  borderRadius: "12px",
                  padding: "10px 14px",
                  fontSize: "13px",
                  fontWeight: 600,
                }}
              >
                ⚠ Low-stock alert:{" "}
                {receipt.low_stock_alerts
                  .map((a) => `${a.product_name} (${a.remaining_stock} left)`)
                  .join(", ")}
              </div>
            )}

            <div className="modal-actions">
              <button className="btn-cancel" onClick={() => setReceipt(null)}>
                Close
              </button>
              <button
                className="btn-submit"
                onClick={() => {
                  setReceipt(null);
                  barcodeRef.current?.focus();
                }}
              >
                New Sale
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
