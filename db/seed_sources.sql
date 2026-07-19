-- Seed the initial source registry. Re-running this is safe.
insert into sources (source_key, name, type, url, trust_category, enabled) values
  ('pib-press-releases', 'Press Information Bureau — Press Releases', 'pib', 'https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=5', 'official', false),
  ('indian-express-india', 'The Indian Express — India', 'rss', 'https://indianexpress.com/section/india/feed/', 'media', true),
  ('the-wire', 'The Wire', 'rss', 'https://thewire.in/feed/', 'media', false)
on conflict (source_key) do update
set name = excluded.name,
    type = excluded.type,
    url = excluded.url,
    trust_category = excluded.trust_category,
    enabled = excluded.enabled;
