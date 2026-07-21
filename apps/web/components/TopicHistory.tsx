"use client";

import { useState } from "react";
import { ChevronDown } from "lucide-react";
import type { HistoryEntry } from "@/lib/types";
import { relativeTime } from "@/lib/format";

const typeLabel: Record<HistoryEntry["type"], string> = {
  claim_added: "Claim added",
  event_added: "Event added",
  fact_added: "Fact added",
  correction_applied: "Correction applied",
  status_changed: "Status changed",
};

export function TopicHistory({ history }: { history: HistoryEntry[] }) {
  const [open, setOpen] = useState(false);

  if (history.length === 0) return null;

  const sorted = [...history].sort((a, b) => (a.timestamp < b.timestamp ? 1 : -1));

  return (
    <section className="border-t border-border pt-6">
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center justify-between text-xs font-medium uppercase tracking-wide text-ink-muted"
        aria-expanded={open}
      >
        History — every addition and correction, never rewritten
        <ChevronDown size={14} className={`transition-transform ${open ? "rotate-180" : ""}`} />
      </button>

      {open && (
        <ol className="mt-4 space-y-3 border-l border-border pl-4">
          {sorted.map((entry) => (
            <li key={entry.id} className="text-sm">
              <span className="text-ink-muted">{relativeTime(entry.timestamp)}</span>
              {" — "}
              <span className="font-medium text-ink-secondary">{typeLabel[entry.type]}:</span>{" "}
              <span className="text-ink-secondary">{entry.description}</span>
            </li>
          ))}
        </ol>
      )}
    </section>
  );
}
