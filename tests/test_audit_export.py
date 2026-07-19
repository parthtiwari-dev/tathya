from pipeline import audit_export


def test_audit_export_prints_claim_rows(monkeypatch, capsys) -> None:
    class Repository:
        @classmethod
        def from_environment(cls):
            return cls()

        def get_table_rows(self, path):
            assert path.startswith("claims?")
            return [{"id": "1", "claim_text": "claim", "quoted_span": "quote"}]

    monkeypatch.setattr(audit_export, "SupabaseRepository", Repository)

    assert audit_export.main(["--target", "claims", "--limit", "1"]) == 0
    output = capsys.readouterr().out
    assert "claim_text" in output
    assert "quote" in output


def test_audit_export_empty_rows_have_header(monkeypatch, capsys) -> None:
    class Repository:
        @classmethod
        def from_environment(cls):
            return cls()

        def get_table_rows(self, path):
            assert path.startswith("events?")
            return []

    monkeypatch.setattr(audit_export, "SupabaseRepository", Repository)

    assert audit_export.main(["--target", "events", "--limit", "1"]) == 0
    assert capsys.readouterr().out.strip() == "empty"
