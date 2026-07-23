"use client";

import Link from "next/link";
import type { Source } from "@/lib/types";
import { useLanguage } from "@/lib/i18n";

const t = {
  heading: { en: "Source Explorer", hi: "स्रोत एक्सप्लोरर" },
  subtitle: {
    en: "The fixed list of sources Tathya watches. Enabled sources are actively ingested; the rest are configured but not yet live.",
    hi: "स्रोतों की निश्चित सूची जिन्हें तथ्य देखता है। सक्षम स्रोत सक्रिय रूप से इनजेस्ट किए जाते हैं; बाकी कॉन्फ़िगर हैं पर अभी सक्रिय नहीं।",
  },
  enabled: { en: "Enabled", hi: "सक्षम" },
  configured: { en: "Configured", hi: "कॉन्फ़िगर किया गया" },
};

const trustLabel: Record<string, { en: string; hi: string }> = {
  official: { en: "Official", hi: "सरकारी" },
  media: { en: "Media", hi: "मीडिया" },
  citizen: { en: "Citizen", hi: "नागरिक" },
  foreign: { en: "Foreign", hi: "विदेशी" },
};

export function SourcesIndexBody({ sources }: { sources: Source[] }) {
  const { lang } = useLanguage();

  return (
    <div className="py-8 sm:py-10">
      <h1 className="font-serif text-2xl font-medium text-ink">{t.heading[lang]}</h1>
      <p className="mt-1 text-sm text-ink-secondary">{t.subtitle[lang]}</p>

      <div className="mt-8 divide-y divide-border border-y border-border">
        {sources.map((source) => (
          <Link
            key={source.sourceKey}
            href={`/source/${source.sourceKey}`}
            className="flex items-center justify-between gap-4 py-3.5 transition-colors hover:bg-surface"
          >
            <div>
              <p className="text-sm font-medium text-ink">{source.name}</p>
              <p className="text-xs text-ink-muted">
                {trustLabel[source.trustCategory][lang]} · {source.type}
              </p>
            </div>
            <span
              className={`shrink-0 rounded-full px-2.5 py-0.5 text-xs font-medium ${
                source.enabled ? "text-accent" : "text-ink-muted"
              }`}
            >
              {source.enabled ? t.enabled[lang] : t.configured[lang]}
            </span>
          </Link>
        ))}
      </div>
    </div>
  );
}
