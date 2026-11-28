import { useCallback, useEffect, useMemo, useState } from "react";
import Shell from "../components/Shell";
import BarcodeScanner from "../components/BarcodeScanner";
import type { Navigate } from "../types";
import { api, formatDate, formatPHP, type CategoryDTO, type ProductDTO } from "../api";

function badgeColor(level: string, isLow: boolean): string {
  if (level === "EXPIRED" || level === "RED") return "red";
  if (level === "AMBER" || isLow) return "amber";
  return "green";
}

export default function StockPage({ navigate }: { navigate: Navigate }) {
  const [products, setProducts] = useState<ProductDTO[]>([]);
  const [categories, setCategories] = useState<CategoryDTO[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [banner, setBanner] = useState<string | null>(null);

  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState("All");
  const [selectedCategory, setSelectedCategory] = useState("All");

  // Modals
  const [isRegisterOpen, setIsRegisterOpen] = useState(false);
  const [isScannerOpen, setIsScannerOpen] = useState(false);
  const [detailProduct, setDetailProduct] = useState<ProductDTO | null>(null);
  const [receiveTarget, setReceiveTarget] = useState<ProductDTO | null>(null);

  // Register form state
  const [formBarcode, setFormBarcode] = useState("");
  const [formName, setFormName] = useState("");
  const [formCategoryId, setFormCategoryId] = useState<string>("");
  const [formUnits, setFormUnits] = useState("");
  const [formCost, setFormCost] = useState("");
  const [formPrice, setFormPrice] = useState("");
  const [formReorder, setFormReorder] = useState("10");
  const [formExpiry, setFormExpiry] = useState("");

  // Receive stock form state
  const [recQty, setRecQty] = useState("12");
  const [recCost, setRecCost] = useState("");
  const [recExpiry, setRecExpiry] = useState("");
  const [olderWarning, setOlderWarning] = useState<
    { batch_id: number; expiry_date: string; units: number; level: string }[]
  >([]);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [prods, cats] = await Promise.all([api.getProducts(), api.getCategories()]);
      setProducts(prods);
      setCategories(cats);
      if (cats.length > 0 && !formCategoryId) {
        setFormCategoryId(String(cats[0].id));
      }
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load inventory.");
    } finally {
      setLoading(false);
    }
  }, [formCategoryId]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const selectedRegCat = categories.find((c) => String(c.id) === formCategoryId);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return products.filter((p) => {
      if (q && !`${p.barcode} ${p.name} ${p.category_name}`.toLowerCase().includes(q)) {
        return false;
      }
      if (selectedCategory !== "All" && p.category_name !== selectedCategory) return false;
      if (filter === "Low") return p.is_low_stock;
      if (filter === "Near Expiry") return ["RED", "AMBER", "EXPIRED"].includes(p.alert_level);
      if (filter === "Untracked") return !p.tracks_expiry;
      return true;
    });
  }, [products, query, filter, selectedCategory]);

  const handleRegisterSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.createProduct({
        barcode: formBarcode.trim(),
        name: formName.trim(),
        category_id: formCategoryId ? Number(formCategoryId) : null,
        cost_price: parseFloat(formCost) || 0,
        selling_price: parseFloat(formPrice) || 0,
        reorder_level: parseInt(formReorder, 10) || 0,
        initial_stock: parseInt(formUnits, 10) || 0,
        expiry_date: selectedRegCat?.tracks_expiry === false ? null : formExpiry || null,
      });
      setIsRegisterOpen(false);
      setFormBarcode("");
      setFormName("");
      setFormUnits("");
      setFormCost("");
      setFormPrice("");
      setFormExpiry("");
      setBanner("✓ Product registered and ready for sale.");
      setTimeout(() => setBanner(null), 3500);
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to register product.");
    }
  };

  const openReceiveModal = (p: ProductDTO) => {
    setReceiveTarget(p);
    setRecQty("12");
    setRecCost(String(p.cost_price));
    setRecExpiry("");
    setOlderWarning([]);
  };

  const handleReceiveSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!receiveTarget) return;
    try {
      const res = await api.receiveStock({
        product_id: receiveTarget.id,
        quantity: parseInt(recQty, 10),
        cost_price: parseFloat(recCost) || receiveTarget.cost_price,
        expiry_date: receiveTarget.tracks_expiry ? recExpiry || null : null,
      });
      if (res.older_batches_warning.length > 0) {
        setOlderWarning(res.older_batches_warning);
      } else {
        setReceiveTarget(null);
      }
      setBanner(`✓ Received +${recQty} units of "${receiveTarget.name}".`);
      setTimeout(() => setBanner(null), 4000);
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to receive stock.");
    }
  };

  return (
    <>
      <Shell
        active="stock"
        page="stock"
        title="Stock"
        subtitle="Manage products, batches, and stock availability"
        navigate={navigate}
        action={
          <button className="primary blue" onClick={() => setIsRegisterOpen(true)}>
            + Register Product
          </button>
        }
      >
        {error && (
          <div style={{ background: "#fee2e2", color: "#991b1b", padding: "10px 16px", borderRadius: "12px", marginBottom: "10px", fontWeight: 600 }}>
            ⚠ {error}
          </div>
        )}
        {banner && (
          <div style={{ background: "#e5efdb", color: "#245c45", padding: "10px 16px", borderRadius: "12px", marginBottom: "10px", fontWeight: 600 }}>
            {banner}
          </div>
        )}

        <input
          className="search-input"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search products or barcode"
          aria-label="Search products"
        />

        <div className="filter-row" style={{ display: "flex", gap: "8px", flexWrap: "wrap", alignItems: "center" }}>
          {["All", "Low", "Near Expiry", "Untracked"].map((f) => (
            <button key={f} className={filter === f ? "blue-pill" : ""} onClick={() => setFilter(f)}>
              {f}
            </button>
          ))}
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            style={{
              height: "46px",
              borderRadius: "23px",
              padding: "0 18px",
              border: "1px solid #dce3d6",
              background: "#fff",
              color: "#243352",
              fontSize: "14px",
              fontWeight: 500,
              cursor: "pointer",
            }}
          >
            <option value="All">All Categories ({products.length})</option>
            {categories.map((cat) => (
              <option key={cat.id} value={cat.name}>
                {cat.name}
              </option>
            ))}
          </select>
          <span style={{ fontSize: "13px", color: "#69756b", marginLeft: "auto" }}>
            Showing <strong>{filtered.length}</strong> of {products.length} products
          </span>
        </div>

        <section className="panel table-panel stock-table">
          <div className="table-scroll">
            {loading ? (
              <p style={{ padding: "24px", color: "#69756b" }}>Loading products from SQLite…</p>
            ) : filtered.length === 0 ? (
              <p style={{ padding: "24px", color: "#69756b" }}>No products match your search or filter.</p>
            ) : (
              <table>
                <thead>
                  <tr>
                    <th>Barcode</th>
                    <th>Name</th>
                    <th>Category</th>
                    <th>Sellable</th>
                    <th>Cost</th>
                    <th>Price</th>
                    <th>Earliest Expiry</th>
                    <th>Status</th>
                    <th style={{ textAlign: "right" }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((p) => (
                    <tr key={p.id}>
                      <td><code>{p.barcode}</code></td>
                      <td>
                        <button
                          style={{
                            background: "none",
                            border: "none",
                            padding: 0,
                            textAlign: "left",
                            fontWeight: 700,
                            color: "#243352",
                            cursor: "pointer",
                            textDecoration: "underline",
                          }}
                          onClick={() => setDetailProduct(p)}
                        >
                          {p.name}
                        </button>
                      </td>
                      <td>{p.category_name}</td>
                      <td>
                        <strong>{p.sellable_stock}</strong>
                        {p.expired_stock > 0 && (
                          <small style={{ color: "#991b1b", display: "block" }}>
                            +{p.expired_stock} expired
                          </small>
                        )}
                      </td>
                      <td>{formatPHP(p.cost_price)}</td>
                      <td>{formatPHP(p.selling_price)}</td>
                      <td><small>{p.tracks_expiry ? formatDate(p.earliest_expiry) : "No expiry"}</small></td>
                      <td>
                        <span className={`badge ${badgeColor(p.alert_level, p.is_low_stock)}`}>
                          {p.status_label}
                        </span>
                      </td>
                      <td style={{ textAlign: "right", whiteSpace: "nowrap" }}>
                        <button
                          className="restock-row-btn"
                          style={{ marginRight: "6px" }}
                          onClick={() => openReceiveModal(p)}
                        >
                          + Receive
                        </button>
                        <button className="purple-pill small" onClick={() => setDetailProduct(p)}>
                          Batches ({p.batches.length})
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </section>

        <div className="page-closing">
          <strong>Every shelf, a little more organized.</strong>
          <span>Click any product to inspect its batches, receive stock, or adjust counts.</span>
        </div>
      </Shell>

      {isScannerOpen && (
        <BarcodeScanner
          onDetected={(code) => {
            setFormBarcode(code);
            setIsScannerOpen(false);
            setIsRegisterOpen(true);
          }}
          onClose={() => setIsScannerOpen(false)}
        />
      )}

      {/* Product Detail & FEFO Batches Modal */}
      {detailProduct && (
        <div className="modal-overlay" onClick={() => setDetailProduct(null)}>
          <div className="modal-dialog wide" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div>
                <h2>{detailProduct.name}</h2>
                <p>
                  Barcode: <code>{detailProduct.barcode}</code> · {detailProduct.category_name} · Reorder at{" "}
                  {detailProduct.reorder_level} units
                </p>
              </div>
              <button type="button" className="modal-close-btn" onClick={() => setDetailProduct(null)}>
                ✕
              </button>
            </div>

            <div className="table-scroll">
              <table style={{ width: "100%" }}>
                <thead>
                  <tr>
                    <th>Batch ID</th>
                    <th>Received</th>
                    <th>Expiry</th>
                    <th>Units</th>
                    <th>Unit Cost</th>
                    <th>Alert Level</th>
                    <th>Shelf Front</th>
                  </tr>
                </thead>
                <tbody>
                  {detailProduct.batches.length === 0 ? (
                    <tr>
                      <td colSpan={7} style={{ textAlign: "center", color: "#69756b", padding: "18px" }}>
                        No active batches in stock.
                      </td>
                    </tr>
                  ) : (
                    detailProduct.batches.map((b) => (
                      <tr key={b.id}>
                        <td>#{b.id}</td>
                        <td>{formatDate(b.received_date)}</td>
                        <td>{detailProduct.tracks_expiry ? formatDate(b.expiry_date) : "No expiry"}</td>
                        <td><strong>{b.quantity}</strong></td>
                        <td>{formatPHP(b.cost_price)}</td>
                        <td>
                          <span className={`badge ${badgeColor(b.level, false)}`}>{b.level}</span>
                        </td>
                        <td>{b.moved_to_front ? "✓ Rotated" : "—"}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>

            <div className="modal-actions">
              <button
                className="btn-cancel"
                onClick={() => {
                  setDetailProduct(null);
                  navigate("adjust");
                }}
              >
                Adjust Count
              </button>
              <button
                className="btn-submit"
                onClick={() => {
                  const target = detailProduct;
                  setDetailProduct(null);
                  openReceiveModal(target);
                }}
              >
                + Receive Stock
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Receive Stock Modal (with IN-5 Older-Stock Warning) */}
      {receiveTarget && (
        <div className="modal-overlay" onClick={() => setReceiveTarget(null)}>
          <div className="modal-dialog" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div>
                <h2>Receive Stock · {receiveTarget.name}</h2>
                <p>Add a new delivery batch to this product's inventory.</p>
              </div>
              <button type="button" className="modal-close-btn" onClick={() => setReceiveTarget(null)}>
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
                  <button className="btn-submit" onClick={() => setReceiveTarget(null)}>
                    Got it
                  </button>
                </div>
              </div>
            ) : (
              <form onSubmit={handleReceiveSubmit} className="modal-form">
                <div className="form-grid">
                  <div className="form-field">
                    <label htmlFor="rec-qty">Units Received *</label>
                    <input
                      id="rec-qty"
                      type="number"
                      min="1"
                      required
                      value={recQty}
                      onChange={(e) => setRecQty(e.target.value)}
                      autoFocus
                    />
                  </div>
                  <div className="form-field">
                    <label htmlFor="rec-cost">Unit Cost (PHP) *</label>
                    <input
                      id="rec-cost"
                      type="number"
                      step="0.01"
                      min="0"
                      required
                      value={recCost}
                      onChange={(e) => setRecCost(e.target.value)}
                    />
                  </div>
                  {receiveTarget.tracks_expiry && (
                    <div className="form-field full-width">
                      <label htmlFor="rec-expiry">Expiry Date *</label>
                      <input
                        id="rec-expiry"
                        type="date"
                        required
                        value={recExpiry}
                        onChange={(e) => setRecExpiry(e.target.value)}
                      />
                    </div>
                  )}
                </div>
                <div className="modal-actions">
                  <button type="button" className="btn-cancel" onClick={() => setReceiveTarget(null)}>
                    Cancel
                  </button>
                  <button type="submit" className="btn-submit">
                    Save Batch
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}

      {/* Register Product Modal */}
      {isRegisterOpen && (
        <div className="modal-overlay" onClick={() => setIsRegisterOpen(false)}>
          <div className="modal-dialog" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div>
                <h2>Register Product</h2>
                <p>Add a new product to your store catalog.</p>
              </div>
              <button type="button" className="modal-close-btn" onClick={() => setIsRegisterOpen(false)}>
                ✕
              </button>
            </div>

            <form onSubmit={handleRegisterSubmit} className="modal-form">
              <div className="form-grid">
                <div className="form-field">
                  <label htmlFor="reg-barcode">Barcode *</label>
                  <div style={{ display: "flex", gap: "8px" }}>
                    <input
                      id="reg-barcode"
                      type="text"
                      required
                      value={formBarcode}
                      onChange={(e) => setFormBarcode(e.target.value)}
                      placeholder="e.g. 4800010007"
                      autoFocus
                      style={{ flex: 1 }}
                    />
                    <button
                      type="button"
                      title="Scan barcode with camera"
                      onClick={() => setIsScannerOpen(true)}
                      style={{
                        height: "48px",
                        padding: "0 14px",
                        borderRadius: "12px",
                        background: "#245c45",
                        color: "#fff",
                        border: "none",
                        cursor: "pointer",
                        fontSize: "18px",
                      }}
                    >
                      📷
                    </button>
                  </div>
                </div>

                <div className="form-field">
                  <label htmlFor="reg-name">Product Name *</label>
                  <input
                    id="reg-name"
                    type="text"
                    required
                    value={formName}
                    onChange={(e) => setFormName(e.target.value)}
                    placeholder="e.g. Fresh Milk 1L"
                  />
                </div>

                <div className="form-field">
                  <label htmlFor="reg-category">Category</label>
                  <select
                    id="reg-category"
                    value={formCategoryId}
                    onChange={(e) => setFormCategoryId(e.target.value)}
                  >
                    <option value="">Uncategorized (tracks expiry, 7d default)</option>
                    {categories.map((cat) => (
                      <option key={cat.id} value={cat.id}>
                        {cat.name} {cat.tracks_expiry ? `(${cat.warn_days}d window)` : "(No expiry)"}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="form-field">
                  <label htmlFor="reg-reorder">Reorder Level</label>
                  <input
                    id="reg-reorder"
                    type="number"
                    min="0"
                    value={formReorder}
                    onChange={(e) => setFormReorder(e.target.value)}
                  />
                </div>

                <div className="form-field">
                  <label htmlFor="reg-cost">Cost Price (PHP) *</label>
                  <input
                    id="reg-cost"
                    type="number"
                    step="0.01"
                    min="0"
                    required
                    value={formCost}
                    onChange={(e) => setFormCost(e.target.value)}
                    placeholder="35.00"
                  />
                </div>

                <div className="form-field">
                  <label htmlFor="reg-price">Selling Price (PHP) *</label>
                  <input
                    id="reg-price"
                    type="number"
                    step="0.01"
                    min="0"
                    required
                    value={formPrice}
                    onChange={(e) => setFormPrice(e.target.value)}
                    placeholder="50.00"
                  />
                </div>

                <div className="form-field">
                  <label htmlFor="reg-units">Initial Units (Optional)</label>
                  <input
                    id="reg-units"
                    type="number"
                    min="0"
                    value={formUnits}
                    onChange={(e) => setFormUnits(e.target.value)}
                    placeholder="e.g. 24"
                  />
                </div>

                {selectedRegCat?.tracks_expiry !== false && (
                  <div className="form-field">
                    <label htmlFor="reg-expiry">Initial Batch Expiry Date</label>
                    <input
                      id="reg-expiry"
                      type="date"
                      value={formExpiry}
                      onChange={(e) => setFormExpiry(e.target.value)}
                    />
                  </div>
                )}
              </div>

              <div className="modal-actions">
                <button type="button" className="btn-cancel" onClick={() => setIsRegisterOpen(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn-submit">
                  Save Product
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
}
