import Link from "next/link";
import type { TopicRelation } from "@/lib/types";

const heading = { en: "Related Topics", hi: "संबंधित विषय" };

const relationLabel: Record<TopicRelation["relationType"], { en: string; hi: string }> = {
  related: { en: "Related", hi: "संबंधित" },
  escalated_from: { en: "Escalated from", hi: "यहाँ से बढ़ा" },
  referenced_in: { en: "Referenced in", hi: "में संदर्भित" },
  same_policy_area: { en: "Same policy area", hi: "समान नीति क्षेत्र" },
};

export function RelatedTopics({ relations, lang = "en" }: { relations: TopicRelation[]; lang?: "en" | "hi" }) {
  if (relations.length === 0) return null;

  return (
    <section aria-labelledby="related-heading">
      <h2 id="related-heading" className="text-xs font-medium uppercase tracking-wide text-ink-muted">
        {heading[lang]}
      </h2>
      <ul className="mt-3 space-y-2">
        {relations.map((relation) => (
          <li key={relation.id}>
            <Link href={`/topic/${relation.relatedTopicSlug}`} className="flex items-center gap-3 rounded-lg border border-border bg-surface p-3 text-sm transition-colors hover:border-accent/40">
              <span className="shrink-0 rounded-full border border-border px-2 py-0.5 text-xs text-ink-muted">
                {relationLabel[relation.relationType][lang]}
              </span>
              <span className="text-ink">{relation.relatedTopicTitle}</span>
            </Link>
          </li>
        ))}
      </ul>
    </section>
  );
}