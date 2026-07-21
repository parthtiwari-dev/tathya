"use client";

import { useEffect, useState } from "react";

const STORAGE_KEY = "tathya-intro-seen";

export function IntroAnimation() {
  const [visible, setVisible] = useState(false);
  const [fading, setFading] = useState(false);

  useEffect(() => {
    const seen = window.localStorage.getItem(STORAGE_KEY);
    if (seen) return;
    setVisible(true);
    const fadeTimer = setTimeout(() => setFading(true), 2200);
    const removeTimer = setTimeout(() => {
      setVisible(false);
      window.localStorage.setItem(STORAGE_KEY, "1");
    }, 2800);
    return () => {
      clearTimeout(fadeTimer);
      clearTimeout(removeTimer);
    };
  }, []);

  if (!visible) return null;

  return (
    <div
      className={`fixed inset-0 z-50 flex items-center justify-center bg-paper transition-opacity duration-600 ${
        fading ? "opacity-0" : "opacity-100"
      }`}
    >
      <div className="max-w-md px-6 text-center">
        <p className="animate-[fadeUp_0.7s_ease_forwards] font-serif text-2xl font-medium text-ink opacity-0 [animation-delay:0.1s] sm:text-3xl">
          We don&apos;t tell you who&apos;s right.
        </p>
        <p className="mt-3 animate-[fadeUp_0.7s_ease_forwards] font-serif text-lg text-ink-secondary opacity-0 [animation-delay:0.6s] sm:text-xl">
          We record what was said, who said it, and what&apos;s verifiable.
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
