"""Phase 0 source registry.

Only source configuration belongs here; topics must never be added manually.
The initial endpoints are publisher-exposed feeds verified on 19 July 2026.
"""

from shared.models import SourceDefinition, SourceType, TrustCategory


STARTER_SOURCES: tuple[SourceDefinition, ...] = (
    SourceDefinition(
        key="pib-press-releases",
        name="Press Information Bureau — Press Releases",
        type=SourceType.PIB,
        url="https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=5",
        trust_category=TrustCategory.OFFICIAL,
        enabled=False,
    ),
    SourceDefinition(
        key="indian-express-india",
        name="The Indian Express — India",
        type=SourceType.RSS,
        url="https://indianexpress.com/section/india/feed/",
        trust_category=TrustCategory.MEDIA,
    ),
    SourceDefinition(
        key="the-wire",
        name="The Wire",
        type=SourceType.RSS,
        url="https://thewire.in/feed/",
        trust_category=TrustCategory.MEDIA,
        # The publisher currently returns non-feed content to the transparent
        # watcher user-agent. Keep it registered but do not poll it until the
        # dedicated source adapter has a compliant resolution.
        enabled=False,
    ),
    SourceDefinition(
        key="ndtv-india",
        name="NDTV — India",
        type=SourceType.RSS,
        url="https://feeds.feedburner.com/ndtvnews-india-news",
        trust_category=TrustCategory.MEDIA,
        # Publisher terms require a licensing/use review before public reuse.
        enabled=False,
    ),
    SourceDefinition(
        key="guardian-world",
        name="The Guardian — World",
        type=SourceType.RSS,
        url="https://www.theguardian.com/world/rss",
        trust_category=TrustCategory.FOREIGN,
        # Public snapshotting requires a licensing/use review.
        enabled=False,
    ),
    SourceDefinition(
        key="lok-sabha-questions",
        name="Lok Sabha — Questions and Answers",
        type=SourceType.PARLIAMENT,
        url="https://sansad.in/ls/questions/questions-and-answers",
        trust_category=TrustCategory.OFFICIAL,
        enabled=False,
    ),
    SourceDefinition(
        key="rajya-sabha-questions",
        name="Rajya Sabha — Questions and Answers",
        type=SourceType.PARLIAMENT,
        url="https://sansad.in/rs/questions/questions-and-answers",
        trust_category=TrustCategory.OFFICIAL,
        enabled=False,
    ),
)
ARCHIVE_AFTER_DAYS = 60
