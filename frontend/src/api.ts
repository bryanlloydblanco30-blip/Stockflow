/**
 * frontend/src/api.ts
 * Typed client for the local Python StockFlow backend API (/api/*).
 * Formatting helpers follow AGENTS.md rules:
 * - Money: PHP 1,250.00
 * - Dates: 12 Nov 2026
 */

export function formatPHP(amount: number): string {
  const num = Number.isFinite(amount) ? amount : 0;
  return `PHP ${num.toLocaleString("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

export function formatDate(iso: string | null | undefined): string {
  if (!iso) return "—";
  const datePart = iso.slice(0, 10);
  const parts = datePart.split("-");
  if (parts.length !== 3) return iso;
  const d = new Date(Number(parts[0]), Number(parts[1]) - 1, Number(parts[2]));
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleDateString("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

interface PyWebViewBridge {
  request: (
    method: string,
    url: string,
    bodyJson?: string,
  ) => Promise<{ status: number; data: unknown }>;
}

declare global {
  interface Window {
    pywebview?: {
      api?: PyWebViewBridge;
    };
  }
}

async function getPyWebViewApi(): Promise<PyWebViewBridge | null> {
  if (window.pywebview?.api) {
    return window.pywebview.api;
  }
  if (window.location.protocol !== "file:") {
    return null;
  }
  return new Promise((resolve) => {
    const onReady = () => {
      window.removeEventListener("pywebviewready", onReady);
      resolve(window.pywebview?.api ?? null);
    };
    window.addEventListener("pywebviewready", onReady);
    setTimeout(() => {
      window.removeEventListener("pywebviewready", onReady);
      resolve(window.pywebview?.api ?? null);
    }, 3000);
  });
}

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const bridge = await getPyWebViewApi();
  if (bridge) {
    const method = (options?.method || "GET").toUpperCase();
    const bodyJson = typeof options?.body === "string" ? options.body : "";
    const res = await bridge.request(method, url, bodyJson);
    if (res.status >= 400) {
      const errObj = (res.data ?? {}) as { error?: string };
      throw new Error(errObj.error || `Request failed (${res.status})`);
    }
    return res.data as T;
  }

  const res = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data.error || `Request failed (${res.status})`);
  }
  return data as T;
}

// --- Types ---

export interface CategoryDTO {
  id: number;
  name: string;
  tracks_expiry: boolean;
  warn_days: number;
  red_days: number;
}

export interface BatchDTO {
  id: number;
  product_id: number;
  quantity: number;
  cost_price: number;
  received_date: string;
  expiry_date: string | null;
  moved_to_front: boolean;
  level: string;
  is_sellable: boolean;
}

export interface ProductDTO {
  id: number;
  barcode: string;
  name: string;
  category_id: number | null;
  category_name: string;
  tracks_expiry: boolean;
  warn_days: number;
  cost_price: number;
  selling_price: number;
  reorder_level: number;
  sellable_stock: number;
  expired_stock: number;
  is_low_stock: boolean;
  earliest_expiry: string | null;
  alert_level: string;
  status_label: string;
  batches: BatchDTO[];
}

export interface DashboardDTO {
  kpis: {
    today_sales: number;
    today_profit: number;
    low_stock_count: number;
    near_expiry_count: number;
  };
  attention: {
    product_id: number;
    product_name: string;
    issue: string;
    urgency: string;
    color: string;
  }[];
  today: string;
}

export interface CartLineDTO {
  product_id: number;
  barcode: string;
  product_name: string;
  unit_price: number;
  quantity: number;
  subtotal: number;
  sellable_stock: number;
}

export interface CartDTO {
  lines: CartLineDTO[];
  item_count: number;
  total: number;
}

export interface ReceiptDTO {
  transaction_id: number;
  date_time: string;
  total: number;
  cash_given: number;
  change: number;
  lines: {
    product_id: number;
    product_name: string;
    quantity: number;
    unit_price: number;
    subtotal: number;
  }[];
  low_stock_alerts: {
    product_id: number;
    product_name: string;
    remaining_stock: number;
    reorder_level: number;
  }[];
}

export interface AlertRowDTO {
  batch_id: number;
  product_id: number;
  product_name: string;
  barcode: string;
  category_name: string;
  quantity: number;
  cost_price: number;
  loss_value: number;
  received_date: string;
  expiry_date: string;
  days_left: number;
  level: string;
  moved_to_front: boolean;
}

export interface AlertsDTO {
  near_expiry: AlertRowDTO[];
  expired: AlertRowDTO[];
  checklist: AlertRowDTO[];
  unresolved_expiry: {
    batch_id: number;
    product_id: number;
    product_name: string;
    quantity: number;
    status: string;
  }[];
}

export interface RestockItemDTO {
  rank: number;
  product_id: number;
  product_name: string;
  barcode: string;
  category_name: string;
  sellable_stock: number;
  selling_speed: number;
  days_of_cover: number | null;
  suggested_reorder: number;
  reason: string;
  cost_price: number;
  reorder_level: number;
  tracks_expiry: boolean;
  urgency: "Urgent" | "Soon" | "OK";
  color: "red" | "amber" | "green";
}

export interface RestockDTO {
  target_cover_days: number;
  queue: RestockItemDTO[];
  top_sellers: { product_id: number; product_name: string; score: number }[];
  bottom_sellers: { product_id: number; product_name: string; score: number }[];
}

export interface ReportsDTO {
  period: string;
  start_date: string;
  end_date: string;
  summary: {
    revenue: number;
    cogs: number;
    gross_profit: number;
    margin_pct: number;
    spoilage: number;
    inventory_value: number;
  };
  daily_series: {
    date: string;
    label: string;
    revenue: number;
    cogs: number;
    profit: number;
    units: number;
  }[];
  top_sellers: { product_id: number; product_name: string; score: number }[];
  bottom_sellers: { product_id: number; product_name: string; score: number }[];
  profit_per_item: {
    product_id: number;
    product_name: string;
    cost_price: number;
    selling_price: number;
    units_sold: number;
    revenue: number;
    total_profit: number;
    margin_pct: number;
  }[];
  spoilage_items: {
    batch_id: number;
    product_name: string;
    category_name: string;
    quantity: number;
    unit_cost: number;
    total_loss: number;
    date_time: string;
  }[];
  inventory_valuation: {
    total_cost_value: number;
    total_retail_value: number;
    potential_profit: number;
    by_category: {
      category: string;
      units: number;
      cost_value: number;
      retail_value: number;
      margin_pct: number;
    }[];
  };
}

export interface TransactionRowDTO {
  id: number;
  type: string;
  date_time: string;
  total: number;
  cash_given: number;
  change: number;
  reverses_id: number | null;
  details: string;
  can_undo: boolean;
}

export interface SettingsDTO {
  store_name: string;
  default_warn_days: number;
  target_cover_days: number;
  db_path: string;
}

export interface BackupFileDTO {
  filename: string;
  path: string;
  size_bytes: number;
  modified_at?: string;
  created_at?: string;
}

// --- API Calls ---

export const api = {
  getDashboard: () => request<DashboardDTO>("/api/dashboard"),
  getCategories: () => request<CategoryDTO[]>("/api/categories"),
  createCategory: (body: { name: string; tracks_expiry: boolean; warn_days: number }) =>
    request<CategoryDTO>("/api/categories", { method: "POST", body: JSON.stringify(body) }),
  updateCategory: (id: number, body: { name?: string; tracks_expiry?: boolean; warn_days?: number }) =>
    request<CategoryDTO>(`/api/categories/${id}`, { method: "PUT", body: JSON.stringify(body) }),
  deleteCategory: (id: number) =>
    request<{ deleted_id: number; affected_products: number }>(`/api/categories/${id}`, { method: "DELETE" }),

  getProducts: () => request<ProductDTO[]>("/api/products"),
  searchProducts: (q: string) => request<ProductDTO[]>(`/api/products/search?q=${encodeURIComponent(q)}`),
  createProduct: (body: {
    barcode: string;
    name: string;
    category_id: number | null;
    cost_price: number;
    selling_price: number;
    reorder_level: number;
    initial_stock?: number;
    expiry_date?: string | null;
  }) => request<ProductDTO>("/api/products", { method: "POST", body: JSON.stringify(body) }),

  scanBarcode: (barcode: string) =>
    request<{ status: "FOUND" | "UNKNOWN"; product?: ProductDTO; barcode?: string }>(
      `/api/pos/scan?barcode=${encodeURIComponent(barcode)}`
    ),
  getCart: () => request<CartDTO>("/api/pos/cart"),
  addToCart: (body: { barcode?: string; product_id?: number; quantity?: number }) =>
    request<{ status: "OK" | "UNKNOWN"; product?: ProductDTO; barcode?: string; cart: CartDTO }>(
      "/api/pos/cart",
      { method: "POST", body: JSON.stringify(body) }
    ),
  updateCartItem: (productId: number, quantity: number) =>
    request<CartDTO>(`/api/pos/cart/${productId}`, {
      method: "PUT",
      body: JSON.stringify({ quantity }),
    }),
  removeCartItem: (productId: number) =>
    request<CartDTO>(`/api/pos/cart/${productId}`, { method: "DELETE" }),
  clearCart: () => request<CartDTO>("/api/pos/cart", { method: "DELETE" }),
  checkout: (cash_given: number) =>
    request<ReceiptDTO>("/api/pos/checkout", {
      method: "POST",
      body: JSON.stringify({ cash_given }),
    }),

  receiveStock: (body: {
    product_id: number;
    quantity: number;
    cost_price?: number;
    expiry_date?: string | null;
  }) =>
    request<{
      batch: { id: number; product_id: number; quantity: number; received_date: string; expiry_date: string | null };
      older_batches_warning: { batch_id: number; expiry_date: string; units: number; level: string }[];
    }>("/api/inventory/receive", { method: "POST", body: JSON.stringify(body) }),

  adjustStock: (body: { batch_id: number; new_quantity: number; reason: string }) =>
    request<{ batch_id: number; old_quantity: number; new_quantity: number; difference: number; reason: string }>(
      "/api/inventory/adjust",
      { method: "POST", body: JSON.stringify(body) }
    ),

  writeOffExpired: (body: { batch_id: number; reason?: string }) =>
    request<{ batch_id: number; units_lost: number; loss_amount: number }>(
      "/api/inventory/writeoff",
      { method: "POST", body: JSON.stringify(body) }
    ),

  markShelfRotated: (batch_id: number) =>
    request<{ batch_id: number; moved_to_front: boolean }>("/api/inventory/rotate", {
      method: "POST",
      body: JSON.stringify({ batch_id }),
    }),

  getAlerts: () => request<AlertsDTO>("/api/alerts"),
  getRestock: () => request<RestockDTO>("/api/restock"),
  getReports: (period: string, start?: string, end?: string) => {
    const params = new URLSearchParams({ period });
    if (start) params.set("start", start);
    if (end) params.set("end", end);
    return request<ReportsDTO>(`/api/reports?${params.toString()}`);
  },
  getTransactions: (type?: string) =>
    request<{ transactions: TransactionRowDTO[]; can_undo_id: number | null }>(
      `/api/transactions${type && type !== "All" ? `?type=${encodeURIComponent(type)}` : ""}`
    ),
  undoLast: () =>
    request<{ void_transaction_id: number; reverses_id: number; total: number }>("/api/undo", {
      method: "POST",
      body: JSON.stringify({}),
    }),

  getSettings: () => request<SettingsDTO>("/api/settings"),
  updateSettings: (body: Partial<SettingsDTO>) =>
    request<SettingsDTO>("/api/settings", { method: "PUT", body: JSON.stringify(body) }),

  exportBackup: () => request<BackupFileDTO>("/api/backup/export", { method: "POST", body: JSON.stringify({}) }),
  listBackups: () => request<{ backups: BackupFileDTO[] }>("/api/backup/list"),
  restoreBackup: (filename: string) =>
    request<{ restored: string; products_loaded: number }>("/api/backup/restore", {
      method: "POST",
      body: JSON.stringify({ filename }),
    }),
};
