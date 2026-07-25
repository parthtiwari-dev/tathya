import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { getTopicBySlug } from "@/lib/api";
import { TopicPageBody } from "@/components/TopicPageBody";

// Dynamic per-request metadata: without this every topic page inherited the
// homepage's static title/description, which is bad for both search ranking
// and link-preview quality on WhatsApp/Twitter shares.
export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  const topic = await getTopicBySlug(slug);
  if (!topic) return {};

  const description = topic.summary.length > 300 ? `${topic.summary.slice(0, 297)}...` : topic.summary;
  const url = `/topic/${topic.slug}`;

  return {
    title: topic.title,
    description,
    alternates: { canonical: url },
    openGraph: {
      type: "article",
      title: topic.title,
      description,
      url,
      tags: topic.entityTags,
    },
    twitter: {
      card: "summary",
      title: topic.title,
      description,
    },
  };
}

// Dynamic per-request (no generateStaticParams / static generation) so a
// newly persisted topic shows up without a rebuild -- see lib/api.ts.
export default async function TopicPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const topic = await getTopicBySlug(slug);
  if (!topic) notFound();
  return <TopicPageBody topic={topic} />;
}
