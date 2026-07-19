-- Seed the source registry. Re-running this is safe.
insert into sources (source_key, name, type, url, trust_category, enabled) values
  ('pib-press-releases', 'Press Information Bureau - Press Releases', 'pib', 'https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=1', 'official', false),
  ('pmo-youtube', 'PMO India - YouTube', 'youtube', 'https://www.youtube.com/feeds/videos.xml?channel_id=UCDS9hpqUEXsXUIcf0qDcBIA', 'official', false),
  ('pmindia-news-updates', 'Prime Minister of India - News Updates', 'official_website', 'https://www.pmindia.gov.in/en/news-updates/', 'official', false),
  ('indian-express-india', 'The Indian Express - India', 'rss', 'https://indianexpress.com/section/india/feed/', 'media', true),
  ('hindustan-times-india', 'Hindustan Times - India', 'rss', 'https://www.hindustantimes.com/feeds/rss/india-news/rssfeed.xml', 'media', true),
  ('the-wire', 'The Wire', 'rss', 'https://thewire.in/feed/', 'media', false),
  ('scroll-in', 'Scroll.in', 'rss', 'https://scroll.in/latest.rss', 'media', false),
  ('ndtv-india', 'NDTV - India', 'rss', 'https://feeds.feedburner.com/ndtvnews-india-news', 'media', false),
  ('times-of-india-india', 'Times of India - India', 'rss', 'https://timesofindia.indiatimes.com/rssfeeds/-2128936835.cms', 'media', false),
  ('guardian-world', 'The Guardian - World', 'rss', 'https://www.theguardian.com/world/rss', 'foreign', false),
  ('bbc-world', 'BBC News - World', 'rss', 'http://feeds.bbci.co.uk/news/world/rss.xml', 'foreign', false),
  ('lok-sabha-questions', 'Lok Sabha - Questions and Answers', 'parliament', 'https://sansad.in/ls/questions/questions-and-answers', 'official', false),
  ('rajya-sabha-questions', 'Rajya Sabha - Questions and Answers', 'parliament', 'https://sansad.in/rs/questions/questions-and-answers', 'official', false)
on conflict (source_key) do update
set name = excluded.name,
    type = excluded.type,
    url = excluded.url,
    trust_category = excluded.trust_category,
    enabled = excluded.enabled;
