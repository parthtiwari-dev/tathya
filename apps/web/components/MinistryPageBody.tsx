"use client";

import Link from "next/link";
import type { TopicSummary } from "@/lib/types";
import { FeedItem } from "@/components/FeedItem";
import { useLanguage } from "@/lib/i18n";

const t = {
  back: { en: "\u2190 All topics", hi: "\u2190 सभी विषय" },
  tracked: { en: "topic(s) tracked under this ministry.", hi: "विषय इस मंत्रालय के अंतर्गत ट्रैक किए गए।" },
  none: {
    en: "No live topics for this ministry right now.",
    hi: "अभी इस मंत्रालय के लिए कोई सक्रिय विषय नहीं है।",
  },
};

export function MinistryPageBody({ name, topics }: { name: string; topics: TopicSummary[] }) {
  const { lang } = useLanguage();

  return (
    <div className="py-8 sm:py-10">
      <Link href="/" className="text-xs text-ink-muted hover:text-accent">
        {t.back[lang]}
      </Link>
      <h1 className="mt-2 font-serif text-2xl font-medium text-ink">{name}</h1>
      <p className="mt-1 text-sm text-ink-secondary">
        {topics.length} {t.tracked[lang]}
      </p>

      <div className="mt-8">
        {topics.length === 0 ? (
          <p className="text-sm text-ink-muted">{t.none[lang]}</p>
        ) : (
          topics.map((topic) => <FeedItem key={topic.id} topic={topic} />)
        )}
      </div>
    </div>
  );
}
