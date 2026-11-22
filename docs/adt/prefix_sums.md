# ADT Specification: Prefix Sums Array

**Module**: `backend/ds/prefix_sums.py`
**Target Role**: Fast date-range financial queries (revenue, units, COGS).

## Operations & Guarantees
- `build(daily_values)`: Constructs running prefix array in $O(n)$ time.
- `range_sum(start_idx, end_idx)`: Calculates sum between two indices in $O(1)$ time:
  $$\text{sum} = \text{prefix}[end] - \text{prefix}[start - 1]$$
- `size()`: Returns length of daily series.

