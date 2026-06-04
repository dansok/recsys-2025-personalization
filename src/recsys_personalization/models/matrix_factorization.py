from typing import Self

import polars as pl

from recsys_personalization.models.base import Recommender


class MatrixFactorizationRecommender(Recommender):
    """Explicit or implicit matrix factorization scaffold."""

    name = "matrix_factorization"

    def fit(self, interactions: pl.DataFrame) -> Self:
        raise NotImplementedError("Implement latent factor training.")

    def score(self, client_id: int, skus: list[int]) -> list[float]:
        raise NotImplementedError("Implement dot-product scoring.")
