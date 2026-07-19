from pipeline.generation.case_file_builder import build_case_file_draft
from pipeline.processing.clusterer import cluster_signals


def test_case_file_draft_keeps_claims_source_bound() -> None:
    rows = [
        {
            "id": "a",
            "published_at": "2026-07-20T10:00:00+00:00",
            "title": "RBI announces update",
            "raw_text": "Reserve Bank of India announced a regulatory update. More detail follows.",
            "url": "https://rbi/a",
            "sources": {"source_key": "rbi", "trust_category": "official"},
        }
    ]
    cluster = cluster_signals(rows, limit=1)[0]

    draft = build_case_file_draft(cluster)

    assert draft.title == "Reserve Bank of India"
    assert draft.claims[0].quoted_span == "RBI announces update Reserve Bank of India announced a regulatory update."
    assert draft.claims[0].source_url == "https://rbi/a"
    assert draft.verifiable_facts[0].primary_doc_url == "https://rbi/a"


def test_case_file_draft_cleans_html_from_quoted_spans() -> None:
    rows = [
        {
            "id": "a",
            "published_at": "2026-07-20T10:00:00+00:00",
            "title": "RBI penalty",
            "raw_text": "<table><tr><td>The Reserve Bank &amp; ministry issued a penalty.</td></tr></table>",
            "url": "https://rbi/a",
            "sources": {"source_key": "rbi", "trust_category": "official"},
        }
    ]
    cluster = cluster_signals(rows, limit=1)[0]

    draft = build_case_file_draft(cluster)

    assert "<table" not in draft.claims[0].quoted_span
    assert "Reserve Bank & ministry" in draft.claims[0].quoted_span
