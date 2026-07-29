import type { OpenQuestion } from "@/lib/types";
import { localizedText } from "@/lib/localizedText";

const heading = { en: "Open Questions", hi: "अनुत्तरित प्रश्न" };
const subheading = {
  en: "Gaps between what has been claimed and what is independently verified so far — not an accusation, a status.",
  hi: "अब तक जो दावा किया गया और जो स्वतंत्र रूप से सत्यापित है, उसके बीच का अंतर — यह आरोप नहीं, एक स्थिति है।",
};
const enBadgeTitle = { en: "Hindi translation not yet available — showing English", hi: "हिंदी अनुवाद अभी उपलब्ध नहीं — अंग्रेज़ी दिखाई जा रही है।" };

export function OpenQuestions({ questions, lang = "en" }: { questions: OpenQuestion[]; lang?: "en" | "hi" }) {
  if (questions.length === 0) return null;

  return (
    <section aria-labelledby="open-questions-heading">
      <h2 id="open-questions-heading" className="text-xs font-medium uppercase tracking-wide text-ink-muted">
        {heading[lang]}
      </h2>
      <p className="mt-1 text-xs text-ink-muted">{subheading[lang]}</p>
      <ul className="mt-3 space-y-2">
        {questions.map((q) => {
          const question = localizedText(q.question, q.questionHi, lang);
          return (
            <li key={q.id} className="rounded-lg border border-dashed border-border bg-surface p-3 text-sm leading-relaxed text-ink-secondary">
              {question.text}
              {question.isFallback && (
                <span className="ml-1.5 align-middle text-[10px] font-medium uppercase tracking-wide text-ink-muted" title={enBadgeTitle[lang]}>
                  EN
                </span>
              )}
            </li>
          );
        })}
      </ul>
    </section>
  );
}