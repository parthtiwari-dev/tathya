import { Landmark, Newspaper, Users, Flag } from "lucide-react";
import type { Claim, ClaimSourceType } from "@/lib/types";
import { relativeTime } from "@/lib/format";
import { CorrectionReportButton } from "@/components/CorrectionReportButton";

const columnOrder: ClaimSourceType[] = ["government", "opposition", "media", "citizen"];

const heading = { en: "Claims Ledger", hi: "दावा लेजर" };
const subheading = {
  en: "What each side said, side by side. No verdict — only who said it and where.",
  hi: "हर पक्ष ने क्या कहा, साथ-साथ। कोई फैसला नहीं — केवल किसने और कहाँ कहा।",
};
const columnLabels = {
  government: { en: "Government Says", hi: "सरकार का कहना है" },
  opposition: { en: "Opposition Says", hi: "विपक्ष का कहना है" },
  media: { en: "Independent Media Reports", hi: "स्वतंत्र मीडिया रिपोर्ट" },
  citizen: { en: "Citizens & Protesters Say", hi: "नागरिक और प्रदर्शनकारी कहते हैं" },
};

const columnIcons: Record<ClaimSourceType, typeof Landmark> = {
  government: Landmark,
  opposition: Flag,
  media: Newspaper,
  citizen: Users,
};

export function ClaimsLedger({ claims, lang = "en" }: { claims: Claim[]; lang?: "en" | "hi" }) {
  if (claims.length === 0) return null;

  const columns = columnOrder
    .map((type) => ({ type, claims: claims.filter((c) => c.sourceType === type) }))
    .filter((column) => column.claims.length > 0);

  return (
    <section aria-labelledby="claims-heading">
      <h2 id="claims-heading" className="text-xs font-medium uppercase tracking-wide text-ink-muted">
        {heading[lang]}
      </h2>
      <p className="mt-1 text-xs text-ink-muted">{subheading[lang]}</p>

      <div className="mt-4 grid gap-6" style={{ gridTemplateColumns: `repeat(auto-fit, minmax(240px, 1fr))` }}>
        {columns.map((column) => {
          const Icon = columnIcons[column.type];
          return (
            <div key={column.type}>
              <h3 className="flex items-center gap-1.5 border-b border-border pb-2 text-sm font-medium text-ink">
                <Icon size={14} className="text-ink-muted" />
                {columnLabels[column.type][lang]}
              </h3>
              <ul className="mt-3 space-y-4">
                {column.claims.map((claim) => (
                  <li key={claim.id} className="rounded-lg border border-border bg-surface p-3.5">
                    <p className="text-sm leading-relaxed text-ink">{claim.claimText}</p>
                    <blockquote className="mt-2 border-l-2 border-accent/40 pl-2.5 text-xs italic text-ink-secondary">
                      "{claim.quotedSpan}"
                    </blockquote>
                    <div className="mt-2.5 flex items-center justify-between text-xs text-ink-muted">
                      <a href={claim.sourceUrl} target="_blank" rel="noopener noreferrer" className="underline-offset-2 hover:text-accent hover:underline">
                        {claim.sourceName}
                      </a>
                      <span>{relativeTime(claim.publishedAt)}</span>
                    </div>
                    <div className="mt-2">
                      <CorrectionReportButton targetTable="claims" targetId={claim.id} />
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          );
        })}
      </div>
    </section>
  );
}