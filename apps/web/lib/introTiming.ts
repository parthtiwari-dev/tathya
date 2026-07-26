// Shared timing constants for the first-visit intro overlay (IntroAnimation)
// and anything on the homepage that wants to time its own entrance to line
// up with the intro fading away (e.g. FeedBento's staggered reveal).
// Keeping these in one place avoids two components silently drifting out
// of sync if either timing is ever tuned.

export const INTRO_STORAGE_KEY = "tathya-intro-seen";
export const INTRO_FADE_START_MS = 2200;
export const INTRO_FADE_DURATION_MS = 600;
export const INTRO_TOTAL_MS = INTRO_FADE_START_MS + INTRO_FADE_DURATION_MS;

export function hasSeenIntro(): boolean {
  if (typeof window === "undefined") return true;
  return window.localStorage.getItem(INTRO_STORAGE_KEY) === "1";
}
