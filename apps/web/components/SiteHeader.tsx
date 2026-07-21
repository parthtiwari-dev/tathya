import Link from "next/link";
import { Search } from "lucide-react";
import { ThemeToggle } from "@/components/ThemeToggle";

export function SiteHeader() {
  return (
    <header className="sticky top-0 z-40 border-b border-border bg-paper/90 backdrop-blur">
      <div className="mx-auto flex max-w-5xl items-center justify-between gap-6 px-6 py-4">
        <Link href="/" className="flex items-baseline gap-2">
          <span className="font-serif text-xl font-medium tracking-tight text-ink">
            तथ्य
          </span>
          <span className="font-serif text-lg text-ink-secondary">Tathya</span>
        </Link>

        <Link
          href="/search"
          className="flex flex-1 max-w-md items-center gap-2 rounded-full border border-border bg-surface px-4 py-2 text-sm text-ink-muted transition-colors hover:border-accent/40"
        >
          <Search size={15} />
          <span>Search topics, people, ministries…</span>
        </Link>

        <nav className="flex items-center gap-5 text-sm text-ink-secondary">
          <Link href="/about" className="hidden transition-colors hover:text-ink sm:inline">
            About
          </Link>
          <ThemeToggle />
        </nav>
      </div>
    </header>
  );
}
