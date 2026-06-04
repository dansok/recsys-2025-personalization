from typing import Self

import polars as pl

from recsys_personalization.models.base import Recommender


class FactorizationMachineRecommender(Recommender):
    """Factorization machine scaffold for sparse user/item/context features."""

    name = "factorization_machine"

    def fit(self, interactions: pl.DataFrame) -> Self:
        raise NotImplementedError("Implement FM feature encoding and optimization.")

    def score(self, client_id: int, skus: list[int]) -> list[float]:
        raise NotImplementedError("Implement FM scoring for candidate products.")
