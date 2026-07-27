// Picks Hindi text when the language toggle is set to Hindi and a Hindi
// version actually exists; falls back to English otherwise. `isFallback`
// tells the caller "we're in Hindi mode but showing English" so the UI can
// mark it honestly (a silent language mix would misrepresent how complete
// the Hindi translation coverage actually is -- see
// docs/audit_and_next_steps.md Section 15).

export function localizedText(
  en: string,
  hi: string | null | undefined,
  lang: "en" | "hi"
): { text: string; isFallback: boolean } {
  if (lang === "hi" && hi) {
    return { text: hi, isFallback: false };
  }
  return { text: en, isFallback: lang === "hi" };
}
