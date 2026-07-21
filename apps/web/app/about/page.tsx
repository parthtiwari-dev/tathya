export const metadata = {
  title: "About — Tathya",
};

const paragraphs = [
  "Tathya is an autonomous civic record of India's Union Government. It watches a fixed list of public sources, stores immutable snapshots of what those sources published, and later groups related material into sourced case files. It does not decide which political stories matter by hand, and it does not publish verdicts on whether a claim is true or false.",
  "A cluster of signals becomes a public case file only when it crosses a fixed significance threshold — independent source count, speed of new coverage, and confirmation from more than one type of source. No person decides this on a per-story basis.",
  "The central promise is narrow and strict: record what was said, who said it, when it was said, and what primary documents can verify. A government claim, an opposition claim, an independent media report, and a citizen statement may sit side by side, but the system must never disguise interpretation as fact. The Verifiable Facts panel is reserved for primary records such as PIB releases, Parliament answers, gazette material, datasets, and similar documents.",
  "Every public claim, event, fact, summary line, and correction must point back to stored source material. If the original page is edited, deleted, or disappears, the ingestion-time snapshot remains the audit trail. Snapshots are for accountability and reproducibility; they are not a license to republish entire copyrighted articles publicly without review.",
  "Tathya protects ordinary private citizens from unnecessary exposure. Public officials, elected representatives, parties, ministries, public spokespeople, and self-identified public actors can be resolved as entities. Private bystanders, incidental names, and people only visible because they were captured in footage should not be expanded into profiles or cross-referenced beyond the public source itself.",
  "Corrections are for Tathya's own mechanical mistakes: a wrong date, merged entity, incorrect attribution, broken source link, or extraction error. Corrections are not a route for political disputes about whether a source's statement is correct. A correction history should be visible and append-only.",
  "The project stays open source under AGPL-3.0 so the scoring, clustering, and generation logic can be inspected by people who disagree with one another. Hosting and data storage should not depend on any single point of failure; the record is built to survive pressure to take it down, not just to survive the founder losing interest. The system earns trust through boring discipline: fixed source rules, append-only evidence, symmetric treatment of political actors, and no private editorial shortcuts.",
];

export default function AboutPage() {
  return (
    <article className="max-w-2xl py-12">
      <h1 className="font-serif text-3xl font-medium text-ink">Mission &amp; Ethics</h1>
      <div className="mt-6 space-y-5">
        {paragraphs.map((paragraph, i) => (
          <p key={i} className="text-[15px] leading-relaxed text-ink-secondary">
            {paragraph}
          </p>
        ))}
      </div>
    </article>
  );
}
