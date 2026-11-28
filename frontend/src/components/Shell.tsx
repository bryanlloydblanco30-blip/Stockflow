import type { Navigate, Page } from "../types";

const assets = "./assets";

const navItems: { page: Page; label: string; icon: string; activeIcon: string }[] = [
  { page: "home", label: "Home", icon: "af3ce.svg", activeIcon: "229d1.svg" },
  { page: "sell", label: "Sell", icon: "0b38a.svg", activeIcon: "5a3bb.svg" },
  { page: "stock", label: "Stock", icon: "bf69b.svg", activeIcon: "5c8bf.svg" },
  { page: "restock", label: "Restock", icon: "4022f.svg", activeIcon: "90354.svg" },
  { page: "reports", label: "Reports", icon: "b5de1.svg", activeIcon: "3ba0c.svg" },
];

const companions: Partial<Record<Page, string>> = {
  home: "c5271.svg",
  sell: "5e2ad.svg",
  stock: "1dcf1.svg",
  restock: "45491.svg",
  reports: "45491.svg",
  states: "d7654.svg",
  adjust: "950f7.svg",
  history: "343ff.svg",
};

type ShellProps = {
  active: "home" | "sell" | "stock" | "restock" | "reports";
  page: Page;
  title: string;
  subtitle: string;
  navigate: Navigate;
  action?: React.ReactNode;
  children: React.ReactNode;
};

export default function Shell({
  active,
  page,
  title,
  subtitle,
  navigate,
  action,
  children,
}: ShellProps) {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <button className="brand" onClick={() => navigate("home")} aria-label="Go home">
          <img
            src={`${assets}/app-logo.png`}
            alt="StockFlow logo"
            style={{ borderRadius: "10px", objectFit: "cover" }}
          />
          <span>
            <strong>StockFlow</strong>
            <small>POINT OF SALE</small>
          </span>
        </button>

        <nav className="side-nav" aria-label="Primary navigation">
          {navItems.map((item) => (
            <button
              key={item.page}
              className={item.page === active ? "active" : ""}
              onClick={() => navigate(item.page)}
            >
              <img src={`${assets}/${item.page === active ? item.activeIcon : item.icon}`} alt="" />
              <span>{item.label}</span>
            </button>
          ))}
        </nav>

        <img
          className="sidebar-shop"
          src={`${assets}/${companions[page] ?? "45491.svg"}`}
          alt="A cheerful illustrated corner shop"
        />
        <div className="sidebar-note">
          <img src={`${assets}/f0424.svg`} alt="" />
          <span>
            Made for your
            <br />
            corner of the world.
          </span>
        </div>
        <button className="back-button" onClick={() => navigate("start")}>
          Back
        </button>
      </aside>

      <main className="main-content">
        <header className="page-header">
          <div>
            <span className="eyebrow">YOUR STORE, SIMPLIFIED</span>
            <h1>{title}</h1>
            <p>{subtitle}</p>
          </div>
          <div className="header-actions">
            <span className="sparkles" aria-hidden="true">
              ✦ <small>✦</small>
            </span>
            <details className="more-menu">
              <summary>More⌄</summary>
              <div>
                <button onClick={() => navigate("alerts")}>Near-expiry & Write-offs</button>
                <button onClick={() => navigate("adjust")}>Adjust count</button>
                <button onClick={() => navigate("history")}>Transaction history</button>
                <button onClick={() => navigate("settings")}>Settings & Backup</button>
                <button onClick={() => navigate("states")}>Sell states</button>
              </div>
            </details>
            {action}
          </div>
        </header>
        {children}
      </main>
    </div>
  );
}
