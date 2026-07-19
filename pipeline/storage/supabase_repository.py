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

    def list_topics(self, limit: int = 20) -> list[dict]:
        query = urlencode(
            {
                "select": "id,title,status,first_seen,last_signal_at,significance_score,summary,summary_generated_at",
                "order": "last_signal_at.desc",
                "limit": str(limit),
            }
        )
        return self.get_table_rows(f"topics?{query}")

    def topic_detail(self, topic_id: str) -> dict:
        topic = self.get_table_rows(f"topics?{urlencode({'id': f'eq.{topic_id}', 'select': '*'})}")
        claims = self.get_table_rows(
            f"claims?{urlencode({'topic_id': f'eq.{topic_id}', 'select': '*', 'order': 'created_at.asc'})}"
        )
        events = self.get_table_rows(
            f"events?{urlencode({'topic_id': f'eq.{topic_id}', 'select': '*', 'order': 'event_date.asc'})}"
        )
        facts = self.get_table_rows(
            f"verifiable_facts?{urlencode({'topic_id': f'eq.{topic_id}', 'select': '*', 'order': 'created_at.asc'})}"
        )
        relations_a = self.get_table_rows(
            f"topic_relations?{urlencode({'topic_id_a': f'eq.{topic_id}', 'select': '*'})}"
        )
        relations_b = self.get_table_rows(
            f"topic_relations?{urlencode({'topic_id_b': f'eq.{topic_id}', 'select': '*'})}"
        )
        return {
            "topic": topic[0] if topic else None,
            "claims": claims,
            "events": events,
            "verifiable_facts": facts,
            "relations": [*relations_a, *relations_b],
        }

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
        for claim in draft.claims:
            self._rpc(
                "append_topic_claim",
                {
                    "p_topic_id": topic_id,
                    "p_claim_text": claim.claim_text,
                    "p_source_type": claim.source_type,
                    "p_source_signal_id": claim.source_signal_id,
                    "p_quoted_span": claim.quoted_span,
                },
            )
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
        return topic_id

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
