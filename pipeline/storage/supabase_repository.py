"""Small PostgREST client for the atomic signal/snapshot database function."""

import json
import os
from dataclasses import dataclass
from urllib.request import Request, urlopen

from dotenv import load_dotenv

from pipeline.processing.snapshotter import build_snapshot
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
