"""Phase 0 source registry.

Only source configuration belongs here; topics must never be added manually.
RSS endpoint URLs are intentionally not guessed. Populate a source only after its
publisher-confirmed RSS endpoint has been verified in the next implementation loop.
"""

from shared.models import SourceDefinition


STARTER_SOURCES: tuple[SourceDefinition, ...] = ()
ARCHIVE_AFTER_DAYS = 60
