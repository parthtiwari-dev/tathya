import { getAllSources } from "@/lib/api";
import { SourcesIndexBody } from "@/components/SourcesIndexBody";

export default async function SourcesIndexPage() {
  const sources = await getAllSources();
  return <SourcesIndexBody sources={sources} />;
}
