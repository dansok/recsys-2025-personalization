from typing import Self

import polars as pl

from recsys_personalization.models.base import Recommender


class BayesianPersonalizedRankingRecommender(Recommender):
    """BPR pairwise ranking scaffold."""

    name = "bayesian_personalized_ranking"

    def fit(self, interactions: pl.DataFrame) -> Self:
        raise NotImplementedError("Implement pairwise BPR sampling and optimization.")

    def score(self, client_id: int, skus: list[int]) -> list[float]:
        raise NotImplementedError("Implement learned user/item factor scoring.")
