"use client";

import { useEffect, useState } from "react";
import type { TopicSummary } from "@/lib/types";
import { BentoCard, type BentoTier } from "@/components/BentoCard";
import { hasSeenIntro, INTRO_TOTAL_MS } from "@/lib/introTiming";

// Rank-based tiering rather than fixed score thresholds -- scales with
// however many live topics exist at any given moment instead of breaking
// once real score distributions look different from today's small dataset.
function tierForRank(rank: number): BentoTier {
  if (rank === 0) return "hero";
  if (rank <= 2) return "wide";
  return "compact";
}

export function FeedBento({ topics }: { topics: TopicSummary[] }) {
  const [revealed, setRevealed] = useState(false);

  useEffect(() => {
    // Returning visitor (intro already dismissed in a prior session): reveal
    // immediately, no reason to hold the grid back. First-time visitor: hold
    // until the intro overlay has fully faded, so the homepage feels like it
    // "opens" right as the intro finishes rather than having already been
    // sitting there underneath it the whole time.
    if (hasSeenIntro()) {
      setRevealed(true);
      return;
    }
    const timer = setTimeout(() => setRevealed(true), INTRO_TOTAL_MS + 50);
    return () => clearTimeout(timer);
  }, []);

  const ranked = [...topics].sort((a, b) => b.significanceScore - a.significanceScore);

  return (
    <div className="grid grid-cols-1 gap-4 [grid-auto-flow:dense] sm:grid-cols-2 lg:grid-cols-4">
      {ranked.map((topic, rank) => (
        <BentoCard key={topic.id} topic={topic} tier={tierForRank(rank)} index={rank} revealed={revealed} />
      ))}
    </div>
  );
}
