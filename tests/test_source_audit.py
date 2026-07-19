from pipeline import source_audit


def test_source_audit_lists_sources(capsys) -> None:
    assert source_audit.main(["--list"]) == 0
    assert "indian-express-india" in capsys.readouterr().out


def test_source_audit_reports_unknown_source() -> None:
    try:
        source_audit.main(["--source", "missing"])
    except SystemExit as error:
        assert "Unknown source" in str(error)
    else:
        raise AssertionError("Expected SystemExit for an unknown source")


def test_source_audit_returns_failure_without_traceback(monkeypatch, capsys) -> None:
    def fail(_source):
        raise RuntimeError("blocked")

    monkeypatch.setattr(source_audit, "fetch_signals", fail)
    assert source_audit.main(["--source", "indian-express-india"]) == 1
    assert "FAILED (blocked)" in capsys.readouterr().out
