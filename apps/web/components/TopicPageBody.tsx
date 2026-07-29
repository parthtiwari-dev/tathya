"use client";

import type { Topic } from "@/lib/types";
import { useLanguage, useTranslations } from "@/lib/i18n";
import { relativeTime } from "@/lib/format";
import { localizedText } from "@/lib/localizedText";
import { TrustBreakdown } from "@/components/TrustBreakdown";
import { Timeline } from "@/components/Timeline";
import { ClaimsLedger } from "@/components/ClaimsLedger";
import { Contradictions } from "@/components/Contradictions";
import { VerifiableFactsPanel } from "@/components/VerifiableFactsPanel";
import { OpenQuestions } from "@/components/OpenQuestions";
import { RelatedTopics } from "@/components/RelatedTopics";
import { SourcesUsed } from "@/components/SourcesUsed";
import { TopicHistory } from "@/components/TopicHistory";

const updatedText = { en: "updated", hi: "अद्यतन" };

export function TopicPageBody({ topic }: { topic: Topic }) {
  const { lang } = useLanguage();
  const t = useTranslations();
  const title = localizedText(topic.title, topic.titleHi, lang);
  const summary = localizedText(topic.summary, topic.summaryHi, lang);

  return (
    <article className="max-w-3xl py-8 sm:py-10">
      <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-ink-muted">
        <StatusLabel status={topic.status} />
        <span>{topic.ministry}</span>
        <span aria-hidden="true">·</span>
        <span>{updatedText[lang]} {relativeTime(topic.lastSignalAt)}</span>
      </div>

      <h1 className="mt-2 font-serif text-2xl font-medium leading-tight text-ink sm:text-3xl">
        {title.text}
        {title.isFallback && (
          <span className="ml-2 align-middle text-xs font-sans font-normal uppercase tracking-wide text-ink-muted" title={t("titleNotTranslatedYet")}>
            EN
          </span>
        )}
      </h1>

      <p className="mt-4 text-[16px] leading-relaxed text-ink-secondary sm:text-[17px]">{summary.text}</p>

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

function StatusLabel({ status }: { status: Topic["status"] }) {
  const t = useTranslations();
  if (status === "live") {
    return (
      <span className="inline-flex items-center gap-1.5 font-medium text-accent">
        <span className="h-1.5 w-1.5 rounded-full bg-accent" />
        {t("statusLive")}
      </span>
    );
  }
  if (status === "archived") {
    return <span className="font-medium text-ink-muted">{t("statusArchived")}</span>;
  }
  return <span className="font-medium text-ink-muted">{t("statusDraft")}</span>;
}