import numpy as np


def apk(actual: set[int], predicted: list[int], k: int) -> float:
    if not actual:
        return 0.0
    hits = 0
    score = 0.0
    seen: set[int] = set()
    for idx, item in enumerate(predicted[:k], start=1):
        if item in seen:
            continue
        seen.add(item)
        if item in actual:
            hits += 1
            score += hits / idx
    return score / min(len(actual), k)


def mapk(actual: list[set[int]], predicted: list[list[int]], k: int) -> float:
    if not actual:
        return 0.0
    return float(np.mean([apk(a, p, k) for a, p in zip(actual, predicted, strict=True)]))


def recall_at_k(actual: set[int], predicted: list[int], k: int) -> float:
    if not actual:
        return 0.0
    return len(actual & set(predicted[:k])) / len(actual)

