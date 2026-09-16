from __future__ import annotations

"""Tiny in-process LRU cache for query embeddings.

AI workers issue repeated / similar tool calls; caching the query embedding
avoids recomputation. Kept dependency-free (OrderedDict) so it works the same
offline and in CI. A production deployment would back this with Redis.
"""

from collections import OrderedDict
from typing import Callable


class LRUCache:
    def __init__(self, capacity: int = 256) -> None:
        self.capacity = capacity
        self._store: "OrderedDict[str, list[float]]" = OrderedDict()
        self.hits = 0
        self.misses = 0

    def get_or_compute(self, key: str, compute: Callable[[], list[float]]) -> list[float]:
        if key in self._store:
            self.hits += 1
            self._store.move_to_end(key)
            return self._store[key]
        self.misses += 1
        value = compute()
        self._store[key] = value
        self._store.move_to_end(key)
        if len(self._store) > self.capacity:
            self._store.popitem(last=False)
        return value

    def stats(self) -> dict:
        total = self.hits + self.misses
        return {
            "hits": self.hits,
            "misses": self.misses,
            "size": len(self._store),
            "hit_rate": round(self.hits / total, 3) if total else 0.0,
        }
