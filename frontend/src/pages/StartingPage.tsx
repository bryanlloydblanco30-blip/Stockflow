import type { Navigate, Page } from "../types";

const items: { page: Page; label: string; icon: string }[] = [
  { page: "home", label: "Home", icon: "83aea.svg" },
  { page: "sell", label: "Sell", icon: "d9751.svg" },
  { page: "stock", label: "Stock", icon: "2db41.svg" },
  { page: "restock", label: "Restock", icon: "30f94.svg" },
  { page: "reports", label: "Reports", icon: "4fd46.svg" },
];

export default function StartingPage({ navigate }: { navigate: Navigate }) {
  return (
    <main className="starting-page">
      <section className="welcome-copy">
        <div className="welcome-brand">
          <img
            src="./assets/app-logo.png"
            alt="StockFlow logo"
            style={{ borderRadius: "12px", objectFit: "cover" }}
          />
          <span>StockFlow</span>
        </div>
        <h1>
          Your store.
          <br />A little happier.
        </h1>
        <p>Everything you need for a good day of shopkeeping.</p>
        <div className="hero-illustration">
          <img src="./assets/051ce.svg" alt="A friendly illustrated corner shop" />
        </div>
        <h2>Small shop. Big possibilities.</h2>
        <p>Sell, restock, and keep your business growing — all in one place.</p>
      </section>
      <section className="start-card">
        <h2>StockFlow</h2>
        <p>Choose where you’d like to start.</p>
        <div className="start-links">
          {items.map((item, index) => (
            <button
              className={index === 0 ? "selected" : ""}
              key={item.page}
              onClick={() => navigate(item.page)}
            >
              <img src={`./assets/${item.icon}`} alt="" />
              <span>{item.label}</span>
            </button>
          ))}
        </div>
      </section>
    </main>
  );
}
