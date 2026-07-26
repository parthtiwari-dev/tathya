"use client";

import { useMemo, useState } from "react";
import { SlidersHorizontal, X } from "lucide-react";
import type { TopicSummary } from "@/lib/types";
import { FilterSidebar } from "@/components/FilterSidebar";
import { FeedItem } from "@/components/FeedItem";
import { FeedBento } from "@/components/FeedBento";
import { useTranslations } from "@/lib/i18n";

export function FeedExplorer({
  topics,
  ministries,
}: {
  topics: TopicSummary[];
  ministries: { slug: string; name: string }[];
}) {
  const t = useTranslations();
  const [selectedMinistries, setSelectedMinistries] = useState<string[]>([]);
  const [selectedStatuses, setSelectedStatuses] = useState<string[]>([]);
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [filtersOpen, setFiltersOpen] = useState(false);

  function toggleMinistry(slug: string) {
    setSelectedMinistries((prev) => (prev.includes(slug) ? prev.filter((s) => s !== slug) : [...prev, slug]));
  }

  function toggleStatus(status: string) {
    setSelectedStatuses((prev) => (prev.includes(status) ? prev.filter((s) => s !== status) : [...prev, status]));
  }

  function reset() {
    setSelectedMinistries([]);
    setSelectedStatuses([]);
    setDateFrom("");
    setDateTo("");
  }

  const filtered = useMemo(() => {
    return topics.filter((topic) => {
      if (selectedMinistries.length > 0 && !selectedMinistries.includes(topic.ministrySlug)) return false;
      if (selectedStatuses.length > 0 && !selectedStatuses.includes(topic.status)) return false;
      if (dateFrom && topic.lastSignalAt < dateFrom) return false;
      if (dateTo && topic.lastSignalAt > `${dateTo}T23:59:59`) return false;
      return true;
    });
  }, [topics, selectedMinistries, selectedStatuses, dateFrom, dateTo]);

  const liveTopics = filtered.filter((topic) => topic.status !== "archived");
  const archivedTopics = filtered.filter((topic) => topic.status === "archived");
  const activeFilterCount = selectedMinistries.length + selectedStatuses.length + (dateFrom ? 1 : 0) + (dateTo ? 1 : 0);

  const filterProps = {
    ministries,
    selectedMinistries,
    onToggleMinistry: toggleMinistry,
    selectedStatuses,
    onToggleStatus: toggleStatus,
    dateFrom,
    dateTo,
    onDateFromChange: setDateFrom,
    onDateToChange: setDateTo,
    onReset: reset,
  };

  return (
    <div className="py-8 sm:py-10">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="font-serif text-2xl font-medium text-ink">{t("homeTitle")}</h1>
          <p className="mt-1 text-sm text-ink-secondary">{t("homeSubtitle")}</p>
        </div>
        <button
          onClick={() => setFiltersOpen(true)}
          className="flex shrink-0 items-center gap-1.5 rounded-full border border-border px-3 py-1.5 text-xs text-ink-secondary transition-colors hover:border-ink-muted"
        >
          <SlidersHorizontal size={13} />
          {t("filtersButton")}
          {activeFilterCount > 0 && (
            <span className="flex h-4 w-4 items-center justify-center rounded-full bg-accent text-[10px] font-medium text-paper">
              {activeFilterCount}
            </span>
          )}
        </button>
      </div>

      <div className="mt-8">
        {filtered.length === 0 ? (
          <p className="text-sm text-ink-muted">{t("noTopicsMatch")}</p>
        ) : (
          <>
            {liveTopics.length > 0 && <FeedBento topics={liveTopics} />}
            {archivedTopics.length > 0 && (
              <div>
                <p className="mb-2 mt-10 text-xs font-medium uppercase tracking-wide text-ink-muted">
                  {t("archivedSection")}
                </p>
                {archivedTopics.map((topic) => (
                  <FeedItem key={topic.id} topic={topic} />
                ))}
              </div>
            )}
          </>
        )}
      </div>

      {filtersOpen && (
        <div className="fixed inset-0 z-50 flex justify-end bg-black/30">
          <div className="h-full w-full max-w-xs overflow-y-auto bg-paper p-5 shadow-xl">
            <div className="mb-4 flex items-center justify-between">
              <p className="text-sm font-medium text-ink">{t("filtersButton")}</p>
              <button onClick={() => setFiltersOpen(false)} aria-label={t("closeFilters")}>
                <X size={18} className="text-ink-secondary" />
              </button>
            </div>
            <FilterSidebar {...filterProps} />
          </div>
        </div>
      )}
    </div>
  );
}
