-- Seed the initial source registry. Re-running this is safe.
insert into sources (source_key, name, type, url, trust_category, enabled) values
  ('pib-press-releases', 'Press Information Bureau — Press Releases', 'pib', 'https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=5', 'official', false),
  ('indian-express-india', 'The Indian Express — India', 'rss', 'https://indianexpress.com/section/india/feed/', 'media', true),
  ('the-wire', 'The Wire', 'rss', 'https://thewire.in/feed/', 'media', false),
  ('ndtv-india', 'NDTV — India', 'rss', 'https://feeds.feedburner.com/ndtvnews-india-news', 'media', false),
  ('guardian-world', 'The Guardian — World', 'rss', 'https://www.theguardian.com/world/rss', 'foreign', false),
  ('lok-sabha-questions', 'Lok Sabha — Questions and Answers', 'parliament', 'https://sansad.in/ls/questions/questions-and-answers', 'official', false),
  ('rajya-sabha-questions', 'Rajya Sabha — Questions and Answers', 'parliament', 'https://sansad.in/rs/questions/questions-and-answers', 'official', false)
on conflict (source_key) do update
set name = excluded.name,
    type = excluded.type,
    url = excluded.url,
    trust_category = excluded.trust_category,
    enabled = excluded.enabled;
