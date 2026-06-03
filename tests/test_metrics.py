from recsys_personalization.metrics import apk, mapk, recall_at_k


def test_apk_scores_ordered_hits():
    assert apk({1, 2}, [1, 3, 2], 3) == (1 / 1 + 2 / 3) / 2


def test_mapk_averages_users():
    assert mapk([{1}, {4}], [[1, 2], [3, 4]], 2) == (1.0 + 0.5) / 2


def test_recall_at_k():
    assert recall_at_k({1, 2, 3}, [3, 4, 5], 2) == 1 / 3

