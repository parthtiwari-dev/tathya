import Link from "next/link";
import type { TopicSummary } from "@/lib/types";
import { relativeTime } from "@/lib/format";

export function FeedItem({ topic }: { topic: TopicSummary }) {
  const totalSources =
    topic.sourceCount.official + topic.sourceCount.media + topic.sourceCount.citizen;

  return (
    <Link
      href={`/topic/${topic.slug}`}
      className="group block border-b border-border py-6 transition-colors first:pt-0"
    >
      <div className="flex items-center gap-3 text-xs text-ink-muted">
        <StatusBadge status={topic.status} />
        <span>{topic.ministry}</span>
        <span aria-hidden="true">·</span>
        <span>{relativeTime(topic.lastSignalAt)}</span>
      </div>

      <h2 className="mt-2 font-serif text-xl font-medium leading-snug text-ink transition-colors group-hover:text-accent">
        {topic.title}
      </h2>

      <p className="mt-2 max-w-2xl text-[15px] leading-relaxed text-ink-secondary">
        {topic.summary}
      </p>

      <div className="mt-3 flex flex-wrap items-center gap-3">
        <span className="text-xs text-ink-muted">
          {totalSources} source{totalSources === 1 ? "" : "s"}
          {" · "}
          {topic.sourceCount.official} official / {topic.sourceCount.media} media / {topic.sourceCount.citizen} citizen
        </span>
      </div>

      {topic.entityTags.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-2">
          {topic.entityTags.map((tag) => (
            <span
              key={tag}
              className="rounded-full border border-border px-2.5 py-0.5 text-xs text-ink-secondary"
            >
              {tag}
            </span>
          ))}
        </div>
      )}
    </Link>
  );
}

function StatusBadge({ status }: { status: TopicSummary["status"] }) {
  if (status === "live") {
    return (
      <span className="inline-flex items-center gap-1.5 font-medium text-accent">
        <span className="h-1.5 w-1.5 rounded-full bg-accent" />
        Live
      </span>
    );
  }
  if (status === "archived") {
    return <span className="font-medium text-ink-muted">Archived</span>;
  }
  return <span className="font-medium text-ink-muted">Draft</span>;
}
