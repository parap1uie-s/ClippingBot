from __future__ import annotations

import hashlib
import re
import unicodedata
from datetime import datetime
from urllib.parse import urlparse

from .models import ExtractedClip


URL_RE = re.compile(r"https?://[^\s<>\"]+")


def extract_clip(raw_text: str) -> ExtractedClip:
    match = URL_RE.search(raw_text)
    if not match:
        raise ValueError("No URL found in incoming text")

    url = match.group(0).rstrip(").,]")
    share_text = " ".join(raw_text.split()).strip()
    prefix = share_text[: match.start()].strip()
    suffix = share_text[match.end() :].strip()
    title = prefix or suffix or None
    return ExtractedClip(url=url, share_text=share_text, share_title=title)


def strip_markdown_title(markdown: str) -> str | None:
    for line in markdown.splitlines():
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
    return None


def make_note_title(share_title: str | None, markdown_title: str | None, url: str) -> str:
    if share_title:
        return share_title
    if markdown_title:
        return markdown_title

    host = urlparse(url).netloc or "clip"
    return f"{host} {datetime.now().strftime('%Y-%m-%d %H-%M-%S')}"


def slugify(value: str, max_length: int = 72) -> str:
    normalized = unicodedata.normalize("NFKC", value)
    safe = re.sub(r"[^\w\s-]", "", normalized, flags=re.UNICODE)
    safe = re.sub(r"[-\s]+", "-", safe.strip(), flags=re.UNICODE).strip("-").lower()
    if not safe:
        safe = "clip"
    return safe[:max_length].rstrip("-")


def short_url_hash(url: str) -> str:
    return hashlib.sha1(url.encode("utf-8")).hexdigest()[:10]

