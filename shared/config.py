"""Phase 0 source registry.

Only source configuration belongs here; topics must never be added manually.
Endpoints below are source-level watch points. Most are deliberately disabled
until their adapter, terms posture, timestamps, and snapshots are manually
verified.
"""

from shared.models import SourceDefinition, SourceType, TrustCategory


STARTER_SOURCES: tuple[SourceDefinition, ...] = (
    SourceDefinition(
        key="pib-press-releases",
        name="Press Information Bureau - Press Releases",
        type=SourceType.PIB,
        url="https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=1",
        trust_category=TrustCategory.OFFICIAL,
        enabled=False,
    ),
    SourceDefinition(
        key="pmo-youtube",
        name="PMO India - YouTube",
        type=SourceType.YOUTUBE,
        url="https://www.youtube.com/feeds/videos.xml?channel_id=UCDS9hpqUEXsXUIcf0qDcBIA",
        trust_category=TrustCategory.OFFICIAL,
        enabled=False,
    ),
    SourceDefinition(
        key="pmindia-news-updates",
        name="Prime Minister of India - News Updates",
        type=SourceType.OFFICIAL_WEBSITE,
        url="https://www.pmindia.gov.in/en/news-updates/",
        trust_category=TrustCategory.OFFICIAL,
        enabled=False,
    ),
    SourceDefinition(
        key="income-tax-press-releases",
        name="Income Tax Department - Press Releases",
        type=SourceType.RSS,
        url="https://www.incometaxindia.gov.in/press-release-rss-feed/-/asset_publisher/bxhj/rss",
        trust_category=TrustCategory.OFFICIAL,
        enabled=False,
    ),
    SourceDefinition(
        key="rbi-press-releases",
        name="Reserve Bank of India - Press Releases",
        type=SourceType.RSS,
        url="https://www.rbi.org.in/pressreleases_rss.xml",
        trust_category=TrustCategory.OFFICIAL,
    ),
    SourceDefinition(
        key="indian-express-india",
        name="The Indian Express - India",
        type=SourceType.RSS,
        url="https://indianexpress.com/section/india/feed/",
        trust_category=TrustCategory.MEDIA,
    ),
    SourceDefinition(
        key="hindustan-times-india",
        name="Hindustan Times - India",
        type=SourceType.RSS,
        url="https://www.hindustantimes.com/feeds/rss/india-news/rssfeed.xml",
        trust_category=TrustCategory.MEDIA,
    ),
    SourceDefinition(
        key="the-wire",
        name="The Wire",
        type=SourceType.RSS,
        url="https://thewire.in/feed/",
        trust_category=TrustCategory.MEDIA,
        enabled=False,
    ),
    SourceDefinition(
        key="scroll-in",
        name="Scroll.in",
        type=SourceType.RSS,
        url="https://scroll.in/latest.rss",
        trust_category=TrustCategory.MEDIA,
        enabled=False,
    ),
    SourceDefinition(
        key="ndtv-india",
        name="NDTV - India",
        type=SourceType.RSS,
        url="https://feeds.feedburner.com/ndtvnews-india-news",
        trust_category=TrustCategory.MEDIA,
        enabled=False,
    ),
    SourceDefinition(
        key="times-of-india-india",
        name="Times of India - India",
        type=SourceType.RSS,
        url="https://timesofindia.indiatimes.com/rssfeeds/-2128936835.cms",
        trust_category=TrustCategory.MEDIA,
        enabled=False,
    ),
    SourceDefinition(
        key="guardian-world",
        name="The Guardian - World",
        type=SourceType.RSS,
        url="https://www.theguardian.com/world/rss",
        trust_category=TrustCategory.FOREIGN,
        enabled=False,
    ),
    SourceDefinition(
        key="bbc-world",
        name="BBC News - World",
        type=SourceType.RSS,
        url="http://feeds.bbci.co.uk/news/world/rss.xml",
        trust_category=TrustCategory.FOREIGN,
        enabled=False,
    ),
    SourceDefinition(
        key="lok-sabha-questions",
        name="Lok Sabha - Questions and Answers",
        type=SourceType.PARLIAMENT,
        url="https://sansad.in/ls/questions/questions-and-answers",
        trust_category=TrustCategory.OFFICIAL,
        enabled=False,
    ),
    SourceDefinition(
        key="rajya-sabha-questions",
        name="Rajya Sabha - Questions and Answers",
        type=SourceType.PARLIAMENT,
        url="https://sansad.in/rs/questions/questions-and-answers",
        trust_category=TrustCategory.OFFICIAL,
        enabled=False,
    ),
)

ARCHIVE_AFTER_DAYS = 60
