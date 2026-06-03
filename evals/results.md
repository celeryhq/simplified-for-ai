# Eval Results & Golden Outputs

Live captures from production (`https://api.simplified.com`). Image-gen and the full
OAuth pipeline were verified end-to-end; social cases are pending a fresh token
(re-run `run_evals.py` to complete them — they were blocked only by a ~1h token
expiry, not by any failure).

Last run: 2026-06-02.

## Status summary

| Case | Layer | Status | Note |
|---|---|---|---|
| OAuth pipeline (DCR → PKCE → token) | infra | ✅ verified | client registered, token minted (3600s, full scopes) |
| C1 — image, transient | I/O | ✅ verified live | real 1024×1024 WebP |
| C2 — image, 16:9 text | I/O | ⏳ not run | image path proven by C1; run with `--with-image` |
| C3 — list accounts | I/O | ⏳ pending auth | read-only; harness ready |
| C4 — draft post | I/O | ⏳ pending auth | accountless draft; harness ready |
| C5 — analytics aggregated | I/O | ⏳ pending auth | needs a connected account |
| C6 — image→draft (cross-skill) | I/O | ⏳ pending auth | run with `--with-image` |

## Golden outputs (captured live)

### api_generateImage — raw endpoint is async (202 → poll)
`POST /api/v1/ai/image/ai-generate-image-v2`:
```json
{ "task_id": "24797bd9-3591-4f19-89cd-9fd935d4839f", "storage": "asset" }   // HTTP 202
```

### api_generateImage — transient (default), via MCP tool
```json
{ "status": "SUCCESS",
  "detail": { "result": ["https://replicate.delivery/…/out-0.webp"], "transient": true } }
```
`detail.result[0]` is a **URL string**. Fetched → HTTP 200 `image/webp`, 1024×1024. ✅

### api_generateImage — asset, via MCP tool
```json
{ "status": "SUCCESS",
  "detail": { "result": [{ "asset_id": "e3441f49-c118-49a0-9a37-5b73f11f2aed",
                           "url": "https://djcdnpt.simplified.com/…/image.webp?Expires=…&Signature=…&Key-Pair-Id=…" }],
              "transient": false, "storage": "asset" } }
```
`detail.result[0]` is an **object** `{asset_id, url}`. Fetched → HTTP 200 `image/webp`,
1024×1024. ✅ The raw task-poll also returns an identical `info` key; the MCP tool
returns only `detail`. The `url` is a **signed CloudFront URL that expires** — carry
the `asset_id` downstream.

### api_getVideoModelFields({type:"image"})
Returns **22 models** (Flux, Google Gemini/Imagen, OpenAI GPT Image, Ideogram,
Stability, Qwen, ByteDance). Identical via direct API and via MCP. ✅ Confirmed: `count`
is only on some models; OpenAI `imgen*` use `size` not `aspect_ratio`. (Full table in
the skill's earlier reference / `generate-image/SKILL.md`.)

## Expected outputs (to confirm on next run)

### social_getSocialMediaAccounts → `{ "accounts": [{ "id": <int>, "name": "...", "type": "..." }] }`
### social_getSocialMediaAnalyticsAggregated → `{ "data": [...], "baseLine": { "impressions_aggregated": {value,prevValue}, "engagement_aggregated": {...}, "followers_aggregated": {...}, "publishing_aggregated": {...} } }`
### social_createSocialMediaPost (action:"draft") → success; draft then visible in `social_getSocialMediaDrafts`.

## How to complete the pending cases
```bash
export SMP_ACCESS_TOKEN=<fresh token>   # see README.md
python3 evals/run_evals.py --with-image
```
Then update the Status table above with PASS/FAIL.
