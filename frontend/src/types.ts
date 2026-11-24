export type Page =
  | "start"
  | "home"
  | "sell"
  | "stock"
  | "restock"
  | "reports"
  | "states"
  | "adjust"
  | "history"
  | "alerts"
  | "settings";

export type Navigate = (page: Page) => void;
