"use client";

import { useState } from "react";
import { Flag } from "lucide-react";

const issueTypes = [
  "Wrong quote",
  "Wrong date",
  "Wrong source",
  "Misattribution",
  "Other extraction error",
];

// NOTE: this posts nowhere yet. Once API v1's POST /corrections is reachable
// from the frontend (CORS configured, deployed URL known), replace the
// setTimeout below with a real fetch(`${API_URL}/corrections`, { method: "POST", body: ... }).
export function CorrectionReportButton({
  targetTable,
  targetId,
}: {
  targetTable: string;
  targetId: string;
}) {
  const [open, setOpen] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [issueType, setIssueType] = useState(issueTypes[0]);
  const [note, setNote] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    await new Promise((resolve) => setTimeout(resolve, 500));
    setSubmitting(false);
    setSubmitted(true);
  }

  if (submitted) {
    return <p className="text-xs text-ink-muted">Reported — thank you.</p>;
  }

  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        className="inline-flex items-center gap-1 text-xs text-ink-muted transition-colors hover:text-accent"
      >
        <Flag size={11} />
        Report an extraction issue
      </button>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-2 rounded-md border border-border bg-paper p-3">
      <input type="hidden" value={targetTable} readOnly />
      <input type="hidden" value={targetId} readOnly />
      <select
        value={issueType}
        onChange={(e) => setIssueType(e.target.value)}
        className="w-full rounded border border-border bg-paper px-2 py-1 text-xs"
      >
        {issueTypes.map((type) => (
          <option key={type} value={type}>
            {type}
          </option>
        ))}
      </select>
      <textarea
        value={note}
        onChange={(e) => setNote(e.target.value)}
        placeholder="What's wrong with the extraction? (not a dispute about the claim itself)"
        rows={2}
        className="w-full rounded border border-border bg-paper px-2 py-1 text-xs"
      />
      <div className="flex items-center gap-2">
        <button
          type="submit"
          disabled={submitting}
          className="rounded bg-accent px-2.5 py-1 text-xs font-medium text-paper disabled:opacity-60"
        >
          {submitting ? "Sending…" : "Submit report"}
        </button>
        <button
          type="button"
          onClick={() => setOpen(false)}
          className="text-xs text-ink-muted hover:text-ink"
        >
          Cancel
        </button>
      </div>
    </form>
  );
}
