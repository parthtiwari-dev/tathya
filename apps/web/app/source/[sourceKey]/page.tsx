import Link from "next/link";
import { notFound } from "next/navigation";
import { getSourceByKey, sources } from "@/lib/mock-sources";
import { getClaimsBySourceKey } from "@/lib/mock-data";
import { relativeTime, sourceTypeLabel } from "@/lib/format";

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

  return (
    <div className="py-10">
      <Link href="/sources" className="text-xs text-ink-muted hover:text-accent">
        ← All sources
      </Link>
      <h1 className="mt-2 font-serif text-2xl font-medium text-ink">{source.name}</h1>
      <p className="mt-1 text-sm text-ink-secondary">
        {source.trustCategory} · {source.type} ·{" "}
        <a href={source.url} target="_blank" rel="noopener noreferrer" className="underline-offset-2 hover:text-accent hover:underline">
          {source.url}
        </a>
      </p>

      <h2 className="mt-8 text-xs font-medium uppercase tracking-wide text-ink-muted">
        Claims traced to this source ({claims.length})
      </h2>

      <ul className="mt-4 space-y-3">
        {claims.length === 0 ? (
          <p className="text-sm text-ink-muted">No claims from this source yet.</p>
        ) : (
          claims.map((claim) => (
            <li key={claim.id} className="rounded-lg border border-border p-3.5">
              <p className="text-xs text-ink-muted">
                <Link href={`/topic/${claim.topicSlug}`} className="hover:text-accent hover:underline">
                  {claim.topicTitle}
                </Link>
                {" · "}
                {sourceTypeLabel(claim.sourceType)}
              </p>
              <p className="mt-1.5 text-sm leading-relaxed text-ink">{claim.claimText}</p>
              <p className="mt-1.5 text-xs text-ink-muted">{relativeTime(claim.publishedAt)}</p>
            </li>
          ))
        )}
      </ul>
    </div>
  );
}
