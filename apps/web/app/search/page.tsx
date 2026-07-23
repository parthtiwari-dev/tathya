"use client";

import { useEffect, useState } from "react";
import { ExternalLink } from "lucide-react";
import { searchSignals, type SignalSearchResult } from "@/lib/api";
import { useLanguage } from "@/lib/i18n";

const t = {
  heading: { en: "Search", hi: "खोजें" },
  subtitle: {
    en: "Semantic search over everything Tathya has ingested -- articles, releases, and other signals, not just topics.",
    hi: "तथ्य द्वारा एकत्र हर चीज़ पर अर्थ-आधारित खोज -- लेख, विज्ञप्तियां और अन्य सिग्नल, केवल विषय नहीं।",
  },
  placeholder: { en: "Try \u201cParliament\u201d, \u201cRailways\u201d, \u201cNEET\u201d\u2026", hi: "\u201cसंसद\u201d, \u201cरेलवे\u201d, \u201cNEET\u201d आज़माएं\u2026" },
  noMatch: { en: "No signals match that search yet.", hi: "अभी कोई सिग्नल इस खोज से मेल नहीं खाता।" },
  searching: { en: "Searching…", hi: "खोज जारी है…" },
  prompt: { en: "Start typing to search the record.", hi: "अभिलेख खोजने के लिए टाइप करना शुरू करें।" },
};

const trustLabel: Record<string, { en: string; hi: string }> = {
  official: { en: "Official", hi: "सरकारी" },
  media: { en: "Media", hi: "मीडिया" },
  citizen: { en: "Citizen", hi: "नागरिक" },
  foreign: { en: "Foreign", hi: "विदेशी" },
};

export default function SearchPage() {
  const { lang } = useLanguage();
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SignalSearchResult[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!query.trim()) {
      setResults([]);
      return;
    }
    setLoading(true);
    const handle = setTimeout(() => {
      searchSignals(query)
        .then(setResults)
        .catch(() => setResults([]))
        .finally(() => setLoading(false));
    }, 300);
    return () => clearTimeout(handle);
  }, [query]);

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
        {!query.trim() ? (
          <p className="text-sm text-ink-muted">{t.prompt[lang]}</p>
        ) : loading ? (
          <p className="text-sm text-ink-muted">{t.searching[lang]}</p>
        ) : results.length === 0 ? (
          <p className="text-sm text-ink-muted">{t.noMatch[lang]}</p>
        ) : (
          <div className="divide-y divide-border border-y border-border">
            {results.map((signal) => (
              <a
                key={signal.id}
                href={signal.url}
                target="_blank"
                rel="noopener noreferrer"
                className="block py-3.5 transition-colors hover:bg-surface"
              >
                <div className="flex items-start justify-between gap-4">
                  <p className="text-sm font-medium text-ink">{signal.title || signal.url}</p>
                  <ExternalLink size={13} className="mt-0.5 shrink-0 text-ink-muted" />
                </div>
                <p className="mt-1 line-clamp-2 text-xs text-ink-secondary">{signal.raw_text}</p>
                <p className="mt-1.5 text-xs text-ink-muted">
                  {trustLabel[signal.trust_category]?.[lang] ?? signal.trust_category} · {signal.source_key} ·{" "}
                  {new Date(signal.published_at).toLocaleDateString(lang === "hi" ? "hi-IN" : "en-IN")}
                </p>
              </a>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
