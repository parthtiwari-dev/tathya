import type { VerifiableFact } from "@/lib/types";
import { CorrectionReportButton } from "@/components/CorrectionReportButton";

const heading = { en: "Verifiable Facts", hi: "सत्यापन योग्य तथ्य" };
const subheading = {
  en: "Checked against primary government documents only — not a claim, a confirmed record.",
  hi: "केवल प्राथमिक सरकारी दस्तावेज़ों से सत्यापित — यह दावा नहीं, एक पुष्ट अभिलेख है।",
};

const docTypeLabel: Record<VerifiableFact["docType"], { en: string; hi: string }> = {
  gazette: { en: "Gazette notification", hi: "राजपत्र अधिसूचना" },
  parliament_qa: { en: "Parliament Q&A", hi: "संसद प्रश्नोत्तर" },
  pib: { en: "PIB release", hi: "PIB विज्ञप्ति" },
  dataset: { en: "Official dataset", hi: "आधिकारिक डेटासेट" },
};

export function VerifiableFactsPanel({ facts, lang = "en" }: { facts: VerifiableFact[]; lang?: "en" | "hi" }) {
  if (facts.length === 0) return null;

  return (
    <section aria-labelledby="facts-heading" className="rounded-xl border border-accent/30 bg-accent-soft p-5">
      <h2 id="facts-heading" className="text-xs font-medium uppercase tracking-wide text-accent">
        {heading[lang]}
      </h2>
      <p className="mt-1 text-xs text-ink-secondary">{subheading[lang]}</p>

      <ul className="mt-4 space-y-3">
        {facts.map((fact) => (
          <li key={fact.id} className="rounded-lg border border-border bg-paper p-3.5">
            <p className="text-sm leading-relaxed text-ink">{fact.factText}</p>
            <blockquote className="mt-2 border-l-2 border-accent/40 pl-2.5 text-xs italic text-ink-secondary">
              "{fact.quotedSpan}"
            </blockquote>
            <div className="mt-2.5 flex items-center justify-between text-xs text-ink-muted">
              <a href={fact.primaryDocUrl} target="_blank" rel="noopener noreferrer" className="underline-offset-2 hover:text-accent hover:underline">
                {docTypeLabel[fact.docType][lang]}
              </a>
            </div>
            <div className="mt-2">
              <CorrectionReportButton targetTable="facts" targetId={fact.id} />
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}