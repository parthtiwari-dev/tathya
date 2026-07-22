import { getAllMinistries, getTopicsByMinistry } from "@/lib/mock-data";
import { MinistryPageBody } from "@/components/MinistryPageBody";

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

  return <MinistryPageBody name={name} topics={topics} />;
}
