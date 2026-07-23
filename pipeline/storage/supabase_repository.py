"""Small PostgREST client for the atomic signal/snapshot database function."""

import json
import os
from dataclasses import dataclass
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from dotenv import load_dotenv

from pipeline.processing.snapshotter import build_snapshot
from pipeline.generation.case_file_builder import CaseFileDraft
from shared.models import IngestedSignal
from shared.slugify import slugify

_TOPIC_TAXONOMY_SELECT = (
    "topic_entities(is_ministry,entities(name,slug)),"
    "topic_signals(signal:signals(id,source:sources(source_key,trust_category)))"
)


@dataclass(frozen=True)
class SupabaseRepository:
    url: str
    service_role_key: str

    @classmethod
    def from_environment(cls) -> "SupabaseRepository":
        load_dotenv()
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        if not url or not key:
            raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set for --persist")
        return cls(url=url.rstrip("/"), service_role_key=key)

    def persist_signal(self, signal: IngestedSignal) -> str:
        """Insert a signal plus its immutable snapshot through one database transaction."""
        snapshot = build_snapshot(signal)
        payload = {
            "p_source_key": signal.source_key,
            "p_published_at": signal.published_at.isoformat(),
            "p_title": signal.title,
            "p_raw_text": signal.raw_text,
            "p_transcript": signal.transcript,
            "p_url": str(signal.canonical_url),
            "p_captured_at": snapshot.captured_at.isoformat(),
            "p_raw_content": snapshot.raw_content,
            "p_content_hash": snapshot.content_hash,
        }
        request = Request(
            f"{self.url.rstrip('/')}/rest/v1/rpc/record_signal_snapshot",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "apikey": self.service_role_key,
                "Authorization": f"Bearer {self.service_role_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urlopen(request, timeout=30) as response:  # noqa: S310 -- URL is deployment config.
            raw = response.read().decode("utf-8").strip()
            return json.loads(raw) if raw else None

    def recent_source_counts(self, source_key: str) -> list[int]:
        payload = {"p_source_key": source_key, "p_limit": 10}
        result = self._rpc("recent_source_counts", payload)
        return [row["signal_count"] for row in result]

    def record_source_run(self, source_key: str, signal_count: int, status: str, detail: str | None = None) -> None:
        self._rpc("record_source_run", {"p_source_key": source_key, "p_signal_count": signal_count, "p_status": status, "p_detail": detail})

    def set_source_enabled(self, source_key: str, enabled: bool) -> bool:
        result = self._rpc("set_source_enabled", {"p_source_key": source_key, "p_enabled": enabled})
        return bool(result)

    def source_activation_summary(self, source_key: str) -> dict:
        result = self._rpc("source_activation_summary", {"p_source_key": source_key})
        if not result:
            return {}
        return result[0]

    def recent_signals(self, limit: int = 250) -> list[dict]:
        query = urlencode(
            {
                "select": "id,published_at,title,raw_text,transcript,url,duplicate_of_signal_id,sources(source_key,trust_category)",
                "order": "published_at.desc",
                "limit": str(limit),
            }
        )
        result = self._get(f"signals?{query}")
        return result if isinstance(result, list) else []

    def recent_signals_without_embeddings(self, limit: int = 100) -> list[dict]:
        query = urlencode(
            {
                "select": "id,published_at,title,raw_text,transcript,url,duplicate_of_signal_id,sources(source_key,trust_category)",
                "embedding": "is.null",
                "order": "published_at.desc",
                "limit": str(limit),
            }
        )
        result = self._get(f"signals?{query}")
        return result if isinstance(result, list) else []

    def store_signal_embedding(self, signal_id: str, embedding_literal: str) -> None:
        self._rpc("store_signal_embedding", {"p_signal_id": signal_id, "p_embedding": embedding_literal})

    def match_similar_signals(self, embedding_literal: str, match_count: int = 20, match_threshold: float = 0.0) -> list[dict]:
        result = self._rpc(
            "match_similar_signals",
            {
                "p_query_embedding": embedding_literal,
                "p_match_count": match_count,
                "p_match_threshold": match_threshold,
            },
        )
        return result if isinstance(result, list) else []

    def get_table_rows(self, path: str) -> list[dict]:
        result = self._get(path)
        return result if isinstance(result, list) else []

    def list_topics(self, limit: int = 20, offset: int = 0) -> tuple[list[dict], int | None]:
        query = urlencode(
            {
                "select": f"id,slug,title,status,first_seen,last_signal_at,significance_score,summary,summary_generated_at,{_TOPIC_TAXONOMY_SELECT}",
                "order": "last_signal_at.desc",
                "limit": str(limit),
                "offset": str(offset),
            }
        )
        return self._get_with_count(f"topics?{query}")

    def get_topic_by_slug(self, slug: str) -> dict | None:
        query = urlencode(
            {
                "slug": f"eq.{slug}",
                "select": f"id,slug,title,status,first_seen,last_signal_at,significance_score,summary,summary_generated_at,{_TOPIC_TAXONOMY_SELECT}",
            }
        )
        rows = self.get_table_rows(f"topics?{query}")
        return rows[0] if rows else None

    def list_sources(self) -> list[dict]:
        query = urlencode({"select": "*", "order": "source_key.asc"})
        return self.get_table_rows(f"sources?{query}")

    def get_source(self, source_key: str) -> dict | None:
        query = urlencode({"select": "*", "source_key": f"eq.{source_key}"})
        rows = self.get_table_rows(f"sources?{query}")
        return rows[0] if rows else None

    def signals_for_source(self, source_key: str, limit: int = 50, offset: int = 0) -> tuple[list[dict], int | None]:
        query = urlencode(
            {
                "select": "id,published_at,title,raw_text,url,duplicate_of_signal_id,sources!inner(source_key)",
                "sources.source_key": f"eq.{source_key}",
                "order": "published_at.desc",
                "limit": str(limit),
                "offset": str(offset),
            }
        )
        return self._get_with_count(f"signals?{query}")

    def source_runs(self, source_key: str | None = None, limit: int = 50, offset: int = 0) -> tuple[list[dict], int | None]:
        params = {
            "select": "id,collected_at,signal_count,status,detail,sources(source_key,name)",
            "order": "collected_at.desc",
            "limit": str(limit),
            "offset": str(offset),
        }
        if source_key:
            params["sources.source_key"] = f"eq.{source_key}"
        return self._get_with_count(f"source_run_metrics?{urlencode(params)}")

    def link_topic_entities(self, topic_id: str, entity_names: tuple[str, ...]) -> None:
        """Match entity_names against the entities table and link them to the topic.

        Called once per persisted topic so Topic.ministry/ministrySlug/entityTags
        can be read straight off the join table instead of re-running entity
        matching on every request.
        """
        if not entity_names:
            return
        quoted = ",".join('"' + name.replace('"', '\\"') + '"' for name in entity_names)
        query = urlencode({"name": f"in.({quoted})", "select": "id,name,type,slug"})
        rows = self.get_table_rows(f"entities?{query}")
        if not rows:
            return
        for row in rows:
            if not row.get("slug"):
                self._patch(f"entities?id=eq.{row['id']}", {"slug": slugify(row["name"])})
        payload = [
            {"topic_id": topic_id, "entity_id": row["id"], "is_ministry": row["type"] == "ministry"}
            for row in rows
        ]
        self._post(
            "topic_entities?on_conflict=topic_id,entity_id",
            payload,
            prefer="resolution=merge-duplicates,return=minimal",
        )

    def topic_claims(self, topic_id: str) -> list[dict]:
        query = urlencode(
            {
                "topic_id": f"eq.{topic_id}",
                "select": "*,signal:signals(published_at,url,source:sources(source_key,name))",
                "order": "created_at.asc",
            }
        )
        return self.get_table_rows(f"claims?{query}")

    def topic_events(self, topic_id: str) -> list[dict]:
        query = urlencode({"topic_id": f"eq.{topic_id}", "select": "*", "order": "event_date.asc"})
        return self.get_table_rows(f"events?{query}")

    def topic_facts(self, topic_id: str) -> list[dict]:
        query = urlencode({"topic_id": f"eq.{topic_id}", "select": "*", "order": "created_at.asc"})
        return self.get_table_rows(f"verifiable_facts?{query}")

    def topic_relations_list(self, topic_id: str) -> list[dict]:
        relations_a = self.get_table_rows(
            f"topic_relations?{urlencode({'topic_id_a': f'eq.{topic_id}', 'select': '*,related:topics!topic_relations_topic_id_b_fkey(id,slug,title)'})}"
        )
        relations_b = self.get_table_rows(
            f"topic_relations?{urlencode({'topic_id_b': f'eq.{topic_id}', 'select': '*,related:topics!topic_relations_topic_id_a_fkey(id,slug,title)'})}"
        )
        return [*relations_a, *relations_b]

    def topic_open_questions(self, topic_id: str) -> list[dict]:
        query = urlencode({"topic_id": f"eq.{topic_id}", "select": "*", "order": "created_at.asc"})
        return self.get_table_rows(f"open_questions?{query}")

    def topic_contradictions(self, topic_id: str) -> list[dict]:
        select = (
            "*,"
            "signal_a:signals!contradictions_statement_a_source_signal_id_fkey(url,source:sources(name)),"
            "signal_b:signals!contradictions_statement_b_source_signal_id_fkey(url,source:sources(name))"
        )
        query = urlencode({"topic_id": f"eq.{topic_id}", "select": select, "order": "created_at.asc"})
        return self.get_table_rows(f"contradictions?{query}")

    def claims_for_source(self, source_key: str, limit: int = 100, offset: int = 0) -> tuple[list[dict], int | None]:
        source = self.get_source(source_key)
        if not source:
            return [], 0
        query = urlencode(
            {
                "select": "*,signal:signals!inner(published_at,url,source_id,source:sources(source_key,name)),topic:topics(slug,title)",
                "signal.source_id": f"eq.{source['id']}",
                "order": "created_at.desc",
                "limit": str(limit),
                "offset": str(offset),
            }
        )
        return self._get_with_count(f"claims?{query}")

    def topic_sources(self, topic_id: str) -> list[dict]:
        query = urlencode(
            {
                "select": "signal:signals(source:sources(source_key,name,type,trust_category,url))",
                "topic_id": f"eq.{topic_id}",
            }
        )
        rows = self.get_table_rows(f"topic_signals?{query}")
        seen: dict[str, dict] = {}
        for row in rows:
            source = (row.get("signal") or {}).get("source")
            if source and source.get("source_key") not in seen:
                seen[source["source_key"]] = source
        return list(seen.values())

    def topic_history(self, topic_id: str) -> list[dict]:
        """Synthesize a history feed from existing created_at timestamps.

        There is no dedicated audit-log/history table yet (that is Phase 5's
        lifecycle work). This assembles the closest honest equivalent from
        rows that already carry a created_at: claims, events, and facts added
        to this topic, plus corrections filed against any of those rows.
        """
        claims = self.get_table_rows(
            f"claims?{urlencode({'topic_id': f'eq.{topic_id}', 'select': 'id,claim_text,created_at'})}"
        )
        events = self.get_table_rows(
            f"events?{urlencode({'topic_id': f'eq.{topic_id}', 'select': 'id,description,created_at'})}"
        )
        facts = self.get_table_rows(
            f"verifiable_facts?{urlencode({'topic_id': f'eq.{topic_id}', 'select': 'id,fact_text,created_at'})}"
        )
        row_ids = [row["id"] for row in (*claims, *events, *facts)]
        corrections: list[dict] = []
        if row_ids:
            id_filter = ",".join(row_ids)
            corrections = self.get_table_rows(
                f"corrections?{urlencode({'target_row_id': f'in.({id_filter})', 'select': '*'})}"
            )

        entries: list[dict] = []
        for row in claims:
            entries.append({"type": "claim_added", "description": row["claim_text"], "timestamp": row["created_at"]})
        for row in events:
            entries.append({"type": "event_added", "description": row["description"], "timestamp": row["created_at"]})
        for row in facts:
            entries.append({"type": "fact_added", "description": row["fact_text"], "timestamp": row["created_at"]})
        for row in corrections:
            entries.append(
                {
                    "type": "correction_applied" if row["status"] == "fixed" else "correction_reported",
                    "description": row["issue_description"],
                    "timestamp": row["created_at"],
                }
            )
        entries.sort(key=lambda entry: entry["timestamp"], reverse=True)
        return entries

    def public_corrections(self, limit: int = 50, offset: int = 0) -> tuple[list[dict], int | None]:
        query = urlencode(
            {
                "select": "*",
                "order": "created_at.desc",
                "limit": str(limit),
                "offset": str(offset),
            }
        )
        return self._get_with_count(f"corrections?{query}")

    def topic_detail(self, topic_id: str) -> dict:
        query = urlencode(
            {
                "id": f"eq.{topic_id}",
                "select": f"id,slug,title,status,first_seen,last_signal_at,significance_score,summary,summary_generated_at,{_TOPIC_TAXONOMY_SELECT}",
            }
        )
        topic = self.get_table_rows(f"topics?{query}")
        return {
            "topic": topic[0] if topic else None,
            "claims": self.topic_claims(topic_id),
            "events": self.topic_events(topic_id),
            "verifiable_facts": self.topic_facts(topic_id),
            "relations": self.topic_relations_list(topic_id),
            "open_questions": self.topic_open_questions(topic_id),
            "contradictions": self.topic_contradictions(topic_id),
            "history": self.topic_history(topic_id),
        }

    def topic_detail_by_slug(self, slug: str) -> dict:
        topic = self.get_topic_by_slug(slug)
        if not topic:
            return {
                "topic": None,
                "claims": [],
                "events": [],
                "verifiable_facts": [],
                "relations": [],
                "open_questions": [],
                "contradictions": [],
                "history": [],
            }
        return self.topic_detail(topic["id"])

    def mark_signal_duplicate(self, duplicate_signal_id: str, canonical_signal_id: str) -> None:
        self._rpc(
            "mark_signal_duplicate",
            {
                "p_duplicate_signal_id": duplicate_signal_id,
                "p_canonical_signal_id": canonical_signal_id,
            },
        )

    def persist_topic_relation(self, topic_id_a: str, topic_id_b: str, relation_type: str) -> str | None:
        result = self._rpc(
            "upsert_topic_relation",
            {
                "p_topic_id_a": topic_id_a,
                "p_topic_id_b": topic_id_b,
                "p_relation_type": relation_type,
            },
        )
        return result if isinstance(result, str) else None

    def create_correction(self, target_table: str, target_row_id: str, issue_description: str) -> dict:
        rows = self._post(
            "corrections",
            {
                "target_table": target_table,
                "target_row_id": target_row_id,
                "issue_description": issue_description,
            },
            prefer="return=representation",
        )
        if not isinstance(rows, list) or not rows:
            raise RuntimeError("Correction report was not created")
        return rows[0]

    def persist_case_file_draft(self, draft: CaseFileDraft, signal_ids: list[str]) -> str:
        topic_id = self._rpc(
            "upsert_topic_cluster",
            {
                "p_title": draft.title,
                "p_signal_ids": signal_ids,
                "p_significance_score": draft.significance_score,
                "p_summary": draft.neutral_summary,
                "p_slug": draft.slug,
            },
        )
        if not topic_id:
            raise RuntimeError(f"Could not persist topic draft {draft.title}")
        for event in draft.events:
            self._rpc(
                "append_topic_event",
                {
                    "p_topic_id": topic_id,
                    "p_event_date": event.event_date,
                    "p_description": event.description,
                    "p_source_signal_ids": list(event.source_signal_ids),
                },
            )
        claim_id_by_signal_id: dict[str, str] = {}
        for claim in draft.claims:
            claim_id = self._rpc(
                "append_topic_claim",
                {
                    "p_topic_id": topic_id,
                    "p_claim_text": claim.claim_text,
                    "p_source_type": claim.source_type,
                    "p_source_signal_id": claim.source_signal_id,
                    "p_quoted_span": claim.quoted_span,
                },
            )
            if isinstance(claim_id, str):
                claim_id_by_signal_id[claim.source_signal_id] = claim_id
        for fact in draft.verifiable_facts:
            self._rpc(
                "append_topic_fact",
                {
                    "p_topic_id": topic_id,
                    "p_fact_text": fact.fact_text,
                    "p_primary_doc_url": fact.primary_doc_url,
                    "p_doc_type": fact.doc_type,
                    "p_quoted_span": fact.quoted_span,
                },
            )
        if draft.related_entities:
            self.link_topic_entities(topic_id, draft.related_entities)
        if draft.open_questions:
            self._persist_open_questions(topic_id, draft.open_questions, claim_id_by_signal_id)
        if draft.contradictions:
            self._persist_contradictions(topic_id, draft.contradictions)
        return topic_id

    def _persist_open_questions(self, topic_id: str, open_questions, claim_id_by_signal_id: dict[str, str]) -> None:
        payload = [
            {
                "topic_id": topic_id,
                "question": open_question.question,
                "related_claim_id": claim_id_by_signal_id.get(open_question.related_claim_source_signal_id),
            }
            for open_question in open_questions
        ]
        if payload:
            self._post("open_questions", payload, prefer="return=minimal")

    def _persist_contradictions(self, topic_id: str, contradictions) -> None:
        payload = [
            {
                "topic_id": topic_id,
                "entity_name": contradiction.entity_name,
                "statement_a_text": contradiction.statement_a_text,
                "statement_a_date": contradiction.statement_a_date,
                "statement_a_source_signal_id": contradiction.statement_a_source_signal_id,
                "statement_b_text": contradiction.statement_b_text,
                "statement_b_date": contradiction.statement_b_date,
                "statement_b_source_signal_id": contradiction.statement_b_source_signal_id,
            }
            for contradiction in contradictions
        ]
        if payload:
            self._post("contradictions", payload, prefer="return=minimal")

    def _rpc(self, function_name: str, payload: dict) -> object:
        """Call one trusted SQL RPC function using the service role."""
        request = Request(
            f"{self.url.rstrip('/')}/rest/v1/rpc/{function_name}",
            data=json.dumps(payload).encode("utf-8"),
            headers={"apikey": self.service_role_key, "Authorization": f"Bearer {self.service_role_key}", "Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(request, timeout=30) as response:  # noqa: S310 -- URL is deployment config.
            raw = response.read().decode("utf-8").strip()
            return json.loads(raw) if raw else None

    def _get(self, path: str) -> object:
        request = Request(
            f"{self.url.rstrip('/')}/rest/v1/{path}",
            headers={"apikey": self.service_role_key, "Authorization": f"Bearer {self.service_role_key}"},
            method="GET",
        )
        with urlopen(request, timeout=30) as response:  # noqa: S310 -- URL is deployment config.
            raw = response.read().decode("utf-8").strip()
            return json.loads(raw) if raw else None

    def _get_with_count(self, path: str) -> tuple[list[dict], int | None]:
        """Like _get, but also asks PostgREST for an exact total row count.

        Used for paginated list endpoints so the API can report `total`
        alongside `limit`/`offset` instead of leaving the frontend to guess
        whether a next page exists.
        """
        request = Request(
            f"{self.url.rstrip('/')}/rest/v1/{path}",
            headers={
                "apikey": self.service_role_key,
                "Authorization": f"Bearer {self.service_role_key}",
                "Prefer": "count=exact",
            },
            method="GET",
        )
        with urlopen(request, timeout=30) as response:  # noqa: S310 -- URL is deployment config.
            raw = response.read().decode("utf-8").strip()
            rows = json.loads(raw) if raw else []
            content_range = response.headers.get("Content-Range")
            total = None
            if content_range and "/" in content_range:
                total_part = content_range.rsplit("/", 1)[-1]
                total = int(total_part) if total_part.isdigit() else None
            return (rows if isinstance(rows, list) else [], total)

    def _patch(self, path: str, payload: dict) -> object:
        request = Request(
            f"{self.url.rstrip('/')}/rest/v1/{path}",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "apikey": self.service_role_key,
                "Authorization": f"Bearer {self.service_role_key}",
                "Content-Type": "application/json",
            },
            method="PATCH",
        )
        with urlopen(request, timeout=30) as response:  # noqa: S310 -- URL is deployment config.
            raw = response.read().decode("utf-8").strip()
            return json.loads(raw) if raw else None

    def _post(self, path: str, payload: dict, prefer: str | None = None) -> object:
        headers = {
            "apikey": self.service_role_key,
            "Authorization": f"Bearer {self.service_role_key}",
            "Content-Type": "application/json",
        }
        if prefer:
            headers["Prefer"] = prefer
        request = Request(
            f"{self.url.rstrip('/')}/rest/v1/{path}",
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urlopen(request, timeout=30) as response:  # noqa: S310 -- URL is deployment config.
            raw = response.read().decode("utf-8").strip()
            return json.loads(raw) if raw else None
