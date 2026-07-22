"use client";

import type { Topic } from "@/lib/types";
import { useLanguage } from "@/lib/i18n";
import { relativeTime } from "@/lib/format";
import { TrustBreakdown } from "@/components/TrustBreakdown";
import { Timeline } from "@/components/Timeline";
import { ClaimsLedger } from "@/components/ClaimsLedger";
import { Contradictions } from "@/components/Contradictions";
import { VerifiableFactsPanel } from "@/components/VerifiableFactsPanel";
import { OpenQuestions } from "@/components/OpenQuestions";
import { RelatedTopics } from "@/components/RelatedTopics";
import { SourcesUsed } from "@/components/SourcesUsed";
import { TopicHistory } from "@/components/TopicHistory";

const statusText = {
  live: { en: "Live", hi: "सक्रिय" },
  archived: { en: "Archived", hi: "संग्रहीत" },
  raw_cluster: { en: "Draft", hi: "मसौदा" },
};

const contentNoticeText = {
  en: "This topic's content (summary, claims, quotes) is only available in English right now. Hindi case-file generation is a later phase.",
  hi: "इस विषय की सामग्री (सारांश, दावे, उद्धरण) अभी केवल अंग्रेज़ी में उपलब्ध है। हिंदी केस-फ़ाइल जनरेशन बाद के चरण में आएगी।",
};

const updatedText = { en: "updated", hi: "अद्यतन" };

export function TopicPageBody({ topic }: { topic: Topic }) {
  const { lang } = useLanguage();

  return (
    <article className="max-w-3xl py-8 sm:py-10">
      <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-ink-muted">
        <StatusLabel status={topic.status} lang={lang} />
        <span>{topic.ministry}</span>
        <span aria-hidden="true">·</span>
        <span>{updatedText[lang]} {relativeTime(topic.lastSignalAt)}</span>
      </div>

      <h1 className="mt-2 font-serif text-2xl font-medium leading-tight text-ink sm:text-3xl">
        {topic.title}
      </h1>

      <p className="mt-4 text-[16px] leading-relaxed text-ink-secondary sm:text-[17px]">{topic.summary}</p>

      {lang === "hi" && (
        <p className="mt-3 rounded-md border border-dashed border-border bg-surface p-3 text-xs text-ink-muted">
          {contentNoticeText.hi}
        </p>
      )}

      <div className="mt-3">
        <TrustBreakdown counts={topic.sourceCount} lang={lang} />
      </div>

      <div className="mt-10 space-y-10">
        <Timeline events={topic.events} lang={lang} />
        <ClaimsLedger claims={topic.claims} lang={lang} />
        <Contradictions items={topic.contradictions} lang={lang} />
        <VerifiableFactsPanel facts={topic.facts} lang={lang} />
        <OpenQuestions questions={topic.openQuestions} lang={lang} />
        <RelatedTopics relations={topic.relations} lang={lang} />
        <SourcesUsed claims={topic.claims} lang={lang} />
        <TopicHistory history={topic.history} lang={lang} />
      </div>
    </article>
  );
}

function StatusLabel({ status, lang }: { status: Topic["status"]; lang: "en" | "hi" }) {
  if (status === "live") {
    return (
      <span className="inline-flex items-center gap-1.5 font-medium text-accent">
        <span className="h-1.5 w-1.5 rounded-full bg-accent" />
        {statusText.live[lang]}
      </span>
    );
  }
  if (status === "archived") {
    return <span className="font-medium text-ink-muted">{statusText.archived[lang]}</span>;
  }
  return <span className="font-medium text-ink-muted">{statusText.raw_cluster[lang]}</span>;
}