import polars as pl

from recsys_personalization.models.popularity import PopularityRecommender


def train_popularity(interactions: pl.DataFrame) -> PopularityRecommender:
    return PopularityRecommender().fit(interactions)
