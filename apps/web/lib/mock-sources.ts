import type { Source } from "./types";

// Mirrors shared/config.py source_key values from the actual pipeline so the
// Source Explorer reflects the real registry, not invented names.
export const sources: Source[] = [
  { sourceKey: "indian-express-india", name: "Indian Express", type: "rss", trustCategory: "media", url: "https://indianexpress.com/section/india/feed/", enabled: true },
  { sourceKey: "hindustan-times-india", name: "Hindustan Times", type: "rss", trustCategory: "media", url: "https://www.hindustantimes.com/feeds/rss/india-news/rssfeed.xml", enabled: true },
  { sourceKey: "rbi-press-releases", name: "RBI Press Releases", type: "official_website", trustCategory: "official", url: "https://www.rbi.org.in/", enabled: true },
  { sourceKey: "pmo-youtube", name: "PMO (YouTube)", type: "youtube", trustCategory: "official", url: "https://www.youtube.com/feeds/videos.xml?channel_id=UCDS9hpqUEXsXUIcf0qDcBIA", enabled: false },
  { sourceKey: "pib-press-releases", name: "PIB Press Releases", type: "pib", trustCategory: "official", url: "https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=1", enabled: false },
  { sourceKey: "lok-sabha-questions", name: "Lok Sabha Q&A", type: "parliament", trustCategory: "official", url: "https://sansad.in/ls/questions/questions-and-answers", enabled: false },
  { sourceKey: "rajya-sabha-questions", name: "Rajya Sabha Q&A", type: "parliament", trustCategory: "official", url: "https://sansad.in/rs/questions/questions-and-answers", enabled: false },
  { sourceKey: "scroll-in", name: "Scroll.in", type: "rss", trustCategory: "media", url: "https://scroll.in/latest.rss", enabled: false },
  { sourceKey: "times-of-india-india", name: "Times of India", type: "rss", trustCategory: "media", url: "https://timesofindia.indiatimes.com/rssfeeds/-2128936835.cms", enabled: false },
  { sourceKey: "the-wire", name: "The Wire", type: "rss", trustCategory: "media", url: "https://thewire.in/feed/", enabled: false },
  { sourceKey: "ndtv-india", name: "NDTV", type: "rss", trustCategory: "media", url: "https://feeds.feedburner.com/ndtvnews-india-news", enabled: false },
  { sourceKey: "bbc-world", name: "BBC World", type: "rss", trustCategory: "foreign", url: "http://feeds.bbci.co.uk/news/world/rss.xml", enabled: false },
  { sourceKey: "guardian-world", name: "The Guardian", type: "rss", trustCategory: "foreign", url: "https://www.theguardian.com/world/rss", enabled: false },
];

export function getSourceByKey(sourceKey: string): Source | undefined {
  return sources.find((s) => s.sourceKey === sourceKey);
}
