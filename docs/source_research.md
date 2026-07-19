# Source Research and Activation Register

Last checked: 19 July 2026. A listed source is not automatically an enabled watcher. Tathya stores immutable snapshots, so publisher terms and operational behavior must both be checked before activation.

| Source | Category | Endpoint / record page | State | Why |
|---|---|---|---|---|
| PIB press releases | Official | `https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=1` | Registered - blocked | Live audit reached the endpoint but received HTTP 403. Keep disabled until a compliant official endpoint or access path is confirmed. |
| PMO YouTube | Official | `https://www.youtube.com/feeds/videos.xml?channel_id=UCDS9hpqUEXsXUIcf0qDcBIA` | Registered - disabled | Live audit fetched 15 videos; sample captions were unavailable, so it is title-only unless a transcript fallback is added. |
| Lok Sabha Q&A | Official | `https://sansad.in/ls/questions/questions-and-answers` | Registered - disabled | Public facet-search record; current adapter only works if rows are server-rendered. |
| Rajya Sabha Q&A | Official | `https://sansad.in/rs/questions/questions-and-answers` | Registered - disabled | Public facet-search record; current adapter only works if rows are server-rendered. |
| Indian Express - India | Media | `https://indianexpress.com/section/india/feed/` | Enabled | Current live dry-run and persistence fetches succeed. |
| Hindustan Times - India | Media | `https://www.hindustantimes.com/feeds/rss/india-news/rssfeed.xml` | Registered - disabled, terms review | Live audit fetched 100 items with good URLs/timestamps but short summaries only; terms posture must be reviewed before public reuse/snapshot display. |
| The Wire | Media | `https://thewire.in/feed/` | Registered - disabled | The endpoint previously returned non-feed content to the transparent watcher. |
| Scroll.in | Media | `https://scroll.in/latest.rss` | Registered - disabled, adapter test | Candidate feed URL; verify live behavior and terms before enablement. |
| NDTV - India | Media | `https://feeds.feedburner.com/ndtvnews-india-news` | Registered - disabled, terms review | NDTV exposes this feed, but published terms need review before public snapshotting. |
| Times of India - India | Media | `https://timesofindia.indiatimes.com/rssfeeds/-2128936835.cms` | Registered - disabled, terms review | TOI documents RSS feeds but restricts use to personal/non-commercial contexts without permission. |
| The Guardian - World | Foreign | `https://www.theguardian.com/world/rss` | Registered - disabled, terms review | The Guardian documents this RSS endpoint; review before public snapshotting. |
| BBC News - World | Foreign | `http://feeds.bbci.co.uk/news/world/rss.xml` | Registered - disabled, terms review | BBC publishes feed endpoints under feed terms; review before public snapshotting. |

Do not add an individual story to this table or to `shared/config.py`. Tathya configures sources only.
