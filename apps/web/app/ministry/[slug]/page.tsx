import type { Metadata } from "next";
import { getAllMinistries, getTopicsByMinistry } from "@/lib/api";
import { MinistryPageBody } from "@/components/MinistryPageBody";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  const allMinistries = await getAllMinistries();
  const ministry = allMinistries.find((m) => m.slug === slug);
  if (!ministry) return {};

  const title = `${ministry.name} — topics`;
  const description = `Sourced case files tracked under the ${ministry.name} on Tathya, an autonomous, non-partisan civic record of the Government of India.`;
  const url = `/ministry/${slug}`;

  return {
    title,
    description,
    alternates: { canonical: url },
    openGraph: { type: "website", title, description, url },
    twitter: { card: "summary", title, description },
  };
}

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
