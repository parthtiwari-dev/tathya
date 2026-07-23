import type { Claim, Ministry, Source, Topic, TopicSummary } from "./types";

// Real API v1 client. Replaces lib/mock-data.ts and lib/mock-sources.ts.
// Server Components call these directly; client components that need topic
// data (CommandPalette, the search page) fetch through the same base URL
// from the browser, so this must stay usable on both sides.
const API_BASE = process.env.NEXT_PUBLIC_TATHYA_API_URL ?? "http://localhost:8000";

interface Page<T> {
  items: T[];
  limit: number;
  offset: number;
  total: number | null;
}

async function apiFetch<T>(path: string): Promise<T> {
  // No caching for now -- Next 16 doesn't cache fetch() by default anyway,
  // and the dataset is small enough that always-fresh is simpler than
  // engineering revalidation this pass (see roadmap: P0 is correctness).
  const res = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`Tathya API ${path} failed: ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export async function getAllTopics(): Promise<TopicSummary[]> {
  const page = await apiFetch<Page<TopicSummary>>("/topics?limit=100");
  return page.items;
}

export async function getTopicBySlug(slug: string): Promise<Topic | undefined> {
  try {
    return await apiFetch<Topic>(`/topics/slug/${encodeURIComponent(slug)}`);
  } catch {
    // Covers both "not found" and a genuine fetch failure -- either way the
    // page should render notFound() rather than throw during render.
    return undefined;
  }
}

export async function getAllMinistries(): Promise<Ministry[]> {
  return apiFetch<Ministry[]>("/ministries");
}

export async function getTopicsByMinistry(ministrySlug: string): Promise<TopicSummary[]> {
  const page = await apiFetch<Page<TopicSummary>>(
    `/topics?limit=100&ministry_slug=${encodeURIComponent(ministrySlug)}`,
  );
  return page.items;
}

export async function getAllSources(): Promise<Source[]> {
  return apiFetch<Source[]>("/sources");
}

export async function getSourceByKey(sourceKey: string): Promise<Source | undefined> {
  try {
    return await apiFetch<Source>(`/sources/${encodeURIComponent(sourceKey)}`);
  } catch {
    return undefined;
  }
}

export type SourceClaim = Claim & { topicSlug: string; topicTitle: string };

export async function getClaimsBySourceKey(sourceKey: string): Promise<SourceClaim[]> {
  const page = await apiFetch<Page<SourceClaim>>(`/sources/${encodeURIComponent(sourceKey)}/claims?limit=100`);
  return page.items;
}

// GET /signals/search does pgvector semantic search over individual signals
// (not topics) -- this is signal-level, matching what the endpoint actually
// returns. See components/SearchResults.tsx for the rendering side.
export interface SignalSearchResult {
  id: string;
  published_at: string;
  title: string | null;
  raw_text: string;
  url: string;
  source_key: string;
  trust_category: "official" | "media" | "citizen" | "foreign";
  similarity: number;
}

export async function searchSignals(query: string): Promise<SignalSearchResult[]> {
  if (!query.trim()) return [];
  const data = await apiFetch<{ query: string; results: SignalSearchResult[] }>(
    `/signals/search?q=${encodeURIComponent(query)}&limit=20`,
  );
  return data.results;
}

export async function submitCorrection(input: {
  targetTable: "claims" | "events" | "verifiable_facts";
  targetRowId: string;
  issueDescription: string;
}): Promise<void> {
  const res = await fetch(`${API_BASE}/corrections`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      target_table: input.targetTable,
      target_row_id: input.targetRowId,
      issue_description: input.issueDescription,
    }),
  });
  if (!res.ok) {
    throw new Error(`Failed to submit correction: ${res.status}`);
  }
}
