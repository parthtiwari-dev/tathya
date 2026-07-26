"use client";

import { useEffect, useState } from "react";
import { useLanguage } from "@/lib/i18n";
import { INTRO_FADE_DURATION_MS, INTRO_FADE_START_MS, INTRO_STORAGE_KEY, INTRO_TOTAL_MS } from "@/lib/introTiming";

const lines = {
  line1: { en: "We don't tell you who's right.", hi: "हम यह नहीं बताते कि सही कौन है।" },
  line2: {
    en: "We record what was said, who said it, and what's verifiable.",
    hi: "हम दर्ज करते हैं कि क्या कहा गया, किसने कहा, और क्या सत्यापन योग्य है।",
  },
};

export function IntroAnimation() {
  const { lang } = useLanguage();
  const [visible, setVisible] = useState(false);
  const [fading, setFading] = useState(false);

  useEffect(() => {
    const seen = window.localStorage.getItem(INTRO_STORAGE_KEY);
    if (seen) return;
    setVisible(true);
    const fadeTimer = setTimeout(() => setFading(true), INTRO_FADE_START_MS);
    const removeTimer = setTimeout(() => {
      setVisible(false);
      window.localStorage.setItem(INTRO_STORAGE_KEY, "1");
    }, INTRO_TOTAL_MS);
    return () => {
      clearTimeout(fadeTimer);
      clearTimeout(removeTimer);
    };
  }, []);

  if (!visible) return null;

  return (
    <div
      className={`fixed inset-0 z-50 flex items-center justify-center bg-paper transition-opacity ease-out ${
        fading ? "opacity-0" : "opacity-100"
      }`}
      style={{ transitionDuration: `${INTRO_FADE_DURATION_MS}ms` }}
    >
      <div className="max-w-md px-6 text-center">
        <p className="animate-[fadeUp_0.7s_ease_forwards] font-serif text-2xl font-medium text-ink opacity-0 [animation-delay:0.1s] sm:text-3xl">
          {lines.line1[lang]}
        </p>
        <p className="mt-3 animate-[fadeUp_0.7s_ease_forwards] font-serif text-lg text-ink-secondary opacity-0 [animation-delay:0.6s] sm:text-xl">
          {lines.line2[lang]}
        </p>
      </div>
      <style>{`
        @keyframes fadeUp {
          from { opacity: 0; transform: translateY(8px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </div>
  );
}
