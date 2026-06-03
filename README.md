# Simplified for AI

A plugin **marketplace** for **Codex, Claude Code, and Cursor** — generate AI images
and manage social media (post, schedule, draft, analyze) across 10 platforms, backed
by Simplified's hosted MCP connector.

The plugin itself lives in [`simplified/`](simplified/); this repo root is the
marketplace that points to it.

## What's inside

| Skill | Does | Tools |
|---|---|---|
| [`generate-image`](simplified/skills/generate-image/) | Text-to-image generation (Flux, Gemini/Imagen, GPT Image, Ideogram, …), saved as a reusable asset | `api_generateImage` |
| [`simplified-social`](simplified/skills/simplified-social/) | Draft / schedule / queue posts + analytics across 10 platforms | `social_*` |

The two compose: `generate-image` returns an **asset id** → pass it into
`simplified-social`'s `media` field to post a freshly generated image.

## Install

**Claude Code**
```
/plugin marketplace add celeryhq/simplified-for-ai
/plugin install simplified@simplified-for-ai
```

**Codex**
```
codex plugin marketplace add celeryhq/simplified-for-ai
codex plugin install simplified
```

**Cursor** — Settings → Plugins → add from this repo.

**ChatGPT (Apps)** — enable the Simplified app (hosted MCP connector); no install needed.

All clients read the same plugin in [`simplified/`](simplified/) and the same
[`.mcp.json`](simplified/.mcp.json) connector.

## Layout

```
simplified-for-ai/                      ← marketplace root
├── .claude-plugin/marketplace.json     → ./simplified   (Claude Code)
├── .agents/plugins/marketplace.json    → ./simplified   (Codex)
├── README.md, LICENSE
├── evals/                              ← contributor QA (not installed)
└── simplified/                         ← the plugin
    ├── .claude-plugin/plugin.json
    ├── .codex-plugin/plugin.json
    ├── .cursor-plugin/plugin.json
    ├── .mcp.json                       ← hosted MCP connector (OAuth)
    ├── AGENTS.md, SKILL_TREE.md
    ├── skills/{generate-image,simplified-social}/
    └── assets/
```

## Connector & auth

The plugin uses the **Simplified hosted MCP connector** in
[`simplified/.mcp.json`](simplified/.mcp.json): `https://apikit.simplified.com/mcp`.
OAuth-secured — the client walks the OAuth flow; no API key to set, and tokens
refresh automatically on expiry.

## Key behavior (see [AGENTS.md](simplified/AGENTS.md))

- Confirm before spending credits (image generation) or publishing (social).
- Draft → confirm → publish for social posts; never publish without confirmation.
- "Post now" → `add_to_queue` (the `action` enum is `schedule | add_to_queue | draft`).
- Carry the `asset_id`, not the URL — generated-image URLs are signed and expire.

## Status

- [x] Hosted connector live: `apikit.simplified.com/mcp` (OAuth + token refresh).
- [x] Plugin in `simplified/`; Claude + Codex marketplaces at root (install verified).
- [x] `action` semantics verified against backend (`add_to_queue` = publish ASAP; `message` ≤ 3000).
- [ ] Submit Simplified ChatGPT App (pending business verification).
- [ ] Optional polish: add `outputSchema` to specs; tighten `generateImage` input schema.
