# Simplified Codex Plugin — Test Cases (OpenAI submission)

Paste these into the OpenAI Codex plugin submission form (fields: **Scenario**,
**User prompt**, **Tool triggered**, **Expected output**). At least 5 required; 6
provided for full coverage of both skills + the cross-skill flow.

## Prerequisites for the review account
- **AI credits** available (cases 1, 2, 6 consume credits — image generation).
- **At least one connected social account** in the review workspace (cases 3–6).
  Connect in the Simplified dashboard → Social.
- Review-account login is supplied separately in the submission form (not in this repo).

All tools are served by the hosted MCP connector (`https://apikit.simplified.com/mcp`),
OAuth-secured. Tool names are namespaced `api_*` (image) and `social_*` (social).

---

## Test Case 1 — Generate an image (text-to-image)
- **Scenario:** Generate an AI image from a text description.
- **User prompt:** `Generate an image of a white ceramic coffee cup on a clean white background, soft studio lighting`
- **Tool triggered:** `api_generateImage`
- **Expected output:** A `SUCCESS` response with a viewable image URL (1024×1024 WebP). With the default `transient` storage, `detail.result[0]` is a temporary image URL. The assistant returns/links the generated image.

## Test Case 2 — Generate a graphic with text + a specific aspect ratio
- **Scenario:** Generate a landscape promo banner with text rendered inside the image.
- **User prompt:** `Make a 16:9 promo banner that says "Summer Sale" in bold modern type`
- **Tool triggered:** `api_generateImage` (model `ideogram.ideogram-v3-turbo`, `capability: "prompt"`, `parameters.aspect_ratio: "16:9"`)
- **Expected output:** A `SUCCESS` response with a 16:9 image URL; the words "Summer Sale" rendered legibly in the image.

## Test Case 3 — List connected social accounts (read-only)
- **Scenario:** Discover which social media accounts are connected.
- **User prompt:** `Which social media accounts do I have connected?`
- **Tool triggered:** `social_getSocialMediaAccounts`
- **Expected output:** A list of connected accounts, each with `id`, `name`, and `type` (e.g. "Instagram business", "LinkedIn company"). If none are connected, the assistant says so and points the user to connect accounts in Simplified — and does not attempt to post.

## Test Case 4 — Draft a social post (no publishing)
- **Scenario:** Draft a post for review before anything is published.
- **User prompt:** `Draft a LinkedIn post announcing our new AI image feature`
- **Tool triggered:** `social_getSocialMediaAccounts`, then `social_createSocialMediaPost` (`action: "draft"`)
- **Expected output:** The assistant lists accounts, composes the post text, shows it, and creates it as a **draft** (`action: "draft"`), returning a confirmation. It must **not** publish or schedule without explicit user confirmation.

## Test Case 5 — Social analytics overview (read-only)
- **Scenario:** Get an analytics summary for a connected account.
- **User prompt:** `How did my Instagram account perform last month?`
- **Tool triggered:** `social_getSocialMediaAccounts`, then `social_getSocialMediaAnalyticsAggregated`
- **Expected output:** A KPI summary for last month — impressions, engagement, followers, posts published — with period-over-period change (`baseLine` with `impressions_aggregated`, `engagement_aggregated`, `followers_aggregated`, `publishing_aggregated`, each `value` + `prevValue`). `date_to` is capped at today (never a future date).

## Test Case 6 — Generate an image and attach it to a draft post (cross-skill)
- **Scenario:** Generate an image and prepare a social post that uses it.
- **User prompt:** `Generate a product image of a sneaker and draft an Instagram post with it`
- **Tool triggered:** `api_generateImage` (`storage: "asset"`), then `social_getSocialMediaAccounts`, then `social_createSocialMediaPost` (`action: "draft"`, `media: ["<asset_id>"]`, `additional.instagram.{postType,channel}`)
- **Expected output:** An image is generated and saved as an **asset** (`detail.result[0].asset_id` returned); a **draft** Instagram post is created with that asset attached via `media: ["<asset_id>"]`; the assistant shows the draft and asks before publishing.
