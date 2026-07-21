"use client";

import { createContext, useContext, useEffect, useState } from "react";

export type Lang = "en" | "hi";

type Dictionary = Record<string, { en: string; hi: string }>;

export const dict: Dictionary = {
  searchPlaceholder: { en: "Search topics, people, ministries…", hi: "विषय, लोग, मंत्रालय खोजें…" },
  navSources: { en: "Sources", hi: "स्रोत" },
  navAbout: { en: "About", hi: "परिचय" },
  footerTagline: {
    en: "Tathya is an autonomous record, not a news outlet. No topic is chosen by hand. Every claim links to its source.",
    hi: "तथ्य एक स्वचालित अभिलेख है, समाचार संस्थान नहीं। कोई भी विषय हाथ से नहीं चुना जाता। हर दावा अपने स्रोत से जुड़ा है।",
  },
  homeTitle: { en: "The Record", hi: "अभिलेख" },
  homeSubtitle: {
    en: "Topics emerge automatically from configured sources. No topic on this feed was chosen by hand.",
    hi: "विषय कॉन्फ़िगर किए गए स्रोतों से स्वतः उभरते हैं। इस फ़ीड में कोई भी विषय हाथ से नहीं चुना गया।",
  },
  clearFilters: { en: "Clear all filters", hi: "सभी फ़िल्टर हटाएं" },
  filterMinistry: { en: "Ministry", hi: "मंत्रालय" },
  filterStatus: { en: "Status", hi: "स्थिति" },
  filterDateRange: { en: "Date range", hi: "दिनांक सीमा" },
  filterFrom: { en: "From", hi: "से" },
  filterTo: { en: "To", hi: "तक" },
  noTopicsMatch: { en: "No topics match these filters.", hi: "इन फ़िल्टर से कोई विषय मेल नहीं खाता।" },
  statusLive: { en: "Live", hi: "सक्रिय" },
  statusArchived: { en: "Archived", hi: "संग्रहीत" },
  statusDraft: { en: "Draft", hi: "मसौदा" },
  sourceOfficial: { en: "official", hi: "सरकारी" },
  sourceMedia: { en: "media", hi: "मीडिया" },
  sourceCitizen: { en: "citizen", hi: "नागरिक" },
  timelineHeading: { en: "Timeline", hi: "समयरेखा" },
  claimsHeading: { en: "Claims Ledger", hi: "दावा लेजर" },
  claimsSubheading: {
    en: "What each side said, side by side. No verdict — only who said it and where.",
    hi: "हर पक्ष ने क्या कहा, साथ-साथ। कोई फैसला नहीं — केवल किसने और कहाँ कहा।",
  },
  govSays: { en: "Government Says", hi: "सरकार का कहना है" },
  oppositionSays: { en: "Opposition Says", hi: "विपक्ष का कहना है" },
  mediaReports: { en: "Independent Media Reports", hi: "स्वतंत्र मीडिया रिपोर्ट" },
  citizensSay: { en: "Citizens & Protesters Say", hi: "नागरिक और प्रदर्शनकारी कहते हैं" },
  factsHeading: { en: "Verifiable Facts", hi: "सत्यापन योग्य तथ्य" },
  factsSubheading: {
    en: "Checked against primary government documents only — not a claim, a confirmed record.",
    hi: "केवल प्राथमिक सरकारी दस्तावेज़ों से सत्यापित — यह दावा नहीं, एक पुष्ट अभिलेख है।",
  },
  contradictionsHeading: { en: "Statements Over Time", hi: "समय के साथ बयान" },
  contradictionsSubheading: {
    en: "The same entity, at two different points — shown side by side, no verdict on which is right.",
    hi: "एक ही पक्ष, दो अलग समयों पर — साथ-साथ दिखाया गया, कौन सही है इस पर कोई फैसला नहीं।",
  },
  openQuestionsHeading: { en: "Open Questions", hi: "अनुत्तरित प्रश्न" },
  openQuestionsSubheading: {
    en: "Gaps between what has been claimed and what is independently verified so far — not an accusation, a status.",
    hi: "अब तक जो दावा किया गया और जो स्वतंत्र रूप से सत्यापित है, उसके बीच का अंतर — यह आरोप नहीं, एक स्थिति है।",
  },
  relatedHeading: { en: "Related Topics", hi: "संबंधित विषय" },
  sourcesUsedHeading: { en: "Sources in this case file", hi: "इस केस फ़ाइल में स्रोत" },
  historyHeading: { en: "History — every addition and correction, never rewritten", hi: "इतिहास — हर जोड़ और सुधार, कभी फिर से नहीं लिखा गया" },
  reportIssue: { en: "Report an extraction issue", hi: "निष्कर्षण त्रुटि की रिपोर्ट करें" },
  contentNotTranslated: {
    en: "This topic's content (summary, claims, quotes) is only available in English right now. Hindi case-file generation is a later phase.",
    hi: "इस विषय की सामग्री (सारांश, दावे, उद्धरण) अभी केवल अंग्रेज़ी में उपलब्ध है। हिंदी केस-फ़ाइल जनरेशन बाद के चरण में आएगी।",
  },
  introLine1: { en: "We don't tell you who's right.", hi: "हम यह नहीं बताते कि सही कौन है।" },
  introLine2: {
    en: "We record what was said, who said it, and what's verifiable.",
    hi: "हम दर्ज करते हैं कि क्या कहा गया, किसने कहा, और क्या सत्यापन योग्य है।",
  },
  filtersButton: { en: "Filters", hi: "फ़िल्टर" },
  closeFilters: { en: "Close", hi: "बंद करें" },
  liveSection: { en: "Live", hi: "सक्रिय" },
  archivedSection: { en: "Archived", hi: "संग्रहीत" },
};

export function useTranslations() {
  const { lang } = useLanguage();
  return function t(key: keyof typeof dict): string {
    return dict[key]?.[lang] ?? dict[key]?.en ?? key;
  };
}

const STORAGE_KEY = "tathya-lang";

const LanguageContext = createContext<{ lang: Lang; setLang: (l: Lang) => void }>({
  lang: "en",
  setLang: () => {},
});

export function LanguageProvider({ children }: { children: React.ReactNode }) {
  const [lang, setLangState] = useState<Lang>("en");

  useEffect(() => {
    const stored = window.localStorage.getItem(STORAGE_KEY) as Lang | null;
    if (stored === "hi" || stored === "en") {
      setLangState(stored);
      document.documentElement.lang = stored;
    }
  }, []);

  function setLang(next: Lang) {
    setLangState(next);
    document.documentElement.lang = next;
    window.localStorage.setItem(STORAGE_KEY, next);
  }

  return (
    <LanguageContext.Provider value={{ lang, setLang }}>{children}</LanguageContext.Provider>
  );
}

export function useLanguage() {
  return useContext(LanguageContext);
}
