import Link from "next/link";
import { getAllMinistries, getTopicsByMinistry } from "@/lib/mock-data";
import { FeedItem } from "@/components/FeedItem";

export function generateStaticParams() {
  return getAllMinistries().map((m) => ({ slug: m.slug }));
}

export default async function MinistryPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const topics = getTopicsByMinistry(slug);
  const ministry = getAllMinistries().find((m) => m.slug === slug);
  const name = ministry?.name ?? slug;

  return (
    <div className="py-10">
      <Link href="/" className="text-xs text-ink-muted hover:text-accent">
        ← All topics
      </Link>
      <h1 className="mt-2 font-serif text-2xl font-medium text-ink">{name}</h1>
      <p className="mt-1 text-sm text-ink-secondary">
        {topics.length} topic{topics.length === 1 ? "" : "s"} tracked under this ministry.
      </p>

      <div className="mt-8">
        {topics.length === 0 ? (
          <p className="text-sm text-ink-muted">No live topics for this ministry right now.</p>
        ) : (
          topics.map((topic) => <FeedItem key={topic.id} topic={topic} />)
        )}
      </div>
    </div>
  );
}
