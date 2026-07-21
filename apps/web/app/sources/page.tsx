import Link from "next/link";
import { sources } from "@/lib/mock-sources";

const trustLabel: Record<string, string> = {
  official: "Official",
  media: "Media",
  citizen: "Citizen",
  foreign: "Foreign",
};

export default function SourcesIndexPage() {
  return (
    <div className="py-10">
      <h1 className="font-serif text-2xl font-medium text-ink">Source Explorer</h1>
      <p className="mt-1 text-sm text-ink-secondary">
        The fixed list of sources Tathya watches. Enabled sources are actively ingested; the rest are configured but not yet live.
      </p>

      <div className="mt-8 divide-y divide-border border-y border-border">
        {sources.map((source) => (
          <Link
            key={source.sourceKey}
            href={`/source/${source.sourceKey}`}
            className="flex items-center justify-between gap-4 py-3.5 transition-colors hover:bg-surface"
          >
            <div>
              <p className="text-sm font-medium text-ink">{source.name}</p>
              <p className="text-xs text-ink-muted">{trustLabel[source.trustCategory]} · {source.type}</p>
            </div>
            <span
              className={`shrink-0 rounded-full px-2.5 py-0.5 text-xs font-medium ${
                source.enabled ? "text-accent" : "text-ink-muted"
              }`}
            >
              {source.enabled ? "Enabled" : "Configured"}
            </span>
          </Link>
        ))}
      </div>
    </div>
  );
}
