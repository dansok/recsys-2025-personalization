from typing import Self

import polars as pl

from recsys_personalization.models.base import Recommender


class ItemNearestNeighborsRecommender(Recommender):
    """Item-item collaborative filtering scaffold."""

    name = "item_nearest_neighbors"

    def fit(self, interactions: pl.DataFrame) -> Self:
        raise NotImplementedError("Implement item-item similarity and neighbor indexing.")

    def score(self, client_id: int, skus: list[int]) -> list[float]:
        raise NotImplementedError("Implement item-neighborhood scoring.")
