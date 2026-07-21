import type { SourceCount } from "@/lib/types";

export function TrustBreakdown({ counts }: { counts: SourceCount }) {
  const total = counts.official + counts.media + counts.citizen;
  if (total === 0) return null;

  const rows = [
    { label: "Official", value: counts.official },
    { label: "Independent media", value: counts.media },
    { label: "Citizen", value: counts.citizen },
  ].filter((row) => row.value > 0);

  return (
    <div className="flex flex-wrap gap-x-5 gap-y-1 text-xs text-ink-muted">
      {rows.map((row) => (
        <span key={row.label}>
          {row.label}: <span className="font-medium text-ink-secondary">{row.value}</span>
        </span>
      ))}
    </div>
  );
}
