"use client";

import { useState } from "react";
import { ChevronDown } from "lucide-react";
import type { HistoryEntry } from "@/lib/types";
import { relativeTime } from "@/lib/format";

const heading = {
  en: "History — every addition and correction, never rewritten",
  hi: "इतिहास — हर जोड़ और सुधार, कभी फिर से नहीं लिखा गया",
};

const typeLabel: Record<HistoryEntry["type"], { en: string; hi: string }> = {
  claim_added: { en: "Claim added", hi: "दावा जोड़ा गया" },
  event_added: { en: "Event added", hi: "घटना जोड़ी गई" },
  fact_added: { en: "Fact added", hi: "तथ्य जोड़ा गया" },
  correction_reported: { en: "Correction reported", hi: "सुधार की सूचना दी गई" },
  correction_applied: { en: "Correction applied", hi: "सुधार लागू किया गया" },
  status_changed: { en: "Status changed", hi: "स्थिति बदली गई" },
};

export function TopicHistory({ history, lang = "en" }: { history: HistoryEntry[]; lang?: "en" | "hi" }) {
  const [open, setOpen] = useState(false);
  if (history.length === 0) return null;
  const sorted = [...history].sort((a, b) => (a.timestamp < b.timestamp ? 1 : -1));

  return (
    <section className="border-t border-border pt-6">
      <button onClick={() => setOpen((v) => !v)} className="flex w-full items-center justify-between gap-3 text-left text-xs font-medium uppercase tracking-wide text-ink-muted" aria-expanded={open}>
        {heading[lang]}
        <ChevronDown size={14} className={`shrink-0 transition-transform ${open ? "rotate-180" : ""}`} />
      </button>

      {open && (
        <ol className="mt-4 space-y-3 border-l border-border pl-4">
          {sorted.map((entry) => (
            <li key={entry.id} className="text-sm">
              <span className="text-ink-muted">{relativeTime(entry.timestamp)}</span>
              {" — "}
              <span className="font-medium text-ink-secondary">{typeLabel[entry.type][lang]}:</span>{" "}
              <span className="text-ink-secondary">{entry.description}</span>
            </li>
          ))}
        </ol>
      )}
    </section>
  );
}