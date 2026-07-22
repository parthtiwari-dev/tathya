import { notFound } from "next/navigation";
import { getSourceByKey, sources } from "@/lib/mock-sources";
import { getClaimsBySourceKey } from "@/lib/mock-data";
import { SourcePageBody } from "@/components/SourcePageBody";

export function generateStaticParams() {
  return sources.map((s) => ({ sourceKey: s.sourceKey }));
}

export default async function SourceDetailPage({
  params,
}: {
  params: Promise<{ sourceKey: string }>;
}) {
  const { sourceKey } = await params;
  const source = getSourceByKey(sourceKey);
  if (!source) notFound();

  const claims = getClaimsBySourceKey(sourceKey);

  return <SourcePageBody source={source} claims={claims} />;
}
