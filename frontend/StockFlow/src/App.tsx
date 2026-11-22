import { useMemo, useState } from "react";

type Page =
  | "start"
  | "home"
  | "sell"
  | "stock"
  | "restock"
  | "reports"
  | "sell-states"
  | "adjust"
  | "history";

const A = "/assets";

const navItems: { id: Page; label: string; icon: string; active: string }[] = [
  { id: "home", label: "Home", icon: "af3ce.svg", active: "229d1.svg" },
  { id: "sell", label: "Sell", icon: "0b38a.svg", active: "5a3bb.svg" },
  { id: "stock", label: "Stock", icon: "bf69b.svg", active: "5c8bf.svg" },
  { id: "restock", label: "Restock", icon: "4022f.svg", active: "90354.svg" },
  { id: "reports", label: "Reports", icon: "b5de1.svg", active: "3ba0c.svg" },
];

const products = [
  ["4800010001", "Pandesal pack", "Bread", "12", "₱32.00", "₱45.00", "Expires soon", "red"],
  ["4800010002", "Sardines 155g", "Canned", "3", "₱20.00", "₱28.00", "Low", "amber"],
  ["4800010003", "Bottled water 500ml", "Drinks", "48", "₱14.00", "₱25.00", "OK", "green"],
  ["4800010004", "Notebook", "School supplies", "20", "₱40.00", "₱58.00", "Untracked", "green"],
  ["4800010005", "Instant noodles", "Canned", "60", "₱9.00", "₱14.00", "OK", "green"],
  ["4800010006", "Loaf bread", "Bread", "9", "₱48.00", "₱65.00", "Near expiry", "amber"],
];

const pageMeta: Record<Exclude<Page, "start">, [string, string]> = {
  home: ["Home", "Your store at a glance"],
  sell: ["Sell", "Build a sale and checkout"],
  stock: ["Stock", "Manage products and availability"],
  restock: ["Restock", "Plan your next replenishment"],
  reports: ["Reports", "Understand your store performance"],
  "sell-states": ["Sell states", "Checkout and inventory availability states"],
  adjust: ["Adjust count · Fresh Milk 1L", "Update the physical count for this batch"],
  history: ["Transaction history", "Review sales and inventory movements"],
};

function Button({ children, onClick, className = "", disabled = false }: {
  children: React.ReactNode; onClick?: () => void; className?: string; disabled?: boolean;
}) {
  return <button className={`button ${className}`} onClick={onClick} disabled={disabled}>{children}</button>;
}

