import type { VerifiableFact } from "@/lib/types";
import { CorrectionReportButton } from "@/components/CorrectionReportButton";

const docTypeLabel: Record<VerifiableFact["docType"], string> = {
  gazette: "Gazette notification",
  parliament_qa: "Parliament Q&A",
  pib: "PIB release",
  dataset: "Official dataset",
};

export function VerifiableFactsPanel({ facts }: { facts: VerifiableFact[] }) {
  if (facts.length === 0) return null;

  return (
    <section
      aria-labelledby="facts-heading"
      className="rounded-xl border border-accent/30 bg-accent-soft p-5"
    >
      <h2 id="facts-heading" className="text-xs font-medium uppercase tracking-wide text-accent">
        Verifiable Facts
      </h2>
      <p className="mt-1 text-xs text-ink-secondary">
        Checked against primary government documents only — not a claim, a confirmed record.
      </p>

      <ul className="mt-4 space-y-3">
        {facts.map((fact) => (
          <li key={fact.id} className="rounded-lg border border-border bg-paper p-3.5">
            <p className="text-sm leading-relaxed text-ink">{fact.factText}</p>
            <blockquote className="mt-2 border-l-2 border-accent/40 pl-2.5 text-xs italic text-ink-secondary">
              “{fact.quotedSpan}”
            </blockquote>
            <div className="mt-2.5 flex items-center justify-between text-xs text-ink-muted">
              <a
                href={fact.primaryDocUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="underline-offset-2 hover:text-accent hover:underline"
              >
                {docTypeLabel[fact.docType]}
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
