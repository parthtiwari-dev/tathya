"use client";

import { useLanguage } from "@/lib/i18n";

export function LanguageToggle() {
  const { lang, setLang } = useLanguage();

  return (
    <button
      onClick={() => setLang(lang === "en" ? "hi" : "en")}
      aria-label="Switch language"
      className="flex h-8 items-center rounded-full border border-border px-2.5 text-xs font-medium text-ink-secondary transition-colors hover:border-accent/40 hover:text-ink"
    >
      <span className={lang === "en" ? "text-accent" : ""}>EN</span>
      <span className="mx-1 text-ink-muted">/</span>
      <span className={lang === "hi" ? "text-accent" : ""}>हिं</span>
    </button>
  );
}
