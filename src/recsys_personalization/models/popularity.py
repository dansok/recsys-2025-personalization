from typing import Self

import polars as pl

from recsys_personalization.features import PRODUCT_EVENT_WEIGHTS
from recsys_personalization.models.base import Recommender


class PopularityRecommender(Recommender):
    """Weighted global popularity baseline implemented from interaction events."""

    name = "popularity"

    def __init__(self) -> None:
        self._scores: dict[int, float] = {}
        self._default_score = 0.0

    def fit(self, interactions: pl.DataFrame) -> Self:
        required = {"event_type", "sku"}
        missing = required - set(interactions.columns)
        if missing:
            raise ValueError(f"interactions missing required columns: {sorted(missing)}")

        scores = (
            interactions.with_columns(
                pl.col("event_type")
                .replace_strict(PRODUCT_EVENT_WEIGHTS, default=0.0, return_dtype=pl.Float64)
                .alias("event_weight")
            )
            .group_by("sku")
            .agg(pl.col("event_weight").sum().alias("score"))
        )
        self._scores = dict(zip(scores["sku"].to_list(), scores["score"].to_list(), strict=True))
        return self

    def score(self, client_id: int, skus: list[int]) -> list[float]:
        _ = client_id
        return [self._scores.get(sku, self._default_score) for sku in skus]
