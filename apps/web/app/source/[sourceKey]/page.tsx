import { notFound } from "next/navigation";
import { getSourceByKey, getClaimsBySourceKey } from "@/lib/api";
import { SourcePageBody } from "@/components/SourcePageBody";

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
