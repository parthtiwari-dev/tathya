"""Single source-type dispatch point for the scheduled ingestion pipeline."""

from pipeline.ingestion.parliament_scraper import fetch_parliament_signals
from pipeline.ingestion.pib_scraper import fetch_pib_signals
from pipeline.ingestion.official_website import fetch_official_website_signals
from pipeline.ingestion.rss_watcher import fetch_rss_signals
from pipeline.ingestion.youtube_watcher import fetch_youtube_signals
from shared.models import IngestedSignal, SourceDefinition, SourceType


def fetch_signals(source: SourceDefinition) -> list[IngestedSignal]:
    match source.type:
        case SourceType.RSS:
            return fetch_rss_signals(source)
        case SourceType.PIB:
            return fetch_pib_signals(source)
        case SourceType.PARLIAMENT:
            return fetch_parliament_signals(source)
        case SourceType.YOUTUBE:
            return fetch_youtube_signals(source)
        case SourceType.OFFICIAL_WEBSITE:
            return fetch_official_website_signals(source)
        case _:
            raise NotImplementedError(f"No watcher is implemented for source type {source.type!s}")
