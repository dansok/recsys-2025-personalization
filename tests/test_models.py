import polars as pl

from recsys_personalization.models.popularity import PopularityRecommender


def test_popularity_recommender_scores_weighted_events() -> None:
    interactions = pl.DataFrame(
        {
            "client_id": [1, 1, 2, 2],
            "event_type": ["product_buy", "add_to_cart", "remove_from_cart", "product_buy"],
            "sku": [10, 20, 20, 30],
        }
    )

    model = PopularityRecommender().fit(interactions)

    assert model.score(client_id=99, skus=[10, 20, 30, 40]) == [4.0, 1.0, 4.0, 0.0]


def test_popularity_recommender_ranks_candidates() -> None:
    interactions = pl.DataFrame(
        {
            "event_type": ["add_to_cart", "product_buy"],
            "sku": [10, 20],
        }
    )

    model = PopularityRecommender().fit(interactions)
    recommendations = model.recommend(client_id=1, candidates=[10, 20], k=2)

    assert [item.sku for item in recommendations] == [20, 10]
    assert [item.score for item in recommendations] == [4.0, 2.0]
