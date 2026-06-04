from typing import Self

import polars as pl

from recsys_personalization.models.base import Recommender


class LightGbmRanker(Recommender):
    """Wrapper scaffold for the non-from-scratch learning-to-rank baseline."""

    name = "lightgbm_ranker"

    def fit(self, interactions: pl.DataFrame) -> Self:
        raise NotImplementedError("Implement feature assembly and LightGBM ranker fitting.")

    def score(self, client_id: int, skus: list[int]) -> list[float]:
        raise NotImplementedError("Implement feature lookup and LightGBM prediction.")
