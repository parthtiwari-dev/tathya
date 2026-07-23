"use client";

import { useState } from "react";
import { Flag } from "lucide-react";
import { useLanguage } from "@/lib/i18n";
import { submitCorrection } from "@/lib/api";

const issueTypes = [
  { en: "Wrong quote", hi: "गलत उद्धरण" },
  { en: "Wrong date", hi: "गलत तिथि" },
  { en: "Wrong source", hi: "गलत स्रोत" },
  { en: "Misattribution", hi: "गलत आरोपण" },
  { en: "Other extraction error", hi: "अन्य निष्कर्षण त्रुटि" },
];

const t = {
  reportIssue: { en: "Report an extraction issue", hi: "निष्कर्षण त्रुटि की रिपोर्ट करें" },
  thanks: { en: "Reported — thank you.", hi: "रिपोर्ट कर दी गई — धन्यवाद।" },
  placeholder: {
    en: "What's wrong with the extraction? (not a dispute about the claim itself)",
    hi: "निष्कर्षण में क्या गलत है? (यह दावे पर विवाद नहीं है)",
  },
  submit: { en: "Submit report", hi: "रिपोर्ट भेजें" },
  sending: { en: "Sending…", hi: "भेजा जा रहा है…" },
  cancel: { en: "Cancel", hi: "रद्द करें" },
  failed: { en: "Couldn't send that — try again?", hi: "भेजा नहीं जा सका — फिर से कोशिश करें?" },
};

// NOTE: /corrections/public and rate-limiting are deliberately not live yet
// (see docs/roadmap_execution_plan.md -- left for right before launch), but
// POST /corrections itself is reachable, so this submits for real.
export function CorrectionReportButton({
  targetTable,
  targetId,
}: {
  targetTable: "claims" | "events" | "verifiable_facts";
  targetId: string;
}) {
  const { lang } = useLanguage();
  const [open, setOpen] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState(false);
  const [issueType, setIssueType] = useState(issueTypes[0].en);
  const [note, setNote] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError(false);
    try {
      await submitCorrection({
        targetTable,
        targetRowId: targetId,
        issueDescription: note.trim() ? `${issueType}: ${note.trim()}` : issueType,
      });
      setSubmitted(true);
    } catch {
      setError(true);
    } finally {
      setSubmitting(false);
    }
  }

  if (submitted) {
    return <p className="text-xs text-ink-muted">{t.thanks[lang]}</p>;
  }

  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        className="inline-flex items-center gap-1 text-xs text-ink-muted transition-colors hover:text-accent"
      >
        <Flag size={11} />
        {t.reportIssue[lang]}
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
          <option key={type.en} value={type.en}>
            {type[lang]}
          </option>
        ))}
      </select>
      <textarea
        value={note}
        onChange={(e) => setNote(e.target.value)}
        placeholder={t.placeholder[lang]}
        rows={2}
        className="w-full rounded border border-border bg-paper px-2 py-1 text-xs"
      />
      {error && <p className="text-xs text-red-600">{t.failed[lang]}</p>}
      <div className="flex items-center gap-2">
        <button
          type="submit"
          disabled={submitting}
          className="rounded bg-accent px-2.5 py-1 text-xs font-medium text-paper disabled:opacity-60"
        >
          {submitting ? t.sending[lang] : t.submit[lang]}
        </button>
        <button
          type="button"
          onClick={() => setOpen(false)}
          className="text-xs text-ink-muted hover:text-ink"
        >
          {t.cancel[lang]}
        </button>
      </div>
    </form>
  );
}
