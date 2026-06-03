import polars as pl


PRODUCT_EVENT_WEIGHTS = {
    "product_buy": 4.0,
    "add_to_cart": 2.0,
    "remove_from_cart": -1.0,
}


def interaction_score(event_type: str) -> float:
    return PRODUCT_EVENT_WEIGHTS.get(event_type, 0.0)


def build_user_features(
    product_events: pl.DataFrame,
    page_visits: pl.DataFrame,
    search_queries: pl.DataFrame,
    product_properties: pl.DataFrame,
    feature_set: str = "behavioral_v1",
) -> pl.DataFrame:
    enriched = product_events.join(product_properties, on="sku", how="left")
    max_ts = product_events["timestamp"].max()

    product_features = (
        enriched.group_by("client_id")
        .agg(
            (pl.col("event_type") == "product_buy").sum().cast(pl.UInt32).alias("buy_count"),
            (pl.col("event_type") == "add_to_cart").sum().cast(pl.UInt32).alias("add_to_cart_count"),
            (pl.col("event_type") == "remove_from_cart").sum().cast(pl.UInt32).alias("remove_from_cart_count"),
            pl.col("sku").n_unique().cast(pl.UInt32).alias("unique_skus"),
            pl.col("category").n_unique().cast(pl.UInt32).alias("unique_categories"),
            pl.col("price").mean().cast(pl.Float32).fill_null(0).alias("avg_price_bucket"),
            (
                (pl.lit(max_ts) - pl.col("timestamp").filter(pl.col("event_type") == "product_buy").max())
                .dt.total_days()
                .cast(pl.Float32)
                .fill_null(9999.0)
            ).alias("days_since_last_buy"),
        )
    )
    page_features = page_visits.group_by("client_id").agg(
        pl.len().cast(pl.UInt32).alias("page_visit_count")
    )
    search_features = search_queries.group_by("client_id").agg(
        pl.len().cast(pl.UInt32).alias("search_count")
    )

    return (
        product_features.join(page_features, on="client_id", how="full", coalesce=True)
        .join(search_features, on="client_id", how="full", coalesce=True)
        .with_columns(
            pl.lit(feature_set).alias("feature_set"),
            pl.col("buy_count").fill_null(0),
            pl.col("add_to_cart_count").fill_null(0),
            pl.col("remove_from_cart_count").fill_null(0),
            pl.col("page_visit_count").fill_null(0),
            pl.col("search_count").fill_null(0),
            pl.col("unique_skus").fill_null(0),
            pl.col("unique_categories").fill_null(0),
            pl.col("avg_price_bucket").fill_null(0),
            pl.col("days_since_last_buy").fill_null(9999.0),
        )
        .select(
            [
                "feature_set",
                "client_id",
                "buy_count",
                "add_to_cart_count",
                "remove_from_cart_count",
                "page_visit_count",
                "search_count",
                "unique_skus",
                "unique_categories",
                "avg_price_bucket",
                "days_since_last_buy",
            ]
        )
    )
