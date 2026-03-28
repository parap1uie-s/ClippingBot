from __future__ import annotations

from .config import Settings
from .crawl4ai_client import Crawl4AIClient
from .models import ClipRequest, SavedClip
from .note_writer import save_note
from .text import extract_clip


class ClipProcessor:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._crawl4ai = Crawl4AIClient(settings)

    def process(self, request: ClipRequest) -> SavedClip:
        extracted = extract_clip(request.raw_text)
        result = self._crawl4ai.fetch_markdown(extracted.url, filter_name=self._settings.crawl4ai_filter)
        if not result.success or not result.markdown.strip():
            raise RuntimeError(f"Crawl4AI returned empty markdown for {extracted.url}")
        return save_note(self._settings, self._settings.obsidian_output_dir, extracted, result.markdown, request.source)
