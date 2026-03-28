# ClippingBot

将飞书机器人消息中的链接自动保存为 [Obsidian](https://obsidian.md) Markdown 笔记。

[English README](./README.md)

## 功能特性

- 接收包含 URL 的文本消息
- 提取消息中的第一个 URL
- 通过 [Crawl4AI](https://github.com/unclecode/crawl4ai) 抓取网页内容
- 生成带 frontmatter 的 Markdown 笔记
- 直接写入本地 [Obsidian](https://obsidian.md) 兼容目录
- 支持飞书长连接模式
- 支持本地 HTTP 服务模式，便于调试或接入自定义自动化
- 支持命令行单次剪藏
- 支持对特定站点使用 [Crawl4AI](https://github.com/unclecode/crawl4ai) fallback 策略
- 支持 Docker Compose 部署

## 工作流程

1. 消息被发送到飞书机器人，或者通过本地 ingest 接口发给 ClippingBot
2. ClippingBot 从文本中提取第一个 URL
3. ClippingBot 调用 [Crawl4AI](https://github.com/unclecode/crawl4ai) 抓取页面内容
4. ClippingBot 生成带元数据的 Markdown 笔记
5. 笔记被写入配置好的知识库目录

## 快速开始

### 本地运行

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

### HTTP 调试

```bash
curl -X POST 'http://127.0.0.1:8787/ingest' \
  -H 'Content-Type: application/json' \
  -d '{"text":"Example Domain https://example.com"}'
```

## 配置项

必填：

- `CLIPPINGBOT_OBSIDIAN_VAULT`
- `CLIPPINGBOT_CRAWL4AI_BASE_URL`
- `CLIPPINGBOT_CRAWL4AI_EMAIL` 或 `CLIPPINGBOT_CRAWL4AI_BEARER_TOKEN`

常用可选项：

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

完整示例见 [`.env.example`](./.env.example)。

## 运行模式

ClippingBot 支持两种运行模式：

- `longconn`
  飞书长连接模式
- `webhook`
  本地 HTTP 服务模式

统一入口：

```bash
python3 -m clippingbot.main
```

## Crawl4AI 抓取模式

ClippingBot 支持三种 [Crawl4AI](https://github.com/unclecode/crawl4ai) 模式：

- `md`
  始终使用 `/md`
- `crawl`
  始终使用 `/crawl`
- `auto`
  默认走 `/md`，必要时 fallback 到 `/crawl`

这对某些站点很有用，例如 `/md` 可能拿到验证页或中间页，而 `/crawl` 仍然能拿到真实正文。

## 输出内容

每次剪藏都会生成一个 Markdown 文件，包含：

- frontmatter
- 源 URL
- 来源渠道
- 剪藏时间
- 原始分享文本
- 抓取后的 Markdown 正文

## Docker Compose

```bash
cp .env.example .env
docker compose up -d --build
```

如果 ClippingBot 和 [Crawl4AI](https://github.com/unclecode/crawl4ai) 都运行在容器里，推荐使用共享 Docker 网络，并把地址配置成：

```env
CLIPPINGBOT_CRAWL4AI_BASE_URL=http://crawl4ai:11235
```

## 飞书事件支持

ClippingBot 期望接收到包含 URL 的文本消息，例如：

```text
Example Domain https://example.com
```

如果使用 Webhook 方式，仓库也兼容标准的 Feishu `im.message.receive_v1` 事件结构。

## 项目结构

- `clippingbot/main.py`：运行入口
- `clippingbot/feishu_longconn.py`：飞书长连接监听
- `clippingbot/server.py`：HTTP 服务和 ingest 接口
- `clippingbot/crawl4ai_client.py`：[Crawl4AI](https://github.com/unclecode/crawl4ai) 客户端和 fallback 逻辑
- `clippingbot/note_writer.py`：Markdown 生成和写入
- `.env.example`：示例配置
- `docker-compose.yml`：Docker 部署入口

## 当前限制

- 当前只处理消息中的第一个 URL
- 去重逻辑基于 URL hash 命名
- 飞书机器人效果仍依赖上游应用权限和事件订阅配置

## Star History

<a href="https://www.star-history.com/?repos=parap1uie-s%2FClippingBot&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/image?repos=parap1uie-s/ClippingBot&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/image?repos=parap1uie-s/ClippingBot&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/image?repos=parap1uie-s/ClippingBot&type=date&legend=top-left" />
 </picture>
</a>