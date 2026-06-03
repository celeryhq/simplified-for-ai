# Simplified for AI

AI-powered content creation for **Codex, Claude Code, and Cursor** — generate AI
images and manage social media (post, schedule, draft, analyze) across 10 platforms,
backed by Simplified's hosted MCP connector.

This repo packages Simplified as an **Agent Skills** plugin: `SKILL.md` workflow files
that teach the agent how to drive the hosted MCP tools.

## What's inside

| Skill | Does | Tools |
|---|---|---|
| [`generate-image`](skills/generate-image/) | Text-to-image generation (Flux, Gemini/Imagen, GPT Image, Ideogram, …), saved as a reusable asset | `api_generateImage` |
| [`simplified-social`](skills/simplified-social/) | Draft / schedule / queue posts + analytics across 10 platforms | `social_*` |

The two compose: `generate-image` returns an **asset id** → pass it into
`simplified-social`'s `media` field to post a freshly generated image.

## Install

| Client | How |
|---|---|
| **Claude Code** | `/install-plugin file:///path/to/simplified-for-ai` (or via marketplace once published) |
| **Cursor** | Settings → Plugins → add from source / repo |
| **Codex** | Drop on the skills discovery path, or enable the Simplified ChatGPT App (hosted connector) |

All three read the **same** skills and the **same** [`.mcp.json`](.mcp.json) connector.

## Layout

```
simplified-for-ai/
├── .mcp.json                    # hosted MCP connector (OAuth) — shared by all clients
├── .claude-plugin/plugin.json   # Claude Code manifest
├── .cursor-plugin/plugin.json   # Cursor manifest
├── .codex-plugin/plugin.json    # Codex / ChatGPT Apps manifest
├── AGENTS.md                    # agent operating guidance (Codex reads natively)
├── SKILL_TREE.md                # skill index
├── README.md
├── skills/
│   ├── generate-image/
│   │   ├── SKILL.md             # self-contained (models, storage, payloads, prompts)
│   │   └── agents/openai.yaml   # per-skill Codex metadata
│   └── simplified-social/
│       ├── SKILL.md
│       ├── agents/openai.yaml
│       └── references/{platform-settings,analytics}.md
├── assets/                      # simplified-logo.png, simplified-treadmark-logo.png
└── evals/                       # test cases + runnable I/O harness
```

## Connector & auth

All skills use the **Simplified hosted MCP connector** declared in
[`.mcp.json`](.mcp.json): `https://apikit.simplified.com/mcp`. It is OAuth-secured —
the client walks the OAuth flow; there is no API key to set, and tokens refresh
automatically on expiry.

## Key behavior (see [AGENTS.md](AGENTS.md))

- Confirm before spending credits (image generation) or publishing (social).
- Draft → confirm → publish for social posts; never publish without confirmation.
- "Post now" → `add_to_queue` (the `action` enum is `schedule | add_to_queue | draft`).
- Carry the `asset_id`, not the URL — generated-image URLs are signed and expire.

## Status

- [x] Hosted connector live: `apikit.simplified.com/mcp` (OAuth + token refresh).
- [x] Brand art (PNG) + color `#FFAD00`.
- [x] `action` semantics verified against backend (`add_to_queue` = publish ASAP; `message` ≤ 3000).
- [x] Multi-client manifests (Claude Code / Cursor / Codex).
- [ ] Submit Simplified ChatGPT App (pending business verification).
- [ ] Optional polish: add `outputSchema` to specs; tighten `generateImage` input schema.
