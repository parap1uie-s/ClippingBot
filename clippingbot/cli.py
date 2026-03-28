from __future__ import annotations

import argparse

from .config import load_settings
from .models import ClipRequest
from .processor import ClipProcessor


def main() -> None:
    parser = argparse.ArgumentParser(description="Save a shared URL into an Obsidian vault.")
    parser.add_argument("text", help="Natural language text containing a URL")
    parser.add_argument("--source", default="manual", help="Source label written into the note")
    args = parser.parse_args()

    settings = load_settings()
    saved = ClipProcessor(settings).process(ClipRequest(raw_text=args.text, source=args.source))
    print(saved.path)


if __name__ == "__main__":
    main()

