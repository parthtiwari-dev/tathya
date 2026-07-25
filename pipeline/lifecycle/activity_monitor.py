"""Detects live topics that have gone stale (roadmap Section 3, Layer 6).

Pure detection, no mutation -- status_manager.py applies the actual archive
transition using what this returns, so the "what's stale" question and the
"do something about it" question stay independently testable.
"""

from datetime import UTC, datetime, timedelta

from pipeline.storage.supabase_repository import SupabaseRepository
from shared.config import ARCHIVE_AFTER_DAYS


def find_stale_live_topics(
    repository: SupabaseRepository, archive_after_days: int = ARCHIVE_AFTER_DAYS
) -> list[dict]:
    """Live topics with no signal in the last `archive_after_days` days."""
    cutoff = datetime.now(UTC) - timedelta(days=archive_after_days)
    return repository.stale_live_topics(cutoff.isoformat())
