"use client";

import { useMemo, useState } from "react";
import { getAllTopics } from "@/lib/mock-data";
import { FeedItem } from "@/components/FeedItem";

// NOTE: this is client-side substring matching over mock data as a placeholder.
// The roadmap specifies pgvector semantic search (GET /signals/search) as the
// real backend — swap the filter below for a fetch to that endpoint once
// API v1 exists, no change needed to the rendering below it.
export default function SearchPage() {
  const [query, setQuery] = useState("");
  const topics = useMemo(() => getAllTopics(), []);

  const results = useMemo(() => {
    if (!query.trim()) return topics;
    const q = query.toLowerCase();
    return topics.filter(
      (topic) =>
        topic.title.toLowerCase().includes(q) ||
        topic.summary.toLowerCase().includes(q) ||
        topic.entityTags.some((tag) => tag.toLowerCase().includes(q)) ||
        topic.ministry.toLowerCase().includes(q),
    );
  }, [query, topics]);

  return (
    <div className="py-10">
      <h1 className="font-serif text-2xl font-medium text-ink">Search</h1>
      <p className="mt-1 text-sm text-ink-secondary">
        Search topics, people, ministries, and entities across the record.
      </p>

      <input
        autoFocus
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Try “Parliament”, “Railways”, “NEET”…"
        className="mt-6 w-full max-w-lg rounded-full border border-border bg-surface px-4 py-2.5 text-sm text-ink outline-none focus:border-accent/50"
      />

      <div className="mt-8">
        {results.length === 0 ? (
          <p className="text-sm text-ink-muted">No topics match that search yet.</p>
        ) : (
          results.map((topic) => <FeedItem key={topic.id} topic={topic} />)
        )}
      </div>
    </div>
  );
}
