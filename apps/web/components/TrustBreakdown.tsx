import type { SourceCount } from "@/lib/types";

const labels = {
  official: { en: "Official", hi: "सरकारी" },
  media: { en: "Independent media", hi: "स्वतंत्र मीडिया" },
  citizen: { en: "Citizen", hi: "नागरिक" },
};

export function TrustBreakdown({ counts, lang = "en" }: { counts: SourceCount; lang?: "en" | "hi" }) {
  const total = counts.official + counts.media + counts.citizen;
  if (total === 0) return null;

  const rows = [
    { label: labels.official[lang], value: counts.official },
    { label: labels.media[lang], value: counts.media },
    { label: labels.citizen[lang], value: counts.citizen },
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