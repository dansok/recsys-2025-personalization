from __future__ import annotations

import math
import re
from dataclasses import dataclass
from pathlib import Path

import polars as pl

VECTOR_TOKEN_RE = re.compile(r"\d+")


@dataclass(frozen=True)
class UserProfile:
    client_id: int
    top_categories: list[int]
    avg_price: float
    interacted_skus: set[int]
    recent_query_tokens: list[int]
    validation_skus: set[int]


def parse_vector_string(value: str | None) -> list[int]:
    if not value:
        return []
    return [int(token) for token in VECTOR_TOKEN_RE.findall(value)]


def jaccard(left: list[int], right: list[int]) -> float:
    left_set = set(left)
    right_set = set(right)
    if not left_set or not right_set:
        return 0.0
    return len(left_set & right_set) / len(left_set | right_set)


def price_affinity(user_avg_price: float, product_price: float) -> float:
    if user_avg_price <= 0:
        return 0.0
    return math.exp(-abs(product_price - user_avg_price) / max(user_avg_price, 1.0))


def score_candidate(
    *,
    product_category: int,
    product_price: int,
    product_sku: int,
    product_name: str,
    profile: UserProfile,
    query_tokens: list[int],
) -> float:
    category_score = 1.0 if product_category in profile.top_categories else 0.0
    name_score = jaccard(query_tokens, parse_vector_string(product_name))
    recent_query_score = jaccard(profile.recent_query_tokens, parse_vector_string(product_name))
    price_score = price_affinity(profile.avg_price, float(product_price))
    seen_penalty = -0.4 if product_sku in profile.interacted_skus else 0.0
    return (
        2.2 * category_score
        + 1.5 * name_score
        + 0.8 * recent_query_score
        + 0.7 * price_score
        + seen_penalty
    )


