import { getAllMinistries, getTopicsByMinistry } from "@/lib/api";
import { MinistryPageBody } from "@/components/MinistryPageBody";

export default async function MinistryPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const [topics, allMinistries] = await Promise.all([getTopicsByMinistry(slug), getAllMinistries()]);
  const ministry = allMinistries.find((m) => m.slug === slug);
  const name = ministry?.name ?? slug;

  return <MinistryPageBody name={name} topics={topics} />;
}
