from dataclasses import dataclass

from recsys_personalization.models.base import Recommender


@dataclass(frozen=True, slots=True)
class BenchmarkResult:
    model_name: str
    metrics: dict[str, float]


def benchmark_model(model: Recommender) -> BenchmarkResult:
    raise NotImplementedError("Implement shared offline benchmark harness.")
