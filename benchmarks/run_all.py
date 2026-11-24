"""
benchmarks/run_all.py
Executes Benchmarks B1 through B6, records machine and Python metadata,
and saves:
- benchmarks/results/results.json
- benchmarks/results/RESULTS.md (tables + honest observations)
- benchmarks/results/b1_chart.svg .. b6_chart.svg (one SVG chart per benchmark, zero Matplotlib)
"""

import json
import os
import platform
import sys
from pathlib import Path
from typing import Dict, List, Tuple

from benchmarks.b1_product_lookup import run_b1
from benchmarks.b2_name_search import run_b2
from benchmarks.b3_spoiled_items import run_b3
from benchmarks.b4_stockouts import run_b4
from benchmarks.b5_range_sales import run_b5
from benchmarks.b6_topk_sellers import run_b6

RESULTS_DIR = Path(__file__).resolve().parent / "results"


def _render_grouped_bar_svg(
    title: str,
    subtitle: str,
    y_label: str,
    categories: List[str],
    series: List[Tuple[str, str, List[float]]],
    out_path: Path,
) -> None:
    """
    Generate a clean grouped bar chart SVG using pure Python (no Matplotlib).
    series: list of (label, hex_color, values)
    """
    width = 760
    height = 400
    pad_left = 80
    pad_right = 30
    pad_top = 75
    pad_bottom = 65
    plot_w = width - pad_left - pad_right
    plot_h = height - pad_top - pad_bottom

    all_vals = [v for _, _, vals in series for v in vals]
    max_val = max(all_vals) if all_vals and max(all_vals) > 0 else 1.0

    n_cats = len(categories)
    n_series = len(series)
    group_w = plot_w / max(n_cats, 1)
    bar_w = min(36.0, (group_w * 0.72) / max(n_series, 1))
    group_inner_w = bar_w * n_series + (n_series - 1) * 4

    lines: List[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#FFF9EF" rx="16"/>',
        f'<text x="{pad_left}" y="30" font-family="Segoe UI, Inter, sans-serif" font-size="18" font-weight="700" fill="#202334">{title}</text>',
        f'<text x="{pad_left}" y="50" font-family="Segoe UI, Inter, sans-serif" font-size="12" fill="#69756B">{subtitle}</text>',
    ]

    # Grid lines & Y-axis ticks (5 ticks)
    for t in range(5):
        frac = t / 4.0
        y = pad_top + plot_h * (1.0 - frac)
        val = max_val * frac
        val_str = f"{val:,.1f}" if max_val < 100 else f"{val:,.0f}"
        lines.append(
            f'<line x1="{pad_left}" y1="{y:.1f}" x2="{width - pad_right}" y2="{y:.1f}" stroke="#E0DEC4" stroke-width="1"/>'
        )
        lines.append(
            f'<text x="{pad_left - 8}" y="{y + 4:.1f}" text-anchor="end" font-family="Segoe UI, Inter, sans-serif" font-size="11" fill="#69756B">{val_str}</text>'
        )

    # Y-axis label
    lines.append(
        f'<text x="18" y="{pad_top + plot_h / 2:.1f}" transform="rotate(-90 18 {pad_top + plot_h / 2:.1f})" text-anchor="middle" font-family="Segoe UI, Inter, sans-serif" font-size="11" fill="#69756B">{y_label}</text>'
    )

    # Bars
    for c_idx, cat in enumerate(categories):
        gx = pad_left + c_idx * group_w + (group_w - group_inner_w) / 2.0
        for s_idx, (_, color, vals) in enumerate(series):
            val = vals[c_idx]
            bh = (val / max_val) * plot_h if max_val > 0 else 0.0
            bx = gx + s_idx * (bar_w + 4)
            by = pad_top + plot_h - bh
            lines.append(
                f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bar_w:.1f}" height="{bh:.1f}" fill="{color}" rx="4"/>'
            )
            lbl = f"{val:,.1f}" if val < 100 else f"{val:,.0f}"
            lines.append(
                f'<text x="{bx + bar_w / 2:.1f}" y="{max(pad_top + 10, by - 5):.1f}" text-anchor="middle" font-family="Segoe UI, Inter, sans-serif" font-size="10" fill="#202334">{lbl}</text>'
            )
        cx = pad_left + (c_idx + 0.5) * group_w
        lines.append(
            f'<text x="{cx:.1f}" y="{pad_top + plot_h + 20}" text-anchor="middle" font-family="Segoe UI, Inter, sans-serif" font-size="12" font-weight="600" fill="#202334">{cat}</text>'
        )

    # Legend
    lx = pad_left
    ly = height - 22
    for label, color, _ in series:
        lines.append(f'<rect x="{lx}" y="{ly - 10}" width="12" height="12" fill="{color}" rx="3"/>')
        lines.append(
            f'<text x="{lx + 18}" y="{ly}" font-family="Segoe UI, Inter, sans-serif" font-size="12" fill="#202334">{label}</text>'
        )
        lx += 24 + len(label) * 7.2 + 16

    lines.append("</svg>")
    out_path.write_text("\n".join(lines), encoding="utf-8")


