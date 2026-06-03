# AGENTS.md — Simplified for AI

Operational guidance for AI coding assistants (Codex, Claude Code, Cursor) using
this plugin.

## Project overview

Simplified for AI lets agents **generate AI images** and **manage social media**
(post, schedule, draft, analyze) across Facebook, Instagram, TikTok, YouTube,
LinkedIn, Pinterest, Threads, Bluesky, and Google Business — through:

- **Skills** ([skills/](skills/)) — `SKILL.md` workflow files that teach the agent
  sequencing, terminology, and safety behavior.
- **A hosted MCP connector** — the tools the skills drive, served at
  `https://apikit.simplified.com/mcp` (OAuth-secured). Declared in
  [.mcp.json](.mcp.json).

## Plugin structure

```
simplified-for-ai/
├── .mcp.json                 # hosted MCP connector (OAuth) — shared by all clients
├── .claude-plugin/plugin.json   # Claude Code manifest
├── .cursor-plugin/plugin.json   # Cursor manifest
├── .codex-plugin/plugin.json    # Codex / ChatGPT Apps manifest
├── skills/                   # SKILL.md workflows (Agent Skills spec)
│   ├── generate-image/
│   └── simplified-social/
├── assets/                   # brand icon + logo
└── evals/                    # test cases + runnable I/O harness
```

## Skills

| Skill | Purpose | Tools |
|---|---|---|
| [generate-image](skills/generate-image/SKILL.md) | Text-to-image generation (Flux, Gemini/Imagen, GPT Image, Ideogram, …); saves as a reusable asset | `api_generateImage` |
| [simplified-social](skills/simplified-social/SKILL.md) | Draft / schedule / queue posts + analytics across 10 platforms | `social_*` |

The two compose: `generate-image` returns an **asset id** → pass it into
`simplified-social`'s `media` field to post a freshly generated image.

## MCP server

Same connector for every client, configured in [.mcp.json](.mcp.json):

```json
{ "mcpServers": { "simplified": { "type": "http", "url": "https://apikit.simplified.com/mcp" } } }
```

OAuth-secured — the client walks the OAuth flow; no API key to set. On a 401, the
client refreshes its token automatically (server emits the standard challenge).

## Key conventions (agent behavior)

- **Confirm before spending credits.** Image generation and social publishing
  consume credits / post to live accounts — confirm when intent is ambiguous.
- **Draft before publish.** For social posts, create a `draft` and show it before
  scheduling/queuing. Never publish without explicit user confirmation.
- **"Post now" → `add_to_queue`** (publishes ASAP). There is no separate immediate
  publish action; the `action` enum is `schedule | add_to_queue | draft`.
- **Carry the `asset_id`, not the URL.** Generated-image URLs are signed and expire;
  the `asset_id` is permanent and is what `simplified-social.media` accepts.
- **Stop if not connected.** If `social_getSocialMediaAccounts` is empty, tell the
  user to connect an account — don't attempt to post.

## Commit attribution

When an AI agent commits to this repo, include a `Co-Authored-By:` line with the
agent model's name.
