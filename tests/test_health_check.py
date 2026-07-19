from pipeline.monitoring.health_check import assess_signal_count
from pipeline import scheduler


def test_new_sources_do_not_alert_without_a_baseline() -> None:
    assessment = assess_signal_count("source", 0, [20, 18])
    assert assessment.baseline_count is None
    assert not assessment.is_abnormal_drop


def test_large_drop_after_a_baseline_is_flagged() -> None:
    assessment = assess_signal_count("source", 3, [20, 18, 22, 19])
    assert assessment.baseline_count == 19.5
    assert assessment.is_abnormal_drop


def test_normal_variation_is_not_flagged() -> None:
    assessment = assess_signal_count("source", 18, [20, 18, 22, 19])
    assert not assessment.is_abnormal_drop


def test_scheduler_test_alert_exits_without_fetching_sources(monkeypatch) -> None:
    monkeypatch.setattr(scheduler, "send_alert", lambda message: message.startswith("Tathya test alert"))
    assert scheduler.main(["--test-alert"]) == 0
