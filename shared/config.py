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
)
ARCHIVE_AFTER_DAYS = 60
