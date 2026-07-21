"use client";

import { useState } from "react";
import Link from "next/link";

const ministries = [
  { label: "Home Affairs", slug: "home-affairs" },
  { label: "Railways", slug: "railways" },
  { label: "Education", slug: "education" },
];

const statuses = ["Live", "Archived"];

export function FilterSidebar() {
  const [openSection, setOpenSection] = useState<string | null>("ministry");

  function toggle(section: string) {
    setOpenSection((current) => (current === section ? null : section));
  }

  return (
    <aside className="hidden w-56 shrink-0 lg:block">
      <div className="sticky top-24 space-y-6 text-sm">
        <FilterSection
          title="Ministry"
          open={openSection === "ministry"}
          onToggle={() => toggle("ministry")}
        >
          <ul className="space-y-1.5">
            {ministries.map((ministry) => (
              <li key={ministry.slug}>
                <Link
                  href={`/ministry/${ministry.slug}`}
                  className="block text-ink-secondary transition-colors hover:text-accent"
                >
                  {ministry.label}
                </Link>
              </li>
            ))}
          </ul>
        </FilterSection>

        <FilterSection
          title="Status"
          open={openSection === "status"}
          onToggle={() => toggle("status")}
        >
          <ul className="space-y-1.5">
            {statuses.map((status) => (
              <li key={status} className="text-ink-secondary">
                <label className="flex items-center gap-2">
                  <input type="checkbox" className="accent-[var(--accent)]" />
                  {status}
                </label>
              </li>
            ))}
          </ul>
        </FilterSection>

        <FilterSection
          title="Date range"
          open={openSection === "date"}
          onToggle={() => toggle("date")}
        >
          <div className="space-y-2 text-ink-secondary">
            <label className="block text-xs text-ink-muted">From</label>
            <input
              type="date"
              className="w-full rounded border border-border bg-paper px-2 py-1 text-xs"
            />
            <label className="block text-xs text-ink-muted">To</label>
            <input
              type="date"
              className="w-full rounded border border-border bg-paper px-2 py-1 text-xs"
            />
          </div>
        </FilterSection>
      </div>
    </aside>
  );
}

function FilterSection({
  title,
  open,
  onToggle,
  children,
}: {
  title: string;
  open: boolean;
  onToggle: () => void;
  children: React.ReactNode;
}) {
  return (
    <div className="border-b border-border pb-4">
      <button
        onClick={onToggle}
        className="flex w-full items-center justify-between text-xs font-medium uppercase tracking-wide text-ink-muted"
      >
        {title}
        <span>{open ? "−" : "+"}</span>
      </button>
      {open && <div className="mt-3">{children}</div>}
    </div>
  );
}
