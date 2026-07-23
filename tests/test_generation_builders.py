from pipeline.generation.case_file_builder import CaseFileDraft, DraftClaim, DraftEvent, DraftFact
from pipeline.generation.claims_ledger_builder import build_claims_ledger
from pipeline.generation.fact_verifier import critique_verifiable_facts
from pipeline.generation.relations_builder import build_topic_relations
from pipeline.generation.summarizer import build_neutral_summary
from pipeline.generation.timeline_builder import build_timeline


def test_roadmap_phase3_builders_keep_source_bound_artifacts() -> None:
    draft = CaseFileDraft(
        title="Reserve Bank of India",
        slug="reserve-bank-of-india",
        neutral_summary="Neutral source-bound summary.",
        significance_score=10,
        promotable=False,
        events=(DraftEvent("2026-07-20", "Later event", ("s2",), ("https://rbi/b",)), DraftEvent("2026-07-19", "Earlier event", ("s1",), ("https://rbi/a",))),
        claims=(DraftClaim("govt", "Govt claim", "quoted span", "s1", "https://rbi/a"), DraftClaim("media", "Media claim", "quoted span", "s2", "https://news/a")),
        verifiable_facts=(DraftFact("Fact", "https://rbi/a", "dataset", "quoted span"),),
        related_entities=("Reserve Bank of India",),
        ministry_entity_name="Reserve Bank of India",
    )

    assert build_neutral_summary(draft) == "Neutral source-bound summary."
    assert build_claims_ledger(draft).govt[0].source_url == "https://rbi/a"
    assert build_timeline(draft)[0].event_date == "2026-07-19"
    assert critique_verifiable_facts(draft)[0].status == "pass"


def test_relations_builder_links_shared_entities() -> None:
    first = CaseFileDraft(
        title="RBI",
        slug="rbi",
        neutral_summary="",
        significance_score=1,
        promotable=False,
        events=(),
        claims=(),
        verifiable_facts=(),
        related_entities=("Reserve Bank of India",),
        ministry_entity_name="Reserve Bank of India",
    )
    second = CaseFileDraft(
        title="Finance",
        slug="finance",
        neutral_summary="",
        significance_score=1,
        promotable=False,
        events=(),
        claims=(),
        verifiable_facts=(),
        related_entities=("Reserve Bank of India", "Ministry of Finance"),
        ministry_entity_name="Reserve Bank of India",
    )

    relations = build_topic_relations([("topic-a", first), ("topic-b", second)])

    assert relations[0].topic_id_a == "topic-a"
    assert relations[0].topic_id_b == "topic-b"
    assert relations[0].relation_type == "same_policy_area"
