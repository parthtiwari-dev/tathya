import type { Contradiction } from "@/lib/types";
import { formatDate } from "@/lib/format";

const heading = { en: "Statements Over Time", hi: "समय के साथ बयान" };
const subheading = {
  en: "The same entity, at two different points — shown side by side, no verdict on which is right.",
  hi: "एक ही पक्ष, दो अलग समयों पर — साथ-साथ दिखाया गया, कौन सही है इस पर कोई फैसला नहीं।",
};

export function Contradictions({ items, lang = "en" }: { items: Contradiction[]; lang?: "en" | "hi" }) {
  if (items.length === 0) return null;

  return (
    <section aria-labelledby="contradictions-heading">
      <h2 id="contradictions-heading" className="text-xs font-medium uppercase tracking-wide text-ink-muted">
        {heading[lang]}
      </h2>
      <p className="mt-1 text-xs text-ink-muted">{subheading[lang]}</p>

      <div className="mt-3 space-y-4">
        {items.map((item) => (
          <div key={item.id} className="rounded-lg border border-border p-4">
            <p className="text-xs font-medium text-ink-secondary">{item.entity}</p>
            <div className="mt-3 grid gap-4 sm:grid-cols-2">
              <StatementCard statement={item.statementA} />
              <StatementCard statement={item.statementB} />
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

function StatementCard({ statement }: { statement: Contradiction["statementA"] }) {
  return (
    <div className="rounded-md bg-surface p-3">
      <p className="text-xs text-ink-muted">{formatDate(statement.date)}</p>
      <p className="mt-1 text-sm leading-relaxed text-ink">{statement.text}</p>
      <a href={statement.sourceUrl} target="_blank" rel="noopener noreferrer" className="mt-2 inline-block text-xs text-ink-muted hover:text-accent hover:underline">
        {statement.sourceName}
      </a>
    </div>
  );
}