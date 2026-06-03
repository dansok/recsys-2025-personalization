from recsys_personalization.personalization import (
    UserProfile,
    jaccard,
    parse_vector_string,
    price_affinity,
    score_candidate,
)


def test_parse_vector_string_extracts_anonymized_tokens():
    assert parse_vector_string("[202 151  50]") == [202, 151, 50]
    assert parse_vector_string("category:3398") == [3398]


def test_jaccard_handles_empty_vectors():
    assert jaccard([], [1]) == 0.0
    assert jaccard([1, 2], [2, 3]) == 1 / 3


def test_price_affinity_is_highest_near_user_average():
    assert price_affinity(50, 50) > price_affinity(50, 90)


def test_score_candidate_prefers_profile_category():
    profile = UserProfile(
        client_id=1,
        top_categories=[10],
        avg_price=50,
        interacted_skus=set(),
        recent_query_tokens=[],
        validation_skus=set(),
    )
    preferred = score_candidate(
        product_category=10,
        product_price=50,
        product_sku=1,
        product_name="[1 2]",
        profile=profile,
        query_tokens=[],
    )
    other = score_candidate(
        product_category=20,
        product_price=50,
        product_sku=2,
        product_name="[1 2]",
        profile=profile,
        query_tokens=[],
    )
    assert preferred > other

