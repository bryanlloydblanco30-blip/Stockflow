import { useEffect, useState } from "react";
import AdjustCountPage from "./pages/AdjustCountPage";
import AlertsPage from "./pages/AlertsPage";
import HistoryPage from "./pages/HistoryPage";
import HomePage from "./pages/HomePage";
import ReportsPage from "./pages/ReportsPage";
import RestockPage from "./pages/RestockPage";
import SellPage from "./pages/SellPage";
import SellStatesPage from "./pages/SellStatesPage";
import SettingsPage from "./pages/SettingsPage";
import StartingPage from "./pages/StartingPage";
import StockPage from "./pages/StockPage";
import type { Page } from "./types";

const validPages: Page[] = [
  "start",
  "home",
  "sell",
  "stock",
  "restock",
  "reports",
  "states",
  "adjust",
  "history",
  "alerts",
  "settings",
];

function pageFromHash(): Page {
  const value = window.location.hash.slice(1) as Page;
  return validPages.includes(value) ? value : "start";
}

export default function App() {
  const [page, setPage] = useState<Page>(pageFromHash);

  useEffect(() => {
    const handleHashChange = () => setPage(pageFromHash());
    window.addEventListener("hashchange", handleHashChange);
    return () => window.removeEventListener("hashchange", handleHashChange);
  }, []);

  const navigate = (nextPage: Page) => {
    window.location.hash = nextPage;
    setPage(nextPage);
  };

  const pages: Record<Page, React.ReactNode> = {
    start: <StartingPage navigate={navigate} />,
    home: <HomePage navigate={navigate} />,
    sell: <SellPage navigate={navigate} />,
    stock: <StockPage navigate={navigate} />,
    restock: <RestockPage navigate={navigate} />,
    reports: <ReportsPage navigate={navigate} />,
    states: <SellStatesPage navigate={navigate} />,
    adjust: <AdjustCountPage navigate={navigate} />,
    history: <HistoryPage navigate={navigate} />,
    alerts: <AlertsPage navigate={navigate} />,
    settings: <SettingsPage navigate={navigate} />,
  };

  return pages[page];
}
