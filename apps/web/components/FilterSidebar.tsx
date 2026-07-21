"use client";

type Ministry = { slug: string; name: string };

export function FilterSidebar({
  ministries,
  selectedMinistries,
  onToggleMinistry,
  selectedStatuses,
  onToggleStatus,
  dateFrom,
  dateTo,
  onDateFromChange,
  onDateToChange,
  onReset,
}: {
  ministries: Ministry[];
  selectedMinistries: string[];
  onToggleMinistry: (slug: string) => void;
  selectedStatuses: string[];
  onToggleStatus: (status: string) => void;
  dateFrom: string;
  dateTo: string;
  onDateFromChange: (value: string) => void;
  onDateToChange: (value: string) => void;
  onReset: () => void;
}) {
  const hasActiveFilters =
    selectedMinistries.length > 0 || selectedStatuses.length > 0 || dateFrom !== "" || dateTo !== "";

  return (
    <aside className="hidden w-56 shrink-0 lg:block">
      <div className="sticky top-24 space-y-6 text-sm">
        {hasActiveFilters && (
          <button onClick={onReset} className="text-xs text-accent hover:underline">
            Clear all filters
          </button>
        )}

        <FilterSection title="Ministry">
          <ul className="space-y-1.5">
            {ministries.map((ministry) => (
              <li key={ministry.slug}>
                <label className="flex items-center gap-2 text-ink-secondary">
                  <input
                    type="checkbox"
                    className="accent-[var(--accent)]"
                    checked={selectedMinistries.includes(ministry.slug)}
                    onChange={() => onToggleMinistry(ministry.slug)}
                  />
                  {ministry.name}
                </label>
              </li>
            ))}
          </ul>
        </FilterSection>

        <FilterSection title="Status">
          <ul className="space-y-1.5">
            {["live", "archived"].map((status) => (
              <li key={status} className="text-ink-secondary">
                <label className="flex items-center gap-2 capitalize">
                  <input
                    type="checkbox"
                    className="accent-[var(--accent)]"
                    checked={selectedStatuses.includes(status)}
                    onChange={() => onToggleStatus(status)}
                  />
                  {status}
                </label>
              </li>
            ))}
          </ul>
        </FilterSection>

        <FilterSection title="Date range">
          <div className="space-y-2 text-ink-secondary">
            <label className="block text-xs text-ink-muted">From</label>
            <input
              type="date"
              value={dateFrom}
              onChange={(e) => onDateFromChange(e.target.value)}
              className="w-full rounded border border-border bg-paper px-2 py-1 text-xs"
            />
            <label className="block text-xs text-ink-muted">To</label>
            <input
              type="date"
              value={dateTo}
              onChange={(e) => onDateToChange(e.target.value)}
              className="w-full rounded border border-border bg-paper px-2 py-1 text-xs"
            />
          </div>
        </FilterSection>
      </div>
    </aside>
  );
}

function FilterSection({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="border-b border-border pb-4">
      <p className="text-xs font-medium uppercase tracking-wide text-ink-muted">{title}</p>
      <div className="mt-3">{children}</div>
    </div>
  );
}
