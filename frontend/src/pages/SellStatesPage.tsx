import { useState } from "react";
import Shell from "../components/Shell";
import type { Navigate } from "../types";

export default function SellStatesPage({ navigate }: { navigate: Navigate }) {
  const [quantity, setQuantity] = useState(5);
  return (
    <Shell
      active="sell"
      page="states"
      title="Sell states"
      subtitle="Checkout and inventory availability states"
      navigate={navigate}
    >
      <div className="state-grid">
        <section className="state-card panel">
          <span>⌑ &nbsp; Empty cart</span>
          <strong>Cart is empty. Scan a product to start.</strong>
          <button disabled>Checkout</button>
        </section>
        <section className="state-card stock-warning">
          <span>◇ &nbsp; Not enough stock</span>
          <p>Fresh Milk 1L × 5</p>
          <strong>Only 3 left. Lower the quantity.</strong>
          <div className="quantity">
            <button onClick={() => setQuantity(Math.max(1, quantity - 1))}>−</button>
            <span>{quantity}</span>
            <button onClick={() => setQuantity(quantity + 1)}>+</button>
          </div>
        </section>
        <section className="state-card expired">
          <span>◇ &nbsp; Only expired stock left</span>
          <strong>Only expired stock left. It cannot be sold.</strong>
          <button className="link-button" onClick={() => navigate("alerts")}>
            Go to write-off list
          </button>
        </section>
      </div>
    </Shell>
  );
}
