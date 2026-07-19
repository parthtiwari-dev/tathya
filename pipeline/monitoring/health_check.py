"""Detect an abnormal signal-count drop without judging source content."""

from dataclasses import dataclass
from statistics import median


@dataclass(frozen=True)
class HealthAssessment:
    source_key: str
    signal_count: int
    baseline_count: float | None
    is_abnormal_drop: bool


def assess_signal_count(source_key: str, signal_count: int, historical_counts: list[int]) -> HealthAssessment:
    """Flag a source producing under 20% of its normal recent count.

    A source needs at least three non-empty historical runs before it can alert;
    this prevents new or intermittently active sources from generating noise.
    """
    baseline_samples = [count for count in historical_counts if count > 0]
    if len(baseline_samples) < 3:
        return HealthAssessment(source_key, signal_count, None, False)
    baseline = float(median(baseline_samples))
    return HealthAssessment(
        source_key=source_key,
        signal_count=signal_count,
        baseline_count=baseline,
        is_abnormal_drop=signal_count < baseline * 0.2,
    )
