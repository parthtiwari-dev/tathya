import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { getSourceByKey, getClaimsBySourceKey } from "@/lib/api";
import { SourcePageBody } from "@/components/SourcePageBody";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ sourceKey: string }>;
}): Promise<Metadata> {
  const { sourceKey } = await params;
  const source = await getSourceByKey(sourceKey);
  if (!source) return {};

  const title = `${source.name} — claims on Tathya`;
  const description = `Every claim attributed to ${source.name} on Tathya, with links back to the original ${source.trustCategory} source for each one.`;
  const url = `/source/${source.sourceKey}`;

  return {
    title,
    description,
    alternates: { canonical: url },
    openGraph: { type: "website", title, description, url },
    twitter: { card: "summary", title, description },
  };
}

export default async function SourceDetailPage({
  params,
}: {
  params: Promise<{ sourceKey: string }>;
}) {
  const { sourceKey } = await params;
  const source = await getSourceByKey(sourceKey);
  if (!source) notFound();

  const claims = await getClaimsBySourceKey(sourceKey);

  return <SourcePageBody source={source} claims={claims} />;
}
