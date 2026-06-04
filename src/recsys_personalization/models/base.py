from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Self

import polars as pl


@dataclass(frozen=True, slots=True)
class Recommendation:
    sku: int
    score: float


class Recommender(ABC):
    """Common interface for from-scratch recommenders and rankers."""

    name: str

    @abstractmethod
    def fit(self, interactions: pl.DataFrame) -> Self:
        """Fit model state from interaction events."""

    @abstractmethod
    def score(self, client_id: int, skus: list[int]) -> list[float]:
        """Score candidate products for a single client."""

    def recommend(self, client_id: int, candidates: list[int], k: int = 10) -> list[Recommendation]:
        scored = zip(candidates, self.score(client_id, candidates), strict=True)
        ranked = sorted(scored, key=lambda item: item[1], reverse=True)
        return [Recommendation(sku=sku, score=score) for sku, score in ranked[:k]]
