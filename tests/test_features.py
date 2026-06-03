from datetime import datetime

import polars as pl

from recsys_personalization.features import build_user_features, interaction_score


def test_interaction_score_orders_behavior_strength():
    assert interaction_score("product_buy") > interaction_score("add_to_cart")
    assert interaction_score("remove_from_cart") < 0


def test_build_user_features_aggregates_events():
    product_events = pl.DataFrame(
        {
            "event_type": ["product_buy", "add_to_cart", "remove_from_cart"],
            "client_id": [1, 1, 2],
            "timestamp": [
                datetime(2026, 1, 1),
                datetime(2026, 1, 2),
                datetime(2026, 1, 3),
            ],
            "sku": [10, 11, 12],
        }
    )
    page_visits = pl.DataFrame(
        {"client_id": [1, 1, 2], "timestamp": [datetime(2026, 1, 1)] * 3, "url": [5, 6, 7]}
    )
    search_queries = pl.DataFrame(
        {"client_id": [1], "timestamp": [datetime(2026, 1, 1)], "query": [[1, 2, 3]]}
    )
    product_properties = pl.DataFrame(
        {"sku": [10, 11, 12], "category": [100, 100, 200], "price": [10, 20, 30], "name": [[1], [2], [3]]}
    )

    features = build_user_features(product_events, page_visits, search_queries, product_properties)
    user_one = features.filter(pl.col("client_id") == 1).row(0, named=True)

    assert user_one["buy_count"] == 1
    assert user_one["add_to_cart_count"] == 1
    assert user_one["page_visit_count"] == 2
    assert user_one["search_count"] == 1
    assert user_one["unique_categories"] == 1

