"""
backend/ds/prefix_sums.py
Prefix sums array for O(1) date-range revenue, units, and COGS queries.
Contract: docs/adt/prefix_sums.md
"""


class PrefixSums:
    def __init__(self, values: list[float] | None = None):
        self._prefix = []
        if values:
            self.build(values)

    def build(self, values: list[float]) -> None:
        pass

    def range_sum(self, start_idx: int, end_idx: int) -> float:
        pass

    def size(self) -> int:
        return len(self._prefix)

