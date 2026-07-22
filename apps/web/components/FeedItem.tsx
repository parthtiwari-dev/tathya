"use client";

import Link from "next/link";
import type { TopicSummary } from "@/lib/types";
import { relativeTime } from "@/lib/format";
import { useLanguage, useTranslations } from "@/lib/i18n";

export function FeedItem({ topic }: { topic: TopicSummary }) {
  const t = useTranslations();
  const { lang } = useLanguage();
  const totalSources =
    topic.sourceCount.official + topic.sourceCount.media + topic.sourceCount.citizen;
  const sourcesWord = lang === "hi" ? "स्रोत" : totalSources === 1 ? "source" : "sources";

  return (
    <Link
      href={`/topic/${topic.slug}`}
      className="group block border-b border-border py-6 transition-colors first:pt-0"
    >
      <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-ink-muted">
        <StatusBadge status={topic.status} />
        <span>{topic.ministry}</span>
        <span aria-hidden="true">·</span>
        <span>{relativeTime(topic.lastSignalAt)}</span>
      </div>

      <h2 className="mt-2 font-serif text-lg font-medium leading-snug text-ink transition-colors group-hover:text-accent sm:text-xl">
        {topic.title}
      </h2>

      <p className="mt-2 max-w-2xl text-[15px] leading-relaxed text-ink-secondary">
        {topic.summary}
      </p>

      <div className="mt-3 flex flex-wrap items-center gap-3">
        <span className="text-xs text-ink-muted">
          {totalSources} {sourcesWord}
          {" · "}
          {topic.sourceCount.official} {t("sourceOfficial")} / {topic.sourceCount.media} {t("sourceMedia")} / {topic.sourceCount.citizen} {t("sourceCitizen")}
        </span>
      </div>

      {topic.entityTags.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-2">
          {topic.entityTags.map((tag) => (
            <span key={tag} className="rounded-full border border-border px-2.5 py-0.5 text-xs text-ink-secondary">
              {tag}
            </span>
          ))}
        </div>
      )}
    </Link>
  );
}

function StatusBadge({ status }: { status: TopicSummary["status"] }) {
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