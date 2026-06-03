---
name: generate-image
description: >-
  Generate AI images with Simplified — text-to-image, image editing, and
  reference-guided generation across Flux, Google (Gemini/Imagen), OpenAI GPT
  Image, Ideogram, Stable Diffusion, Qwen and SeeDream. Use when the user asks to
  create, generate, make, draw, or design an image, photo, picture, graphic,
  logo, poster, banner, icon, or illustration from a description.
---

# Generate AI Image

Generate an image from a text prompt using Simplified, across many leading AI
providers, and return a viewable image URL (plus an asset id you can reuse).

## What it can do

- **Text-to-image** (`capability: "prompt"`) — make an image from a description.
- **Image editing / image-to-image** (`capability: "reference_image"`) — transform
  or edit using one reference image (`parameters.reference_images`).
- **Multi-reference composition** (`capability: "multiple_images"`) — guide with
  several reference images (supported on some models).

Good for: product shots, hero/banner images, social graphics, illustrations,
3D-style renders, icons/logo concepts, photoreal scenes, and **text rendered inside
the image** (posters, quote cards, ad headlines).

## Providers & models

Pass the model `id` as the `model` field. Credits/image in parens.

**Google** — `google.gemini-2.5-flash-image` (100, reliable default), `google.gemini-3-pro-image-preview` (120, top quality), `google.gemini-3.1-flash-image-preview` (150, best reference fidelity), `google.imagen-4.0-generate-001` (70), `google.imagen-4.0-fast-generate-001` (50)
**Flux** — `flux.flux-schnell` (8, cheapest/fastest), `flux.flux-realism` (100, "Flux Pro"), `flux.dev` (60), `flux.flux-kontext-pro` (100), `flux.flux-kontext-max` (200), `flux.flux-1.1-pro-ultra` (200), `flux.flux-2-pro` (200)
**OpenAI** — `openai.imgen` (100, GPT Image 1), `openai.imgen-1.5` (150), `openai.imgen-2` (100)
**Ideogram** — `ideogram.ideogram-v3-turbo` (100, best text-in-image)
**Stability** — `stability.diffusion` (100, SDXL)
**Qwen** — `qwen.qwen-image` (60), `qwen.qwen-image-edit` (75, editing only)
**ByteDance** — `bytedance.seedream-4` (75), `bytedance.seedream-4.5` (200)

Quick pick: **default** `google.gemini-2.5-flash-image` · **cheapest** `flux.flux-schnell` · **text in image** `ideogram.ideogram-v3-turbo` · **highest quality** `google.gemini-3-pro-image-preview`.

## Tool

`api_generateImage` — **consumes paid AI credits**. The connector polls
automatically and returns the **final result directly** (no separate poll step).

## Storage (default: `transient`)

| `storage` | Behavior |
|---|---|
| `transient` | **Default.** Temporary URL, not saved, expires. Best for one-off images. |
| `asset` | Persistent — no expiry, returns an `asset_id`. Use when you want to **reuse** the image, e.g. attach it to a post via the `simplified-social` skill (pass the `asset_id` in `media`). |
| `default` | Saved to your AiImageArt gallery. |

## Request shape & examples

`parameters` is a **required nested object** — never flatten its fields to the top
level. The prompt text goes in `parameters.prompt` (not in `capability`).

**Text-to-image (default, transient):**
```json
{ "model": "google.gemini-2.5-flash-image", "capability": "prompt", "storage": "transient",
  "parameters": { "prompt": "A white ceramic coffee cup on a clean white background", "aspect_ratio": "1:1" } }
```

**Cheap/fast draft:**
```json
{ "model": "flux.flux-schnell", "capability": "prompt", "storage": "transient",
  "parameters": { "prompt": "sketch of a mountain cabin", "aspect_ratio": "16:9", "count": 1 } }
```

**Keep it to reuse / post to social (asset):**
```json
{ "model": "google.gemini-2.5-flash-image", "capability": "prompt", "storage": "asset",
  "parameters": { "prompt": "product hero shot of sneakers", "aspect_ratio": "4:5" } }
```

**Edit / reference-guided:**
```json
{ "model": "google.gemini-3.1-flash-image-preview", "capability": "reference_image", "storage": "asset",
  "parameters": { "prompt": "put this logo on a t-shirt", "reference_images": ["<asset_uuid_or_https_url>"] } }
```

### Parameters (small per-model differences)
- `prompt` (required), `aspect_ratio` (e.g. `1:1`, `16:9`, `9:16`, `4:5`, `21:9`).
- `count` (number of images) — only some models support it (Flux Schnell/Dev,
  Imagen, OpenAI, Stability, SeeDream); Gemini, Flux Pro/Kontext, Recraft, Ideogram
  ignore it.
- `reference_images` — for the reference/multiple capabilities (asset UUIDs or URLs).
- Note: OpenAI `imgen*` models use `size` instead of `aspect_ratio`.

For the exact per-model field list, ratios, and reference-image field name, call
`api_getVideoModelFields({type:"image", model_id, capability})` (it covers image
engines despite the name).

## Response

The MCP tool returns the final result directly. **The shape depends on `storage`:**

- **`transient` (default)** — `result` is a list of **URL strings**:
  ```json
  { "status": "SUCCESS", "detail": { "result": ["https://replicate.delivery/…/out-0.webp"], "transient": true } }
  ```
  Read `detail.result[0]` (a URL string). No `asset_id` — the URL is temporary.

- **`asset`** — `result` is a list of **objects** with a reusable id:
  ```json
  { "status": "SUCCESS", "detail": { "result": [{ "asset_id": "<uuid>", "url": "https://…/image.webp?Expires=…" }], "transient": false, "storage": "asset" } }
  ```
  Read `detail.result[0].url` (the image; **signed URL — expires**) and
  `detail.result[0].asset_id` (permanent — hand off to `simplified-social`'s `media`).

Output is WebP either way.

## Example prompts to try

- "A minimalist product photo of a white ceramic coffee cup on a clean white background, soft studio lighting"
- "A vibrant 3D render of a friendly robot mascot, pastel colors, studio lighting, 1:1"
- "A cinematic 16:9 landscape of snowy mountains at golden hour"
- "A flat vector app icon of a paper plane, rounded corners, blue gradient"
- "A bold quote card that says 'Ship it' in modern type" (use `ideogram.ideogram-v3-turbo` for crisp text)

## Safety

- Generation spends credits — if the request is ambiguous, restate what you'll
  generate and confirm once. If it's explicit, proceed.
- `429` = AI credits exhausted; tell the user plainly and don't retry.
- On error, report it; don't silently retry.
