import { notFound } from "next/navigation";
import { getAllTopics, getTopicBySlug } from "@/lib/mock-data";
import { TopicPageBody } from "@/components/TopicPageBody";

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
  return <TopicPageBody topic={topic} />;
}