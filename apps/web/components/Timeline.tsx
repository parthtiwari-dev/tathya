import type { TimelineEvent } from "@/lib/types";
import { formatDate } from "@/lib/format";
import { localizedText } from "@/lib/localizedText";

const heading = { en: "Timeline", hi: "समयरेखा" };
const enBadgeTitle = { en: "Hindi translation not yet available — showing English", hi: "हिंदी अनुवाद अभी उपलब्ध नहीं — अंग्रेज़ी दिखाई जा रही है।" };

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
          {sorted.map((event) => {
            const description = localizedText(event.description, event.descriptionHi, lang);
            return (
              <li key={event.id} className="min-w-[220px] max-w-[260px] flex-1 border-l-2 border-accent/30 pl-4">
                <p className="text-xs font-medium text-accent">{formatDate(event.eventDate)}</p>
                <p className="mt-1.5 text-sm leading-relaxed text-ink-secondary">
                  {description.text}
                  {description.isFallback && (
                    <span className="ml-1.5 align-middle text-[10px] font-medium uppercase tracking-wide text-ink-muted" title={enBadgeTitle[lang]}>
                      EN
                    </span>
                  )}
                </p>
              </li>
            );
          })}
        </ol>
      </div>
    </section>
  );
}
