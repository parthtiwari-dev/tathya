import { notFound } from "next/navigation";
import { getAllTopics, getTopicBySlug } from "@/lib/mock-data";
import { relativeTime } from "@/lib/format";
import { Timeline } from "@/components/Timeline";
import { ClaimsLedger } from "@/components/ClaimsLedger";
import { VerifiableFactsPanel } from "@/components/VerifiableFactsPanel";
import { RelatedTopics } from "@/components/RelatedTopics";
import { TopicHistory } from "@/components/TopicHistory";

export function generateStaticParams() {
  return getAllTopics().map((topic) => ({ slug: topic.slug }));
}

export default async function TopicPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const topic = getTopicBySlug(slug);

  if (!topic) notFound();

  return (
    <article className="max-w-3xl py-10">
      <div className="flex items-center gap-3 text-xs text-ink-muted">
        <StatusLabel status={topic.status} />
        <span>{topic.ministry}</span>
        <span aria-hidden="true">·</span>
        <span>updated {relativeTime(topic.lastSignalAt)}</span>
      </div>

      <h1 className="mt-2 font-serif text-3xl font-medium leading-tight text-ink">
        {topic.title}
      </h1>

      <p className="mt-4 text-[17px] leading-relaxed text-ink-secondary">{topic.summary}</p>

      <div className="mt-10 space-y-10">
        <Timeline events={topic.events} />
        <ClaimsLedger claims={topic.claims} />
        <VerifiableFactsPanel facts={topic.facts} />
        <RelatedTopics relations={topic.relations} />
        <TopicHistory history={topic.history} />
      </div>
    </article>
  );
}

function StatusLabel({ status }: { status: string }) {
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
