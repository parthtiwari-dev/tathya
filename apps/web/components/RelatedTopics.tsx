import Link from "next/link";
import type { TopicRelation } from "@/lib/types";

const relationLabel: Record<TopicRelation["relationType"], string> = {
  related: "Related",
  escalated_from: "Escalated from",
  referenced_in: "Referenced in",
  same_policy_area: "Same policy area",
};

export function RelatedTopics({ relations }: { relations: TopicRelation[] }) {
  if (relations.length === 0) return null;

  return (
    <section aria-labelledby="related-heading">
      <h2 id="related-heading" className="text-xs font-medium uppercase tracking-wide text-ink-muted">
        Related Topics
      </h2>
      <ul className="mt-3 space-y-2">
        {relations.map((relation) => (
          <li key={relation.id}>
            <Link
              href={`/topic/${relation.relatedTopicSlug}`}
              className="flex items-center gap-3 rounded-lg border border-border bg-surface p-3 text-sm transition-colors hover:border-accent/40"
            >
              <span className="shrink-0 rounded-full border border-border px-2 py-0.5 text-xs text-ink-muted">
                {relationLabel[relation.relationType]}
              </span>
              <span className="text-ink">{relation.relatedTopicTitle}</span>
            </Link>
          </li>
        ))}
      </ul>
    </section>
  );
}
