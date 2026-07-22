"use client";

import { useTranslations } from "@/lib/i18n";

export function SiteFooter() {
  const t = useTranslations();
  return (
    <footer className="mx-auto mt-16 max-w-5xl border-t border-border px-4 py-8 text-xs text-ink-muted sm:px-6">
      {t("footerTagline")}
    </footer>
  );
}