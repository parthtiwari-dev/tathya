"use client";

import { useMemo, useState } from "react";
import type { TopicSummary } from "@/lib/types";
import { FilterSidebar } from "@/components/FilterSidebar";
import { FeedItem } from "@/components/FeedItem";

export function FeedExplorer({
  topics,
  ministries,
}: {
  topics: TopicSummary[];
  ministries: { slug: string; name: string }[];
}) {
  const [selectedMinistries, setSelectedMinistries] = useState<string[]>([]);
  const [selectedStatuses, setSelectedStatuses] = useState<string[]>([]);
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");

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

  return (
    <div className="flex gap-10 py-10">
      <FilterSidebar
        ministries={ministries}
        selectedMinistries={selectedMinistries}
        onToggleMinistry={toggleMinistry}
        selectedStatuses={selectedStatuses}
        onToggleStatus={toggleStatus}
        dateFrom={dateFrom}
        dateTo={dateTo}
        onDateFromChange={setDateFrom}
        onDateToChange={setDateTo}
        onReset={reset}
      />
      <div className="min-w-0 flex-1">
        <h1 className="font-serif text-2xl font-medium text-ink">The Record</h1>
        <p className="mt-1 text-sm text-ink-secondary">
          Topics emerge automatically from configured sources. No topic on this feed was chosen by hand.
        </p>

        <div className="mt-8">
          {filtered.length === 0 ? (
            <p className="text-sm text-ink-muted">No topics match these filters.</p>
          ) : (
            filtered.map((topic) => <FeedItem key={topic.id} topic={topic} />)
          )}
        </div>
      </div>
    </div>
  );
}