function Sidebar({ page, setPage }: { page: Page; setPage: (page: Page) => void }) {
  const section = page === "sell-states" ? "sell" : page === "adjust" ? "stock" : page === "history" ? "reports" : page;
  return (
    <aside className="sidebar">
      <button className="brand" onClick={() => setPage("start")}>
        <img src={`${A}/18451.svg`} alt="" />
        <span><b>StockFlow</b><small>POINT OF SALE</small></span>
      </button>
      <nav>
        {navItems.map((item) => {
          const active = section === item.id;
          return (
            <button key={item.id} className={active ? "nav-item active" : "nav-item"} onClick={() => setPage(item.id)}>
              <img src={`${A}/${active ? item.active : item.icon}`} alt="" />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>
      <img className="shop-companion" src={`${A}/45491.svg`} alt="A cheerful corner store" />
      <div className="made-card">
        <img src={`${A}/af3ce.svg`} alt="" />
        <span>Made for the<br />corner of the world.</span>
      </div>
      <button className="back-button" onClick={() => setPage("start")}>Back</button>
    </aside>
  );
}

function Header({ page, setPage }: { page: Exclude<Page, "start">; setPage: (page: Page) => void }) {
  const [open, setOpen] = useState(false);
  const [title, subtitle] = pageMeta[page];
  return (
    <header className="page-header">
      <div>
        <small>YOUR STORE, SIMPLIFIED</small>
        <h1>{title}</h1>
        <p>{subtitle}</p>
      </div>
      <div className="header-actions">
        <span className="sparkle">✦</span>
        <div className="more-wrap">
          <Button className="more" onClick={() => setOpen(!open)}>More⌄</Button>
          {open && (
            <div className="more-menu">
              <button onClick={() => setPage("sell-states")}>Sell states</button>
              <button onClick={() => setPage("adjust")}>Adjust stock</button>
              <button onClick={() => setPage("history")}>History</button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}

function StatCard({ label, value, tone = "" }: { label: string; value: string; tone?: string }) {
  return <div className={`stat-card ${tone}`}><small>{label}</small><strong>{value}</strong></div>;
}

function Badge({ children, tone = "green" }: { children: React.ReactNode; tone?: string }) {
  return <span className={`badge ${tone}`}>{children}</span>;
}

function DataTable({ headers, rows }: { headers: string[]; rows: React.ReactNode[][] }) {
  return (
    <div className="table-wrap">
      <table>
        <thead><tr>{headers.map((h) => <th key={h}>{h}</th>)}</tr></thead>
        <tbody>{rows.map((row, i) => <tr key={i}>{row.map((cell, j) => <td key={j}>{cell}</td>)}</tr>)}</tbody>
      </table>
    </div>
  );
}

function StartPage({ setPage }: { setPage: (page: Page) => void }) {
  return (
    <main className="start-page">
      <section className="start-story">
        <div className="start-brand"><img src={`${A}/ea9fe.svg`} alt="" /><span>StockFlow</span></div>
        <div className="hero-copy">
          <span className="hero-spark left">✦</span>
          <h1>Your store.<br />A little happier.</h1>
          <p>Everything you need for a good day of shopkeeping.</p>
        </div>
        <img className="hero-shop" src={`${A}/051ce.svg`} alt="A happy neighborhood corner store" />
        <div className="hero-footer">
          <h2>Small shop. Big possibilities.</h2>
          <p>Sell, restock, and keep your business growing — all in one place.</p>
        </div>
      </section>
      <section className="start-window">
        <h2>StockFlow</h2>
        <p>Choose where you’d like to start.</p>
        <div className="start-nav">
          {navItems.map((item, i) => (
            <button key={item.id} className={i === 0 ? "selected" : ""} onClick={() => setPage(item.id)}>
              <img src={`${A}/${i === 0 ? item.active : item.icon}`} alt="" />
              <span>{item.label}</span>
            </button>
          ))}
        </div>
      </section>
    </main>
  );
}

function HomePage({ setPage }: { setPage: (page: Page) => void }) {
  const attention = [
    ["Pandesal pack", "Expires in 1 day", <Badge tone="red">Red</Badge>],
    ["Canned sardines 155g", "3 units left", <Badge tone="amber">Amber</Badge>],
    ["Bottled water 500ml", "Reorder level reached", <Badge tone="amber">Amber</Badge>],
    ["Loaf bread", "Expires in 3 days", <Badge tone="amber">Amber</Badge>],
    ["Pencil HB", "6 units left", <Badge>Low</Badge>],
  ];
  return (
    <>
      <div className="title-button"><Button className="peach" onClick={() => setPage("sell")}>START SALE</Button></div>
      <div className="stats-grid four">
        <StatCard label="Today's Sales" value="₱4,860.00" tone="yellow" />
        <StatCard label="Today's Profit" value="₱1,120.00" tone="green" />
        <StatCard label="Low Stock Items" value="7" tone="peach" />
        <StatCard label="Near Expiry Batches" value="4" tone="lavender" />
      </div>
      <section className="panel">
        <h2>Needs attention</h2>
        <DataTable headers={["Product", "Issue", "Urgency"]} rows={attention} />
      </section>
      <button className="callout green-callout" onClick={() => setPage("sell")}>
        <span><b>Ready for your next customer?</b><small>Start a sale, check your shelves, and keep things moving.</small></span>
        <img src={`${A}/0b38a.svg`} alt="" />
      </button>
    </>
  );
}

function SellPage() {
  const initial = [
    { name: "Pandesal pack", qty: 1, price: 45 },
    { name: "Sardines 155g", qty: 2, price: 28 },
    { name: "Bottled water 500ml", qty: 1, price: 25 },
    { name: "Notebook", qty: 1, price: 58 },
  ];
  const [cart, setCart] = useState(initial);
  const total = cart.reduce((sum, item) => sum + item.qty * item.price, 0);
  const changeQty = (index: number, by: number) => setCart(cart.map((item, i) => i === index ? { ...item, qty: Math.max(1, item.qty + by) } : item));
  return (
    <div className="sell-layout">
      <section className="panel cart-panel">
        <div className="scan-row"><input aria-label="Barcode" placeholder="Scan or type barcode" /><Button className="blue">Scan</Button><Button className="lavender">Simulate</Button></div>
        <div className="cart-head"><span>Item</span><span>Qty</span><span>Unit price</span><span>Line total</span><span /></div>
        {cart.map((item, i) => (
          <div className="cart-row" key={item.name}>
            <span>{item.name}</span>
            <span className="stepper"><button onClick={() => changeQty(i, -1)}>−</button>{item.qty}<button onClick={() => changeQty(i, 1)}>+</button></span>
            <span>₱{item.price.toFixed(2)}</span>
            <span>₱{(item.price * item.qty).toFixed(2)}</span>
            <Button className="lavender mini" onClick={() => setCart(cart.filter((_, n) => n !== i))}>Remove</Button>
          </div>
        ))}
      </section>
      <aside className="checkout-column">
        <section className="panel summary">
          <b>Summary</b><p><span>Items</span><strong>{cart.reduce((n, i) => n + i.qty, 0)}</strong></p>
          <p><span>Subtotal</span><strong>₱{total.toFixed(2)}</strong></p><p><span>Tax 0%</span><strong>₱0.00</strong></p>
          <hr /><p className="total"><span>Total</span><strong>₱{total.toFixed(2)}</strong></p>
          <Button className="blue checkout">Checkout (Enter)</Button>
        </section>
        <section className="message-card"><h2>A smooth checkout,<br />a happy customer.</h2><p>Scan items, review, and you’re ready.</p></section>
      </aside>
    </div>
  );
}

function StockPage({ setPage }: { setPage: (page: Page) => void }) {
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState("All");
  const visible = useMemo(() => products.filter((p) => p.join(" ").toLowerCase().includes(query.toLowerCase()) && (filter === "All" || (filter === "Low" && p[6] === "Low") || (filter === "Near Expiry" && p[6].toLowerCase().includes("expir")) || (filter === "Untracked" && p[6] === "Untracked"))), [query, filter]);
  return (
    <>
      <div className="title-button"><Button className="blue">+ Register Product</Button></div>
      <input className="search" value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search products or barcode" />
      <div className="chips">{["All", "Low", "Near Expiry", "Untracked"].map((f) => <Button key={f} onClick={() => setFilter(f)} className={filter === f ? "blue chip" : "lavender chip"}>{f}</Button>)}</div>
      <button className="table-button" onClick={() => setPage("adjust")}>
        <DataTable headers={["Barcode", "Name", "Category", "Units", "Cost", "Price", "Status"]} rows={visible.map((p) => [...p.slice(0, 6), <Badge tone={p[7]}>{p[6]}</Badge>])} />
      </button>
      <div className="closing-copy"><h2>Every shelf, a little more organized.</h2><p>Find your products, check availability, and spot what needs attention.</p></div>
    </>
  );
}

function RestockPage() {
  const rows = [
    ["92", "Sardines 155g", "1.5", "2.0 / day", "24", <Badge tone="red">Urgent</Badge>],
    ["85", "Bottled water 500ml", "3", "16 / day", "60", <Badge tone="red">Urgent</Badge>],
    ["61", "Pencil HB", "6", "1.0 / day", "12", <Badge tone="amber">Soon</Badge>],
    ["48", "Instant noodles", "9", "6.5 / day", "40", <Badge tone="amber">Soon</Badge>],
  ];
  return (
    <>
      <div className="chips"><Button className="blue chip wide">Priority Queue</Button><Button className="lavender chip wide">Fast / Slow Movers</Button></div>
      <DataTable headers={["Score", "Product", "Days of cover", "14-day speed", "Suggested qty", "Urgency"]} rows={rows} />
      <div className="callout restock-callout"><img src={`${A}/4022f.svg`} alt="" /><span><b>Keep your favorites on the shelf.</b><small>Start with urgent items, then work your way down the priority queue.</small></span></div>
    </>
  );
}

function ReportsPage({ setPage }: { setPage: (page: Page) => void }) {
  const [period, setPeriod] = useState("Week");
  const bars = [44, 62, 36, 72, 56, 88, 66];
  return (
    <>
      <div className="periods">{["Day", "Week", "Month", "Custom"].map((p) => <Button key={p} className={period === p ? "blue chip" : "lavender chip"} onClick={() => setPeriod(p)}>{p}</Button>)}</div>
      <div className="stats-grid four report-stats">
        <StatCard label="Revenue" value="₱31,400.00" /><StatCard label="Gross profit" value="₱8,250.00" tone="green" />
        <StatCard label="Margin" value="26.3%" tone="yellow" /><StatCard label="COGS" value="₱23,150.00" tone="rose" />
      </div>
      <section className="panel chart-panel"><h2>Sales and profit trend</h2><div className="chart">{bars.map((h, i) => <div className="bar-slot" key={i}><div className={`bar b${i}`} style={{ height: `${h}%` }} /><span>{["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][i]}</span></div>)}</div></section>
      <div className="report-links"><Button onClick={() => setPage("history")} className="lavender">Best and worst sellers ›</Button><Button className="lavender">Profit per item ›</Button><Button className="lavender">Spoilage loss ›</Button><Button className="lavender">Inventory value ›</Button></div>
    </>
  );
}

function SellStatesPage() {
  return (
    <div className="state-grid">
      <section className="panel state-card"><p className="state-label"><img src={`${A}/0b38a.svg`} alt="" />Empty cart</p><b>Cart is empty. Scan a product to start.</b><Button disabled>Checkout</Button></section>
      <section className="panel state-card yellow"><p className="state-label"><img src={`${A}/bf69b.svg`} alt="" />Not enough stock</p><span>Fresh Milk 1L × 5</span><b className="danger">Only 3 left. Lower the quantity.</b><div className="stepper"><button>−</button>5<button>+</button></div></section>
      <section className="panel state-card rose"><p className="state-label"><img src={`${A}/bf69b.svg`} alt="" />Only expired stock left</p><b className="danger">Only expired stock left. It cannot be sold.</b><a href="#write-off">Go to write-off list</a></section>
    </div>
  );
}

function AdjustPage({ setPage }: { setPage: (page: Page) => void }) {
  const [count, setCount] = useState("6");
  const [saved, setSaved] = useState(false);
  return (
    <>
      <div className="title-button"><Button className="lavender" onClick={() => setPage("stock")}>Cancel</Button></div>
      <div className="adjust-layout">
        <form className="panel form-card" onSubmit={(e) => { e.preventDefault(); setSaved(true); }}>
          <label>Batch<select><option>Batch A · exp 12 Nov 2026</option></select></label>
          <label>Current count<input value="8" readOnly /></label>
          <label>New count (after physical check)<input value={count} onChange={(e) => setCount(e.target.value)} /></label>
          <label>Reason<input defaultValue="Counted 6 on shelf" /></label>
          <Button className="blue">{saved ? "Adjustment saved" : "Save adjustment"}</Button>
          <small>Saved with old count, new count and reason. History is never edited.</small>
        </form>
        <aside className="message-card fresh-card"><img src={`${A}/bf69b.svg`} alt="" /><h2>A fresh count.</h2><p>Count what’s on your shelf,<br />then leave a reason to keep<br />your stock history clear.</p></aside>
      </div>
    </>
  );
}

function HistoryPage() {
  const [filter, setFilter] = useState("All");
  const all = [
    ["7 Nov 10:42", "Sale", "3 items", "PHP 184.00", "green"],
    ["7 Nov 09:15", "Receive", "Fresh Milk 1L × 24", "PHP 1,152.00", "amber"],
    ["6 Nov 17:30", "Write-off", "Yogurt cup × 2", "PHP 70.00", "red"],
    ["6 Nov 12:05", "Sale", "2 items", "PHP 90.00", "green"],
  ];
  const rows = all.filter((r) => filter === "All" || r[1] === filter).map((r, i) => [r[0], <Badge tone={r[4]}>{r[1]}</Badge>, r[2], r[3], i === 0 && filter === "All" ? <Button className="lavender mini">Void last sale</Button> : ""]);
  return (
    <>
      <div className="chips history-filters">{["All", "Sale", "Receive", "Void", "Adjustment", "Write-off"].map((f) => <Button key={f} className={filter === f ? "blue chip" : "lavender chip"} onClick={() => setFilter(f)}>{f}</Button>)}</div>
      <DataTable headers={["Date", "Type", "Details", "Amount", ""]} rows={rows} />
      <p className="hint">Undo is available only on the latest transaction.</p>
    </>
  );
}

function AppPage({ page, setPage }: { page: Exclude<Page, "start">; setPage: (page: Page) => void }) {
  return (
    <div className="app-shell">
      <Sidebar page={page} setPage={setPage} />
      <main className="workspace">
        <Header page={page} setPage={setPage} />
        <div className="page-content">
          {page === "home" && <HomePage setPage={setPage} />}
          {page === "sell" && <SellPage />}
          {page === "stock" && <StockPage setPage={setPage} />}
          {page === "restock" && <RestockPage />}
          {page === "reports" && <ReportsPage setPage={setPage} />}
          {page === "sell-states" && <SellStatesPage />}
          {page === "adjust" && <AdjustPage setPage={setPage} />}
          {page === "history" && <HistoryPage />}
        </div>
      </main>
    </div>
  );
}

export default function App() {
  const [page, setPage] = useState<Page>("start");
  return page === "start" ? <StartPage setPage={setPage} /> : <AppPage page={page} setPage={setPage} />;
}
