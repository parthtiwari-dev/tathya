import Link from "next/link";
import type { Claim } from "@/lib/types";

const heading = { en: "Sources in this case file", hi: "इस केस फ़ाइल में स्रोत" };

export function SourcesUsed({ claims, lang = "en" }: { claims: Claim[]; lang?: "en" | "hi" }) {
  const nameByKey = new Map<string, string>();
  for (const claim of claims) {
    if (claim.sourceKey && !nameByKey.has(claim.sourceKey)) {
      nameByKey.set(claim.sourceKey, claim.sourceName ?? claim.sourceKey);
    }
  }
  const uniqueKeys = Array.from(nameByKey.keys());
  if (uniqueKeys.length === 0) return null;

  return (
    <section aria-labelledby="sources-heading">
      <h2 id="sources-heading" className="text-xs font-medium uppercase tracking-wide text-ink-muted">
        {heading[lang]}
      </h2>
      <div className="mt-3 flex flex-wrap gap-2">
        {uniqueKeys.map((key) => (
          <Link key={key} href={`/source/${key}`} className="rounded-full border border-border px-3 py-1 text-xs text-ink-secondary transition-colors hover:border-accent/40 hover:text-accent">
            {nameByKey.get(key)}
          </Link>
        ))}
      </div>
    </section>
  );
}
