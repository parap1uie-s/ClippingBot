from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ClipRequest:
    raw_text: str
    source: str
    external_id: str | None = None
    reply_target: str | None = None


@dataclass(frozen=True)
class ExtractedClip:
    url: str
    share_text: str
    share_title: str | None


@dataclass(frozen=True)
class CrawlMarkdownResult:
    url: str
    markdown: str
    success: bool
    filter_name: str


@dataclass(frozen=True)
class SavedClip:
    path: Path
    title: str
    url: str
    created: bool
