# ClippingBot

Turn Feishu bot messages into Markdown notes in your [Obsidian](https://obsidian.md) vault.

[中文文档](./README.zh-CN.md)

## Features

- Receive text messages that contain URLs
- Extract the first URL from the message body
- Fetch page content through [Crawl4AI](https://github.com/unclecode/crawl4ai)
- Save the result as a Markdown note with frontmatter
- Write notes directly into a local [Obsidian](https://obsidian.md)-compatible directory
- Run in Feishu long-connection mode
- Run in local HTTP server mode for debugging or custom automation
- Run one-off clipping jobs from the CLI
- Support [Crawl4AI](https://github.com/unclecode/crawl4ai) fallback strategies for problematic sites
- Deploy with Docker Compose

## How It Works

1. A message is sent to a Feishu bot, or posted to the local ingest endpoint.
2. ClippingBot extracts the first URL from the incoming text.
3. ClippingBot requests content from [Crawl4AI](https://github.com/unclecode/crawl4ai).
4. ClippingBot renders a Markdown note with metadata.
5. The note is written to the configured vault directory.

## Quick Start

### Local

```bash
git clone https://github.com/parap1uie-s/ClippingBot.git
cd ClippingBot
cp .env.example .env
python3 -m clippingbot.main
```

### CLI

```bash
python3 -m clippingbot.cli "Example Domain https://example.com"
```

### HTTP Ingest

```bash
curl -X POST 'http://127.0.0.1:8787/ingest' \
  -H 'Content-Type: application/json' \
  -d '{"text":"Example Domain https://example.com"}'
```

## Configuration

Required:

- `CLIPPINGBOT_OBSIDIAN_VAULT`
- `CLIPPINGBOT_CRAWL4AI_BASE_URL`
- One of:
  - `CLIPPINGBOT_CRAWL4AI_EMAIL`
  - `CLIPPINGBOT_CRAWL4AI_BEARER_TOKEN`

Common optional settings:

- `CLIPPINGBOT_OBSIDIAN_INBOX`
- `CLIPPINGBOT_CRAWL4AI_FILTER`
- `CLIPPINGBOT_CRAWL4AI_TIMEOUT_SECONDS`
- `CLIPPINGBOT_CRAWL4AI_MODE`
- `CLIPPINGBOT_CRAWL4AI_CRAWL_FALLBACK_DOMAINS`
- `CLIPPINGBOT_NOTE_TAGS`
- `CLIPPINGBOT_NOTE_OVERWRITE_EXISTING`
- `CLIPPINGBOT_FILENAME_MAX_LENGTH`
- `CLIPPINGBOT_FEISHU_APP_ID`
- `CLIPPINGBOT_FEISHU_APP_SECRET`
- `CLIPPINGBOT_FEISHU_DELIVERY_MODE`
- `CLIPPINGBOT_FEISHU_REPLY_ENABLED`
- `CLIPPINGBOT_FEISHU_REPLY_RECEIVE_ID_TYPE`

See [`.env.example`](./.env.example) for a complete example.

## Runtime Modes

ClippingBot supports two runtime modes:

- `longconn`
  Feishu long-connection mode
- `webhook`
  Local HTTP server mode

Unified entrypoint:

```bash
python3 -m clippingbot.main
```

## Crawl4AI Modes

ClippingBot supports three [Crawl4AI](https://github.com/unclecode/crawl4ai) fetch modes:

- `md`
  Always use `/md`
- `crawl`
  Always use `/crawl`
- `auto`
  Use `/md` by default and fall back to `/crawl` when needed

This is useful for sites where `/md` may return an interstitial or verification page while `/crawl` can still extract the article body.

## Output

Each clip is written as a Markdown file that includes:

- frontmatter
- source URL
- source channel
- clip timestamp
- original share text
- captured Markdown content

## Docker Compose

```bash
cp .env.example .env
docker compose up -d --build
```

If ClippingBot and [Crawl4AI](https://github.com/unclecode/crawl4ai) both run in containers, prefer using a shared Docker network and a service-style base URL such as:

```env
CLIPPINGBOT_CRAWL4AI_BASE_URL=http://crawl4ai:11235
```

## Feishu Event Support

ClippingBot accepts text messages that contain URLs, for example:

```text
Example Domain https://example.com
```

For webhook-style delivery, the repository also supports standard Feishu `im.message.receive_v1` payloads.

## Project Structure

- `clippingbot/main.py`: runtime entrypoint
- `clippingbot/feishu_longconn.py`: Feishu long-connection listener
- `clippingbot/server.py`: HTTP server and ingest endpoint
- `clippingbot/crawl4ai_client.py`: [Crawl4AI](https://github.com/unclecode/crawl4ai) client and fallback logic
- `clippingbot/note_writer.py`: Markdown note rendering and persistence
- `.env.example`: example configuration
- `docker-compose.yml`: Docker deployment entry

## Limitations

- Only the first URL in a message is processed
- Duplicate handling is filename-based using a URL hash
- Feishu bot behavior still depends on upstream app permissions and event subscription configuration

## Star History

<a href="https://www.star-history.com/?repos=parap1uie-s%2FClippingBot&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/image?repos=parap1uie-s/ClippingBot&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/image?repos=parap1uie-s/ClippingBot&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/image?repos=parap1uie-s/ClippingBot&type=date&legend=top-left" />
 </picture>
</a>