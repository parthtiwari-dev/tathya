"use client";

import { useMemo, useState } from "react";
import { getAllTopics } from "@/lib/mock-data";
import { FeedItem } from "@/components/FeedItem";
import { useLanguage } from "@/lib/i18n";

const t = {
  heading: { en: "Search", hi: "खोजें" },
  subtitle: {
    en: "Search topics, people, ministries, and entities across the record.",
    hi: "अभिलेख में विषय, लोग, मंत्रालय और संस्थाएं खोजें।",
  },
  placeholder: { en: "Try \u201cParliament\u201d, \u201cRailways\u201d, \u201cNEET\u201d\u2026", hi: "\u201cसंसद\u201d, \u201cरेलवे\u201d, \u201cNEET\u201d आज़माएं\u2026" },
  noMatch: { en: "No topics match that search yet.", hi: "अभी कोई विषय इस खोज से मेल नहीं खाता।" },
};

// NOTE: this is client-side substring matching over mock data as a placeholder.
// The roadmap specifies pgvector semantic search (GET /signals/search) as the
// real backend — swap the filter below for a fetch to that endpoint once
// API v1 exists, no change needed to the rendering below it.
export default function SearchPage() {
  const { lang } = useLanguage();
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
    <div className="py-8 sm:py-10">
      <h1 className="font-serif text-2xl font-medium text-ink">{t.heading[lang]}</h1>
      <p className="mt-1 text-sm text-ink-secondary">{t.subtitle[lang]}</p>

      <input
        autoFocus
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder={t.placeholder[lang]}
        className="mt-6 w-full max-w-lg rounded-full border border-border bg-surface px-4 py-2.5 text-sm text-ink outline-none focus:border-accent/50"
      />

      <div className="mt-8">
        {results.length === 0 ? (
          <p className="text-sm text-ink-muted">{t.noMatch[lang]}</p>
        ) : (
          results.map((topic) => <FeedItem key={topic.id} topic={topic} />)
        )}
      </div>
    </div>
  );
}
