"use client";

import Link from "next/link";
import type { Source, ClaimSourceType } from "@/lib/types";
import { relativeTime } from "@/lib/format";
import { useLanguage } from "@/lib/i18n";

type ClaimWithTopic = {
  id: string;
  claimText: string;
  sourceType: ClaimSourceType;
  publishedAt: string;
  topicSlug: string;
  topicTitle: string;
};

const t = {
  back: { en: "\u2190 All sources", hi: "\u2190 सभी स्रोत" },
  claimsHeading: { en: "Claims traced to this source", hi: "इस स्रोत से जुड़े दावे" },
  none: { en: "No claims from this source yet.", hi: "अभी इस स्रोत से कोई दावा नहीं है।" },
};

const trustLabel: Record<string, { en: string; hi: string }> = {
  official: { en: "official", hi: "सरकारी" },
  media: { en: "media", hi: "मीडिया" },
  citizen: { en: "citizen", hi: "नागरिक" },
  foreign: { en: "foreign", hi: "विदेशी" },
};

const sourceTypeLabel: Record<ClaimSourceType, { en: string; hi: string }> = {
  government: { en: "Government Says", hi: "सरकार का कहना है" },
  opposition: { en: "Opposition Says", hi: "विपक्ष का कहना है" },
  media: { en: "Independent Media Reports", hi: "स्वतंत्र मीडिया रिपोर्ट" },
  citizen: { en: "Citizens & Protesters Say", hi: "नागरिक और प्रदर्शनकारी कहते हैं" },
};

export function SourcePageBody({ source, claims }: { source: Source; claims: ClaimWithTopic[] }) {
  const { lang } = useLanguage();

  return (
    <div className="py-8 sm:py-10">
      <Link href="/sources" className="text-xs text-ink-muted hover:text-accent">
        {t.back[lang]}
      </Link>
      <h1 className="mt-2 font-serif text-2xl font-medium text-ink">{source.name}</h1>
      <p className="mt-1 text-sm text-ink-secondary">
        {trustLabel[source.trustCategory][lang]} · {source.type} ·{" "}
        <a
          href={source.url}
          target="_blank"
          rel="noopener noreferrer"
          className="underline-offset-2 hover:text-accent hover:underline"
        >
          {source.url}
        </a>
      </p>

      <h2 className="mt-8 text-xs font-medium uppercase tracking-wide text-ink-muted">
        {t.claimsHeading[lang]} ({claims.length})
      </h2>

      <ul className="mt-4 space-y-3">
        {claims.length === 0 ? (
          <p className="text-sm text-ink-muted">{t.none[lang]}</p>
        ) : (
          claims.map((claim) => (
            <li key={claim.id} className="rounded-lg border border-border p-3.5">
              <p className="text-xs text-ink-muted">
                <Link href={`/topic/${claim.topicSlug}`} className="hover:text-accent hover:underline">
                  {claim.topicTitle}
                </Link>
                {" · "}
                {sourceTypeLabel[claim.sourceType][lang]}
              </p>
              <p className="mt-1.5 text-sm leading-relaxed text-ink">{claim.claimText}</p>
              <p className="mt-1.5 text-xs text-ink-muted">{relativeTime(claim.publishedAt)}</p>
            </li>
          ))
        )}
      </ul>
    </div>
  );
}
