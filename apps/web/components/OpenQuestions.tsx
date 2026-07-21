import type { OpenQuestion } from "@/lib/types";

export function OpenQuestions({ questions }: { questions: OpenQuestion[] }) {
  if (questions.length === 0) return null;

  return (
    <section aria-labelledby="open-questions-heading">
      <h2 id="open-questions-heading" className="text-xs font-medium uppercase tracking-wide text-ink-muted">
        Open Questions
      </h2>
      <p className="mt-1 text-xs text-ink-muted">
        Gaps between what has been claimed and what is independently verified so far — not an accusation, a status.
      </p>
      <ul className="mt-3 space-y-2">
        {questions.map((q) => (
          <li
            key={q.id}
            className="rounded-lg border border-dashed border-border bg-surface p-3 text-sm leading-relaxed text-ink-secondary"
          >
            {q.question}
          </li>
        ))}
      </ul>
    </section>
  );
}
