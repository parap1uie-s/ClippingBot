from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .config import Settings
from .models import ExtractedClip, SavedClip
from .text import make_note_title, short_url_hash, slugify, strip_markdown_title


def render_note(settings: Settings, extracted: ExtractedClip, markdown: str, source: str) -> tuple[str, str]:
    markdown_title = strip_markdown_title(markdown)
    title = make_note_title(extracted.share_title, markdown_title, extracted.url)
    clipped_at = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")

    frontmatter = {
        "title": title,
        "source_url": extracted.url,
        "clipped_from": source,
        "clipped_at": clipped_at,
        "share_text": extracted.share_text,
        "tags": list(settings.note_tags),
    }

    body = [
        "---",
        *[f"{key}: {json.dumps(value, ensure_ascii=False)}" for key, value in frontmatter.items()],
        "---",
        "",
        "## Source",
        "",
        f"- URL: {extracted.url}",
        f"- Shared via: {source}",
        "",
        "## Captured Markdown",
        "",
        markdown.strip(),
        "",
    ]
    return title, "\n".join(body)


def save_note(settings: Settings, output_dir: Path, extracted: ExtractedClip, markdown: str, source: str) -> SavedClip:
    output_dir.mkdir(parents=True, exist_ok=True)
    title, note_text = render_note(settings, extracted, markdown, source)
    filename = f"{slugify(title, max_length=settings.filename_max_length)}-{short_url_hash(extracted.url)}.md"
    path = output_dir / filename
    created = not path.exists()
    if path.exists() and not settings.note_overwrite_existing:
        return SavedClip(path=path, title=title, url=extracted.url, created=False)
    path.write_text(note_text, encoding="utf-8")
    return SavedClip(path=path, title=title, url=extracted.url, created=created)