def _fmt_metric(m: Dict[str, float], unit_key_prefix: str) -> str:
    mn = m[f"min_{unit_key_prefix}"]
    md = m[f"median_{unit_key_prefix}"]
    mx = m[f"max_{unit_key_prefix}"]
    return f"{md:,.2f} (min {mn:,.2f} / max {mx:,.2f})"


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    meta = {
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
        "processor": platform.processor() or os.environ.get("PROCESSOR_IDENTIFIER", "unknown"),
        "machine": platform.machine(),
    }

    print("Running B1 (Product Lookup: BST vs Linear)...")
    b1 = run_b1()
    print("Running B2 (Name Search: Trie vs Linear Scan)...")
    b2 = run_b2()
    print("Running B3 (Spoiled Items: FEFO Min-Heap vs FIFO vs Random)...")
    b3 = run_b3()
    print("Running B4 (Stockouts: Priority Max-Heap vs No Alerts)...")
    b4 = run_b4()
    print("Running B5 (Date-Range Sales: Prefix Sums vs Raw Loop)...")
    b5 = run_b5()
    print("Running B6 (Top-k Sellers: Size-k Heap vs Full Sort)...")
    b6 = run_b6()

    all_results = {"meta": meta, "B1": b1, "B2": b2, "B3": b3, "B4": b4, "B5": b5, "B6": b6}
    (RESULTS_DIR / "results.json").write_text(json.dumps(all_results, indent=2), encoding="utf-8")

    # Charts
    b1_cats = list(b1.keys())
    _render_grouped_bar_svg(
        "B1: Barcode Lookup (Median us, 10 queries)",
        "BST Average vs BST Worst Case (sorted insert) vs Naive Linear Search",
        "Microseconds (us)",
        [f"n={c}" for c in b1_cats],
        [
            ("Naive Linear", "#E07A5F", [b1[c]["naive_linear"]["median_us"] for c in b1_cats]),
            ("BST Worst (Sorted)", "#F2CC8F", [b1[c]["bst_worst"]["median_us"] for c in b1_cats]),
            ("BST Avg", "#245C45", [b1[c]["bst_avg"]["median_us"] for c in b1_cats]),
        ],
        RESULTS_DIR / "b1_chart.svg",
    )

    b2_cats = list(b2.keys())
    _render_grouped_bar_svg(
        "B2: Name Prefix Search (Median us, 10 prefixes)",
        "Trie Prefix Autocomplete (limit 8) vs Naive String Scan",
        "Microseconds (us)",
        [f"n={c}" for c in b2_cats],
        [
            ("Naive Scan", "#E07A5F", [b2[c]["naive_scan"]["median_us"] for c in b2_cats]),
            ("Trie", "#245C45", [b2[c]["trie"]["median_us"] for c in b2_cats]),
        ],
        RESULTS_DIR / "b2_chart.svg",
    )

    b3_cats = list(b3.keys())
    _render_grouped_bar_svg(
        "B3: Spoiled Units Over Simulated Periods",
        "FEFO Min-Heap vs FIFO Baseline vs Random Order (tracked products only)",
        "Median Spoiled Units",
        b3_cats,
        [
            ("Random", "#E07A5F", [b3[c]["random_baseline"]["median_units"] for c in b3_cats]),
            ("FIFO", "#F2CC8F", [b3[c]["fifo_baseline"]["median_units"] for c in b3_cats]),
            ("FEFO Min-Heap", "#245C45", [b3[c]["fefo_min_heap"]["median_units"] for c in b3_cats]),
        ],
        RESULTS_DIR / "b3_chart.svg",
    )

    b4_cats = list(b4.keys())
    _render_grouped_bar_svg(
        "B4: Out-of-Stock Product-Days Over Simulated Periods",
        "Restock Priority Queue (Max-Heap) vs No Alerts Baseline",
        "Median Stockout Days",
        b4_cats,
        [
            ("No Alerts", "#E07A5F", [b4[c]["no_alerts"]["median_stockout_days"] for c in b4_cats]),
            ("Max-Heap PQ", "#245C45", [b4[c]["priority_queue"]["median_stockout_days"] for c in b4_cats]),
        ],
        RESULTS_DIR / "b4_chart.svg",
    )

    b5_cats = list(b5.keys())
    _render_grouped_bar_svg(
        "B5: Date-Range Sales Query (Median us, 20 queries)",
        "O(1) Prefix Sums vs O(n) Raw Record Loop",
        "Microseconds (us)",
        [f"n={c}" for c in b5_cats],
        [
            ("Naive Loop", "#E07A5F", [b5[c]["naive_loop"]["median_us"] for c in b5_cats]),
            ("Prefix Sums", "#245C45", [b5[c]["prefix_sums"]["median_us"] for c in b5_cats]),
        ],
        RESULTS_DIR / "b5_chart.svg",
    )

    b6_k5 = b6["k=5"]
    b6_cats = list(b6_k5.keys())
    _render_grouped_bar_svg(
        "B6: Top-k Sellers (k=5, Median us)",
        "Custom Size-k Heap vs Python C-level sorted()",
        "Microseconds (us)",
        [f"n={c}" for c in b6_cats],
        [
            ("Full sorted() (C)", "#E07A5F", [b6_k5[c]["full_sort"]["median_us"] for c in b6_cats]),
            ("Size-k Heap (Py)", "#245C45", [b6_k5[c]["size_k_heap"]["median_us"] for c in b6_cats]),
        ],
        RESULTS_DIR / "b6_chart.svg",
    )

    # Markdown report
    md = [
        "# StockFlow Benchmark Results (B1–B6)",
        "",
        "## Environment",
        f"- **Python**: `{meta['python_version']}`",
        f"- **Platform**: `{meta['platform']}`",
        f"- **Processor**: `{meta['processor']}`",
        "- **Protocol**: `time.perf_counter()`, warmup runs, 30 measured repetitions (min / median / max).",
        "",
        "## B1: Product Barcode Lookup (microseconds for 10 lookups)",
        "| Size | Naive Linear (us) | BST Avg (us) | BST Worst Sorted-Insert (us) |",
        "| :--- | :--- | :--- | :--- |",
    ]
    for c in b1_cats:
        md.append(
            f"| {c} | {_fmt_metric(b1[c]['naive_linear'], 'us')} | {_fmt_metric(b1[c]['bst_avg'], 'us')} | {_fmt_metric(b1[c]['bst_worst'], 'us')} |"
        )

    md += [
        "",
        "## B2: Product Name Prefix Search (microseconds for 10 prefixes, limit 8)",
        "| Size | Naive String Scan (us) | Trie (us) |",
        "| :--- | :--- | :--- |",
    ]
    for c in b2_cats:
        md.append(
            f"| {c} | {_fmt_metric(b2[c]['naive_scan'], 'us')} | {_fmt_metric(b2[c]['trie'], 'us')} |"
        )

    md += [
        "",
        "## B3: Spoiled Units Simulation (Tracked Products Only)",
        "| Period | FEFO Min-Heap (units) | FIFO Baseline (units) | Random Baseline (units) |",
        "| :--- | :--- | :--- | :--- |",
    ]
    for c in b3_cats:
        md.append(
            f"| {c} | {_fmt_metric(b3[c]['fefo_min_heap'], 'units')} | {_fmt_metric(b3[c]['fifo_baseline'], 'units')} | {_fmt_metric(b3[c]['random_baseline'], 'units')} |"
        )

    md += [
        "",
        "## B4: Stockout Product-Days Simulation",
        "| Period | Max-Heap Priority Queue (days) | No Alerts Baseline (days) |",
        "| :--- | :--- | :--- |",
    ]
    for c in b4_cats:
        md.append(
            f"| {c} | {_fmt_metric(b4[c]['priority_queue'], 'stockout_days')} | {_fmt_metric(b4[c]['no_alerts'], 'stockout_days')} |"
        )

    md += [
        "",
        "## B5: Date-Range Sales Queries (microseconds for 20 range queries)",
        "| Records | Naive Raw Loop (us) | Prefix Sums O(1) (us) |",
        "| :--- | :--- | :--- |",
    ]
    for c in b5_cats:
        md.append(
            f"| {c} | {_fmt_metric(b5[c]['naive_loop'], 'us')} | {_fmt_metric(b5[c]['prefix_sums'], 'us')} |"
        )

    md += [
        "",
        "## B6: Top-k Sellers (microseconds)",
        "| k | Size | Full `sorted()` (us) | Size-k Heap (us) |",
        "| :--- | :--- | :--- | :--- |",
    ]
    for k_label, k_data in b6.items():
        for c, metrics in k_data.items():
            md.append(
                f"| {k_label} | {c} | {_fmt_metric(metrics['full_sort'], 'us')} | {_fmt_metric(metrics['size_k_heap'], 'us')} |"
            )

    (RESULTS_DIR / "RESULTS.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"Saved results and 6 SVG charts to {RESULTS_DIR}")


if __name__ == "__main__":
    main()
