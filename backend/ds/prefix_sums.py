"""
backend/ds/prefix_sums.py
Prefix sums array for O(1) date-range revenue, units, and COGS queries.
Contract: docs/adt/prefix_sums.md
Used by: financial reports and sales speed calculations (Doc 7.3 C, Phase 1.7).
"""


class PrefixSums:
    """
    Prefix sums array providing $O(n)$ build and $O(1)$ range sum queries.
    Range sum formula:
    range_sum(L, R) = prefix[R] - (prefix[L - 1] if L > 0 else 0)
    """

    def __init__(self, values: list[float] | None = None):
        self._prefix: list[float] = []
        if values is not None:
            self.build(values)

    def build(self, values: list[float]) -> None:
        """Construct running prefix array from a list of numerical values in O(n) time."""
        self._prefix = []
        running = 0.0
        for v in values:
            running += v
            self._prefix.append(running)

    def range_sum(self, start_idx: int, end_idx: int) -> float:
        """
        Calculate sum of elements between start_idx and end_idx (inclusive) in O(1) time.
        Raises IndexError for out of bounds, ValueError if start_idx > end_idx.
        """
        n = len(self._prefix)
        if start_idx < 0 or end_idx >= n or n == 0:
            raise IndexError(
                f"Range indices ({start_idx}, {end_idx}) out of bounds for size {n}"
            )
        if start_idx > end_idx:
            raise ValueError(
                f"start_idx ({start_idx}) cannot exceed end_idx ({end_idx})"
            )

        if start_idx == 0:
            return self._prefix[end_idx]
        return self._prefix[end_idx] - self._prefix[start_idx - 1]

    def size(self) -> int:
        """Return number of values in original series."""
        return len(self._prefix)

    def is_empty(self) -> bool:
        """Return True if prefix array is empty."""
        return len(self._prefix) == 0
