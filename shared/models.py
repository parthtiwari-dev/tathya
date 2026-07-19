"""Typed boundary models shared by watchers and later pipeline stages."""

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import AnyHttpUrl, BaseModel, Field


class SourceType(StrEnum):
    RSS = "rss"
    X = "x"
    YOUTUBE = "youtube"
    PIB = "pib"
    PARLIAMENT = "parliament"


class TrustCategory(StrEnum):
    OFFICIAL = "official"
    MEDIA = "media"
    CITIZEN = "citizen"
    FOREIGN = "foreign"


class SourceDefinition(BaseModel):
    """A configured source, never a manually selected story."""

    key: str = Field(pattern=r"^[a-z0-9-]+$")
    name: str
    type: SourceType
    url: AnyHttpUrl
    trust_category: TrustCategory
    enabled: bool = True


class IngestedSignal(BaseModel):
    """Raw source material before entity extraction or clustering."""

    source_key: str
    source_url: AnyHttpUrl
    canonical_url: AnyHttpUrl
    published_at: datetime
    raw_text: str = Field(min_length=1)
    title: str | None = None
    transcript: str | None = None


class SnapshotRecord(BaseModel):
    """An immutable capture linked to a signal after database persistence."""

    signal_id: UUID | None = None
    captured_at: datetime
    raw_content: str = Field(min_length=1)
    content_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
