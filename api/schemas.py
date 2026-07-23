"""Pydantic response models for API v1.

Field names are camelCase to match the frontend's lib/types.ts exactly --
that TypeScript contract was locked first (against mock data), so this API
is built to match it, not the other way around.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    items: list[T]
    limit: int
    offset: int
    total: Optional[int] = None


class SourceCount(BaseModel):
    official: int = 0
    media: int = 0
    citizen: int = 0


class TopicSummary(BaseModel):
    id: str
    slug: str
    title: str
    summary: Optional[str] = None
    status: str
    ministry: str
    ministrySlug: str
    entityTags: list[str] = []
    firstSeen: Optional[datetime] = None
    lastSignalAt: Optional[datetime] = None
    significanceScore: float = 0
    sourceCount: SourceCount = SourceCount()


class Claim(BaseModel):
    id: str
    claimText: str
    sourceType: str
    sourceSignalId: str
    quotedSpan: str
    createdAt: Optional[datetime] = None
    sourceName: Optional[str] = None
    sourceUrl: Optional[str] = None
    sourceKey: Optional[str] = None
    publishedAt: Optional[datetime] = None
    # Populated only by /sources/{key}/claims, where a claim is shown out of
    # topic context and needs to link back to its topic.
    topicSlug: Optional[str] = None
    topicTitle: Optional[str] = None


class TimelineEvent(BaseModel):
    id: str
    eventDate: date
    description: str
    sourceSignalIds: list[str] = []


class VerifiableFact(BaseModel):
    id: str
    factText: str
    primaryDocUrl: str
    docType: str
    quotedSpan: str
    createdAt: Optional[datetime] = None


class TopicRelation(BaseModel):
    id: str
    relatedTopicId: str
    relatedTopicSlug: Optional[str] = None
    relatedTopicTitle: Optional[str] = None
    relationType: str


class HistoryEntry(BaseModel):
    id: str
    type: str
    description: str
    timestamp: datetime


class OpenQuestion(BaseModel):
    id: str
    question: str
    relatedClaimId: Optional[str] = None


class ContradictionStatement(BaseModel):
    text: str
    date: date
    sourceName: str
    sourceUrl: str


class Contradiction(BaseModel):
    id: str
    entity: str
    statementA: ContradictionStatement
    statementB: ContradictionStatement


class TopicDetail(BaseModel):
    """Full nested topic, matching lib/types.ts' Topic interface exactly."""

    id: str
    slug: str
    title: str
    summary: Optional[str] = None
    status: str
    ministry: str
    ministrySlug: str
    entityTags: list[str] = []
    firstSeen: Optional[datetime] = None
    lastSignalAt: Optional[datetime] = None
    sourceCount: SourceCount = SourceCount()
    claims: list[Claim] = []
    events: list[TimelineEvent] = []
    facts: list[VerifiableFact] = []
    relations: list[TopicRelation] = []
    history: list[HistoryEntry] = []
    openQuestions: list[OpenQuestion] = []
    contradictions: list[Contradiction] = []


class Ministry(BaseModel):
    slug: str
    name: str


class Source(BaseModel):
    sourceKey: str
    name: str
    type: str
    trustCategory: str
    url: str
    enabled: bool


class SignalSummary(BaseModel):
    id: str
    publishedAt: datetime
    title: Optional[str] = None
    url: str
    isDuplicate: bool = False


class SourceRun(BaseModel):
    id: str
    sourceKey: Optional[str] = None
    sourceName: Optional[str] = None
    collectedAt: datetime
    signalCount: int
    status: str
    detail: Optional[str] = None


class Correction(BaseModel):
    id: str
    targetTable: str
    targetRowId: str
    issueDescription: str
    status: str
    createdAt: datetime
    resolvedAt: Optional[datetime] = None
