"use client";

import Link from "next/link";
import type { TopicSummary } from "@/lib/types";
import { relativeTime } from "@/lib/format";
import { useLanguage, useTranslations } from "@/lib/i18n";
import { accentColorFromLabel } from "@/lib/accentColor";

export type BentoTier = "hero" | "wide" | "compact";

const TIER_SPAN: Record<BentoTier, string> = {
  hero: "col-span-1 sm:col-span-2 lg:col-span-4",
  wide: "col-span-1 sm:col-span-2 lg:col-span-2",
  compact: "col-span-1",
};

export function BentoCard({
  topic,
  tier,
  index,
  revealed,
}: {
  topic: TopicSummary;
  tier: BentoTier;
  index: number;
  revealed: boolean;
}) {
  const t = useTranslations();
  const { lang } = useLanguage();
  const totalSources = topic.sourceCount.official + topic.sourceCount.media + topic.sourceCount.citizen;
  const sourcesWord = lang === "hi" ? "स्रोत" : totalSources === 1 ? "source" : "sources";
  const accent = accentColorFromLabel(topic.entityTags[0] || topic.ministry);

  return (
    <Link
      href={`/topic/${topic.slug}`}
      className={`reveal-card group relative flex flex-col overflow-hidden rounded-2xl border border-border bg-surface/40 transition-colors hover:border-ink-muted ${TIER_SPAN[tier]} ${
        tier === "hero" ? "p-6 sm:p-8" : tier === "wide" ? "p-5" : "p-4"
      } ${revealed ? "is-revealed" : ""}`}
      style={{ animationDelay: `${Math.min(index, 10) * 70}ms` }}
    >
      <span className="absolute inset-x-0 top-0 h-[3px]" style={{ backgroundColor: accent }} aria-hidden="true" />

      <div className="flex flex-wrap items-center gap-x-2.5 gap-y-1 text-xs text-ink-muted">
        <StatusBadge status={topic.status} />
        <span className="truncate">{topic.ministry}</span>
        <span aria-hidden="true">·</span>
        <span className="whitespace-nowrap">{relativeTime(topic.lastSignalAt)}</span>
      </div>

      <h2
        className={`mt-2.5 font-serif font-medium leading-snug text-ink transition-colors group-hover:text-accent ${
          tier === "hero" ? "text-2xl sm:text-3xl" : tier === "wide" ? "text-lg sm:text-xl" : "text-base"
        }`}
      >
        {topic.title}
      </h2>

      {tier !== "compact" && (
        <p
          className={`mt-2 text-ink-secondary ${
            tier === "hero" ? "max-w-3xl text-[15px] leading-relaxed" : "text-sm leading-relaxed line-clamp-2"
          }`}
        >
          {topic.summary}
        </p>
      )}

      <div className="mt-auto pt-3">
        <div className="flex flex-wrap items-center gap-2 text-xs text-ink-muted">
          <span>
            {totalSources} {sourcesWord}
            {tier === "hero" && (
              <>
                {" · "}
                {topic.sourceCount.official} {t("sourceOfficial")} / {topic.sourceCount.media} {t("sourceMedia")} /{" "}
                {topic.sourceCount.citizen} {t("sourceCitizen")}
              </>
            )}
          </span>
        </div>

        {tier !== "compact" && topic.entityTags.length > 0 && (
          <div className="mt-2.5 flex flex-wrap gap-1.5">
            {topic.entityTags.slice(0, tier === "hero" ? 6 : 3).map((tag) => (
              <span key={tag} className="rounded-full border border-border px-2 py-0.5 text-[11px] text-ink-secondary">
                {tag}
              </span>
            ))}
            {tier === "wide" && topic.entityTags.length > 3 && (
              <span className="px-1 text-[11px] text-ink-muted">+{topic.entityTags.length - 3}</span>
            )}
          </div>
        )}
      </div>
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
