"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { Search, X } from "lucide-react";
import { getAllTopics } from "@/lib/api";
import type { TopicSummary } from "@/lib/types";
import { useLanguage, dict } from "@/lib/i18n";

export function CommandPalette() {
  const router = useRouter();
  const { lang } = useLanguage();
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [topics, setTopics] = useState<TopicSummary[]>([]);

  useEffect(() => {
    getAllTopics()
      .then(setTopics)
      .catch(() => setTopics([]));
  }, []);

  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      const isModK = (e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k";
      if (isModK) {
        e.preventDefault();
        setOpen((v) => !v);
        return;
      }
      if (e.key === "Escape") setOpen(false);
    }
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  useEffect(() => {
    if (!open) setQuery("");
  }, [open]);

  const results = useMemo(() => {
    if (!query.trim()) return topics.slice(0, 6);
    const q = query.toLowerCase();
    return topics
      .filter(
        (topic) =>
          topic.title.toLowerCase().includes(q) ||
          topic.summary.toLowerCase().includes(q) ||
          topic.entityTags.some((tag) => tag.toLowerCase().includes(q)) ||
          topic.ministry.toLowerCase().includes(q),
      )
      .slice(0, 8);
  }, [query, topics]);

  if (!open) return null;

  function goTo(slug: string) {
    setOpen(false);
    router.push(`/topic/${slug}`);
  }

  return (
    <div
      className="fixed inset-0 z-[60] flex items-start justify-center bg-black/30 pt-24"
      onClick={() => setOpen(false)}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        className="w-full max-w-lg overflow-hidden rounded-xl border border-border bg-paper shadow-2xl"
      >
        <div className="flex items-center gap-2 border-b border-border px-4 py-3">
          <Search size={16} className="text-ink-muted" />
          <input
            autoFocus
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={dict.searchPlaceholder[lang]}
            className="flex-1 bg-transparent text-sm text-ink outline-none placeholder:text-ink-muted"
          />
          <button onClick={() => setOpen(false)} aria-label="Close" className="text-ink-muted hover:text-ink">
            <X size={16} />
          </button>
        </div>

        <div className="max-h-80 overflow-y-auto p-2">
          {results.length === 0 ? (
            <p className="px-3 py-6 text-center text-sm text-ink-muted">{dict.noTopicsMatch[lang]}</p>
          ) : (
            results.map((topic) => (
              <button
                key={topic.id}
                onClick={() => goTo(topic.slug)}
                className="block w-full rounded-lg px-3 py-2.5 text-left transition-colors hover:bg-surface"
              >
                <p className="text-sm font-medium text-ink">{topic.title}</p>
                <p className="mt-0.5 text-xs text-ink-muted">{topic.ministry}</p>
              </button>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
