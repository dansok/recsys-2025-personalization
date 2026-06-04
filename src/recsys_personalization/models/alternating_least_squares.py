from typing import Self

import polars as pl

from recsys_personalization.models.base import Recommender


class AlternatingLeastSquaresRecommender(Recommender):
    """Implicit-feedback alternating least squares scaffold."""

    name = "alternating_least_squares"

    def fit(self, interactions: pl.DataFrame) -> Self:
        raise NotImplementedError("Implement alternating user/item least-squares updates.")

    def score(self, client_id: int, skus: list[int]) -> list[float]:
        raise NotImplementedError("Implement learned factor scoring.")
