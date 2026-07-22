import Link from "next/link";
import type { Claim } from "@/lib/types";
import { getSourceByKey } from "@/lib/mock-sources";

const heading = { en: "Sources in this case file", hi: "इस केस फ़ाइल में स्रोत" };

export function SourcesUsed({ claims, lang = "en" }: { claims: Claim[]; lang?: "en" | "hi" }) {
  const uniqueKeys = Array.from(new Set(claims.map((c) => c.sourceKey)));
  if (uniqueKeys.length === 0) return null;

  return (
    <section aria-labelledby="sources-heading">
      <h2 id="sources-heading" className="text-xs font-medium uppercase tracking-wide text-ink-muted">
        {heading[lang]}
      </h2>
      <div className="mt-3 flex flex-wrap gap-2">
        {uniqueKeys.map((key) => {
          const source = getSourceByKey(key);
          return (
            <Link key={key} href={`/source/${key}`} className="rounded-full border border-border px-3 py-1 text-xs text-ink-secondary transition-colors hover:border-accent/40 hover:text-accent">
              {source?.name ?? key}
            </Link>
          );
        })}
      </div>
    </section>
  );
}