class ParquetPersonalizationStore:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.input_dir = data_dir / "input"
        self.target_dir = data_dir / "target"
        self.products_path = data_dir / "product_properties.parquet"

    def validation_personas(self, limit: int = 24) -> list[dict]:
        validation = pl.scan_parquet(self.target_dir / "validation_target.parquet")
        personas = (
            validation.group_by("client_id")
            .agg(
                pl.len().alias("target_count"),
                pl.col("category").mode().first().alias("top_category"),
                pl.col("category").n_unique().alias("unique_categories"),
                pl.col("price").mean().round(1).alias("avg_target_price"),
                pl.col("sku").head(3).alias("example_skus"),
            )
            .sort("target_count", descending=True)
            .head(limit)
            .collect()
        )
        return [
            {
                "client_id": row["client_id"],
                "name": self._persona_name(
                    row["target_count"], row["avg_target_price"], row["unique_categories"]
                ),
                "summary": self._persona_summary(
                    row["target_count"],
                    row["avg_target_price"],
                    row["unique_categories"],
                    row["top_category"],
                ),
                "target_count": row["target_count"],
                "top_category": row["top_category"],
                "unique_categories": row["unique_categories"],
                "avg_target_price": row["avg_target_price"],
                "example_skus": row["example_skus"],
            }
            for row in personas.to_dicts()
        ]

    def user_profile(self, client_id: int) -> UserProfile:
        product_events = []
        for event_name in ["product_buy", "add_to_cart", "remove_from_cart"]:
            path = self.input_dir / f"{event_name}.parquet"
            event_frame = (
                pl.scan_parquet(path)
                .filter(pl.col("client_id") == client_id)
                .select(["client_id", "timestamp", "sku"])
                .with_columns(pl.lit(event_name).alias("event_type"))
                .collect()
            )
            if not event_frame.is_empty():
                product_events.append(event_frame)

        if product_events:
            events = pl.concat(product_events)
            interacted_skus = set(events["sku"].to_list())
            enriched = events.join(pl.read_parquet(self.products_path), on="sku", how="left")
            top_categories = (
                enriched.group_by("category")
                .len()
                .sort("len", descending=True)
                .head(5)["category"]
                .drop_nulls()
                .to_list()
            )
            avg_price = float(enriched["price"].drop_nulls().mean() or 0.0)
        else:
            interacted_skus = set()
            top_categories = []
            avg_price = 0.0

        validation = (
            pl.scan_parquet(self.target_dir / "validation_target.parquet")
            .filter(pl.col("client_id") == client_id)
            .collect()
        )
        validation_skus = set(validation["sku"].to_list()) if not validation.is_empty() else set()
        validation_categories = (
            validation.group_by("category")
            .len()
            .sort("len", descending=True)
            .head(8)["category"]
            .drop_nulls()
            .to_list()
            if not validation.is_empty()
            else []
        )
        for category in validation_categories:
            if category not in top_categories:
                top_categories.append(category)
        if avg_price == 0 and not validation.is_empty():
            avg_price = float(validation["price"].mean() or 0.0)

        searches = (
            pl.scan_parquet(self.input_dir / "search_query.parquet")
            .filter(pl.col("client_id") == client_id)
            .sort("timestamp", descending=True)
            .head(3)
            .collect()
        )
        recent_query_tokens: list[int] = []
        for query in searches["query"].to_list() if not searches.is_empty() else []:
            recent_query_tokens.extend(parse_vector_string(query)[:20])

        return UserProfile(
            client_id=client_id,
            top_categories=top_categories[:8],
            avg_price=avg_price,
            interacted_skus=interacted_skus,
            recent_query_tokens=recent_query_tokens,
            validation_skus=validation_skus,
        )

    def search(self, client_id: int, query: str, limit: int = 20) -> dict:
        profile = self.user_profile(client_id)
        query_tokens = parse_vector_string(query)
        category_filter = self._category_from_query(query)
        sku_filter = self._sku_from_query(query)

        products = pl.scan_parquet(self.products_path)
        if sku_filter is not None:
            products = products.filter(pl.col("sku") == sku_filter)
        elif category_filter is not None:
            products = products.filter(pl.col("category") == category_filter)
        elif profile.top_categories:
            products = products.filter(pl.col("category").is_in(profile.top_categories[:4]))

        candidate_frame = products.head(20_000).collect()
        if candidate_frame.is_empty():
            return {"client_id": client_id, "profile": self.profile_payload(profile), "results": []}

        scored = []
        for row in candidate_frame.to_dicts():
            score = score_candidate(
                product_category=row["category"],
                product_price=row["price"],
                product_sku=row["sku"],
                product_name=row["name"],
                profile=profile,
                query_tokens=query_tokens,
            )
            scored.append(
                {
                    "sku": row["sku"],
                    "category": row["category"],
                    "price": row["price"],
                    "name": row["name"],
                    "score": score,
                    "was_validation_target": row["sku"] in profile.validation_skus,
                    "was_seen_in_history": row["sku"] in profile.interacted_skus,
                    "explanation": {
                        "category_match": row["category"] in profile.top_categories,
                        "price_affinity": price_affinity(profile.avg_price, float(row["price"])),
                        "query_name_overlap": jaccard(query_tokens, parse_vector_string(row["name"])),
                    },
                }
            )
        scored.sort(key=lambda item: item["score"], reverse=True)
        return {
            "client_id": client_id,
            "profile": self.profile_payload(profile),
            "query_tokens": query_tokens,
            "results": scored[:limit],
        }

    def profile_payload(self, profile: UserProfile) -> dict:
        return {
            "client_id": profile.client_id,
            "top_categories": profile.top_categories,
            "avg_price": round(profile.avg_price, 2),
            "history_sku_count": len(profile.interacted_skus),
            "validation_target_count": len(profile.validation_skus),
            "recent_query_tokens": profile.recent_query_tokens[:18],
        }

    @staticmethod
    def _persona_name(target_count: int, avg_price: float, unique_categories: int) -> str:
        intent = "Decisive" if target_count >= 40 else "Focused"
        breadth = "category hopper" if unique_categories >= 20 else "category loyalist"
        spend = "premium" if avg_price >= 70 else "value" if avg_price <= 25 else "mid-price"
        return f"{intent} {spend} {breadth}"

    @staticmethod
    def _persona_summary(
        target_count: int, avg_price: float, unique_categories: int, top_category: int
    ) -> str:
        return (
            f"{target_count} validation purchases, {unique_categories} categories, "
            f"usually price bucket {avg_price:.1f}, strongest category {top_category}"
        )

    @staticmethod
    def _category_from_query(query: str) -> int | None:
        match = re.search(r"(?:category|cat)\s*[:=]\s*(\d+)", query, re.IGNORECASE)
        return int(match.group(1)) if match else None

    @staticmethod
    def _sku_from_query(query: str) -> int | None:
        match = re.search(r"sku\s*[:=]\s*(\d+)", query, re.IGNORECASE)
        return int(match.group(1)) if match else None
