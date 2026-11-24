# StockFlow Benchmark Results (B1–B6)

## Environment
- **Python**: `3.13.4`
- **Platform**: `Windows-11-10.0.26200-SP0`
- **Processor**: `AMD64 Family 23 Model 104 Stepping 1, AuthenticAMD`
- **Protocol**: `time.perf_counter()`, warmup runs, 30 measured repetitions (min / median / max).

## B1: Product Barcode Lookup (microseconds for 10 lookups)
| Size | Naive Linear (us) | BST Avg (us) | BST Worst Sorted-Insert (us) |
| :--- | :--- | :--- | :--- |
| 100 | 14.90 (min 14.80 / max 24.70) | 5.60 (min 5.50 / max 5.90) | 36.60 (min 36.40 / max 40.40) |
| 1000 | 130.80 (min 130.60 / max 160.50) | 8.10 (min 7.90 / max 9.70) | 427.60 (min 418.20 / max 459.10) |
| 10000 | 1,496.65 (min 1,471.00 / max 1,749.90) | 10.30 (min 10.10 / max 12.20) | 3,715.00 (min 3,582.30 / max 4,817.80) |

## B2: Product Name Prefix Search (microseconds for 10 prefixes, limit 8)
| Size | Naive String Scan (us) | Trie (us) |
| :--- | :--- | :--- |
| 100 | 69.00 (min 67.30 / max 79.90) | 57.00 (min 55.80 / max 144.40) |
| 1000 | 222.85 (min 217.50 / max 228.10) | 57.50 (min 56.50 / max 149.80) |
| 10000 | 1,535.10 (min 1,493.30 / max 1,564.60) | 51.55 (min 50.30 / max 59.90) |
| 100000 | 13,961.15 (min 13,806.50 / max 17,539.50) | 52.05 (min 50.60 / max 76.80) |

## B3: Spoiled Units Simulation (Tracked Products Only)
| Period | FEFO Min-Heap (units) | FIFO Baseline (units) | Random Baseline (units) |
| :--- | :--- | :--- | :--- |
| 30d | 20.00 (min 6.00 / max 58.00) | 53.00 (min 28.00 / max 93.00) | 109.50 (min 55.00 / max 148.00) |
| 60d | 49.00 (min 11.00 / max 93.00) | 94.50 (min 68.00 / max 164.00) | 180.00 (min 119.00 / max 242.00) |
| 90d | 81.00 (min 16.00 / max 126.00) | 139.50 (min 73.00 / max 198.00) | 240.50 (min 168.00 / max 381.00) |

## B4: Stockout Product-Days Simulation
| Period | Max-Heap Priority Queue (days) | No Alerts Baseline (days) |
| :--- | :--- | :--- |
| 30d | 183.50 (min 125.00 / max 207.00) | 330.50 (min 247.00 / max 386.00) |
| 60d | 446.50 (min 386.00 / max 475.00) | 719.00 (min 546.00 / max 842.00) |
| 90d | 710.50 (min 646.00 / max 736.00) | 1,113.00 (min 868.00 / max 1,301.00) |

## B5: Date-Range Sales Queries (microseconds for 20 range queries)
| Records | Naive Raw Loop (us) | Prefix Sums O(1) (us) |
| :--- | :--- | :--- |
| 1000 | 374.30 (min 361.90 / max 389.00) | 3.80 (min 3.70 / max 4.40) |
| 10000 | 3,531.75 (min 3,388.40 / max 3,664.40) | 3.80 (min 3.70 / max 3.90) |
| 100000 | 33,738.95 (min 33,037.90 / max 37,737.10) | 3.60 (min 3.60 / max 4.30) |
| 1000000 | 412,923.15 (min 400,855.10 / max 537,728.40) | 3.60 (min 3.60 / max 3.80) |

## B6: Top-k Sellers (microseconds)
| k | Size | Full `sorted()` (us) | Size-k Heap (us) |
| :--- | :--- | :--- | :--- |
| k=5 | 100 | 8.50 (min 8.30 / max 9.00) | 54.85 (min 52.90 / max 106.00) |
| k=5 | 1000 | 125.50 (min 124.90 / max 149.30) | 218.95 (min 217.50 / max 223.30) |
| k=5 | 10000 | 1,598.35 (min 1,567.40 / max 2,189.50) | 1,869.00 (min 1,830.40 / max 2,266.50) |
| k=5 | 100000 | 28,397.35 (min 26,454.80 / max 47,338.50) | 21,109.40 (min 20,274.40 / max 24,440.80) |
| k=10 | 100 | 8.50 (min 8.40 / max 10.20) | 83.60 (min 83.20 / max 87.90) |
| k=10 | 1000 | 124.40 (min 124.00 / max 127.90) | 252.25 (min 248.90 / max 278.70) |
| k=10 | 10000 | 1,566.85 (min 1,544.60 / max 2,255.30) | 1,963.95 (min 1,924.60 / max 2,637.50) |
| k=10 | 100000 | 25,851.60 (min 23,944.90 / max 37,860.00) | 18,882.50 (min 18,358.30 / max 19,938.70) |
