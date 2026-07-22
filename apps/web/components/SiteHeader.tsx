"use client";

import Link from "next/link";
import { Search, Menu, X } from "lucide-react";
import { useState } from "react";
import { ThemeToggle } from "@/components/ThemeToggle";
import { LanguageToggle } from "@/components/LanguageToggle";
import { useTranslations } from "@/lib/i18n";

export function SiteHeader() {
  const t = useTranslations();
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <header className="sticky top-0 z-40 border-b border-border bg-paper/90 backdrop-blur">
      <div className="mx-auto flex max-w-5xl flex-wrap items-center gap-x-4 gap-y-3 px-4 py-4 sm:px-6">
        <Link href="/" className="flex items-baseline gap-2">
          <span className="font-serif text-xl font-medium tracking-tight text-ink">तथ्य</span>
          <span className="font-serif text-lg text-ink-secondary">Tathya</span>
        </Link>

        <Link
          href="/search"
          className="order-3 flex w-full basis-full items-center gap-2 rounded-full border border-border bg-surface px-4 py-2 text-sm text-ink-muted transition-colors hover:border-accent/40 sm:order-none sm:w-auto sm:basis-auto sm:flex-1"
        >
          <Search size={15} />
          <span className="truncate">{t("searchPlaceholder")}</span>
          <kbd className="ml-auto hidden shrink-0 rounded border border-border px-1.5 py-0.5 text-[10px] text-ink-muted sm:inline">
            ⌘K
          </kbd>
        </Link>

        <div className="ml-auto flex items-center gap-2 sm:ml-0">
          <nav className="hidden items-center gap-4 text-sm text-ink-secondary sm:flex">
            <Link href="/sources" className="transition-colors hover:text-ink">
              {t("navSources")}
            </Link>
            <Link href="/about" className="transition-colors hover:text-ink">
              {t("navAbout")}
            </Link>
          </nav>
          <LanguageToggle />
          <ThemeToggle />
          <button
            onClick={() => setMenuOpen((v) => !v)}
            aria-label="Menu"
            className="flex h-8 w-8 items-center justify-center rounded-full text-ink-secondary hover:bg-surface hover:text-ink sm:hidden"
          >
            {menuOpen ? <X size={16} /> : <Menu size={16} />}
          </button>
        </div>

        {menuOpen && (
          <nav className="flex w-full basis-full flex-col gap-1 border-t border-border pt-3 text-sm text-ink-secondary sm:hidden">
            <Link href="/sources" onClick={() => setMenuOpen(false)} className="py-1.5">
              {t("navSources")}
            </Link>
            <Link href="/about" onClick={() => setMenuOpen(false)} className="py-1.5">
              {t("navAbout")}
            </Link>
          </nav>
        )}
      </div>
    </header>
  );
}