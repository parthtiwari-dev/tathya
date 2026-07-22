import type { TimelineEvent } from "@/lib/types";
import { formatDate } from "@/lib/format";

const heading = { en: "Timeline", hi: "समयरेखा" };

export function Timeline({ events, lang = "en" }: { events: TimelineEvent[]; lang?: "en" | "hi" }) {
  if (events.length === 0) return null;
  const sorted = [...events].sort((a, b) => (a.eventDate < b.eventDate ? -1 : 1));

  return (
    <section aria-labelledby="timeline-heading">
      <h2 id="timeline-heading" className="text-xs font-medium uppercase tracking-wide text-ink-muted">
        {heading[lang]}
      </h2>
      <div className="mt-4 overflow-x-auto">
        <ol className="flex min-w-full gap-6 pb-2">
          {sorted.map((event) => (
            <li key={event.id} className="min-w-[220px] max-w-[260px] flex-1 border-l-2 border-accent/30 pl-4">
              <p className="text-xs font-medium text-accent">{formatDate(event.eventDate)}</p>
              <p className="mt-1.5 text-sm leading-relaxed text-ink-secondary">{event.description}</p>
            </li>
          ))}
        </ol>
      </div>
    </section>
  );
}