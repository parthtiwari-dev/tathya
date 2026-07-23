import { notFound } from "next/navigation";
import { getTopicBySlug } from "@/lib/api";
import { TopicPageBody } from "@/components/TopicPageBody";

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
