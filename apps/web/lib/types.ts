export type TopicStatus = "raw_cluster" | "live" | "archived";

export type ClaimSourceType = "government" | "media" | "citizen" | "opposition";

export type TrustCategory = "official" | "media" | "citizen" | "foreign";

export type FactDocType = "gazette" | "parliament_qa" | "pib" | "dataset";

export type RelationType =
  | "related"
  | "escalated_from"
  | "referenced_in"
  | "same_policy_area";

export type HistoryEntryType =
  | "claim_added"
  | "event_added"
  | "fact_added"
  | "correction_reported"
  | "correction_applied"
  | "status_changed";

export interface Claim {
  id: string;
  claimText: string;
  sourceType: ClaimSourceType;
  quotedSpan: string;
  sourceName: string;
  sourceUrl: string;
  sourceKey: string;
  publishedAt: string;
}

export interface OpenQuestion {
  id: string;
  question: string;
  relatedClaimId: string;
}

export interface Contradiction {
  id: string;
  entity: string;
  statementA: { text: string; date: string; sourceName: string; sourceUrl: string };
  statementB: { text: string; date: string; sourceName: string; sourceUrl: string };
}

export interface Source {
  sourceKey: string;
  name: string;
  type: string;
  trustCategory: TrustCategory;
  url: string;
  enabled: boolean;
}

export interface TimelineEvent {
  id: string;
  eventDate: string;
  description: string;
  sourceSignalIds: string[];
}

export interface VerifiableFact {
  id: string;
  factText: string;
  primaryDocUrl: string;
  docType: FactDocType;
  quotedSpan: string;
}

export interface TopicRelation {
  id: string;
  relatedTopicSlug: string;
  relatedTopicTitle: string;
  relationType: RelationType;
}

export interface HistoryEntry {
  id: string;
  type: HistoryEntryType;
  description: string;
  timestamp: string;
}

export interface SourceCount {
  official: number;
  media: number;
  citizen: number;
}

export interface Topic {
  id: string;
  slug: string;
  title: string;
  summary: string;
  status: TopicStatus;
  ministry: string;
  ministrySlug: string;
  entityTags: string[];
  firstSeen: string;
  lastSignalAt: string;
  sourceCount: SourceCount;
  claims: Claim[];
  events: TimelineEvent[];
  facts: VerifiableFact[];
  relations: TopicRelation[];
  history: HistoryEntry[];
  openQuestions: OpenQuestion[];
  contradictions: Contradiction[];
}

export interface TopicSummary {
  id: string;
  slug: string;
  title: string;
  summary: string;
  status: TopicStatus;
  ministry: string;
  ministrySlug: string;
  entityTags: string[];
  lastSignalAt: string;
  sourceCount: SourceCount;
}
