---
name: simplified-social
description: >-
  Manage your entire social media from Codex with Simplified — post, schedule,
  queue, draft, and analyze across Facebook, Instagram, TikTok, YouTube,
  LinkedIn, Pinterest, Threads, Bluesky and Google Business. Triggers: social
  media, post to, schedule post, publish on, social accounts, analytics, reach,
  impressions, engagement, followers growth, content calendar.
---

# Simplified Social Media

Schedule, queue, and draft social media posts, and retrieve analytics across 10 platforms using Simplified.com.

## Connector

All tools (`social_getSocialMediaAccounts`, `social_createSocialMediaPost`, `social_getSocialMediaAnalyticsRange`, etc.) are provided by the **Simplified hosted MCP connector** (`https://apikit.simplified.com/mcp`), namespaced `social_*`. They are not built-in tools.

The connector is **OAuth-secured** — Codex walks the OAuth flow; there is no API key to set.

## IMPORTANT: Before Any Operation

If any tool call returns a **401 / Unauthorized**, the Simplified connector is not authorized:

1. **Stop immediately** — do not retry the failed call.
2. **Inform the user** that they need to connect Simplified (authorize the connector) before social tools will work.
3. **Do not proceed** with the original request until the connector is authorized.

## Setup

1. Sign up at [simplified.com](https://simplified.com).
2. Connect your social media accounts in the Simplified dashboard.
3. Enable the Simplified connector in Codex and complete the OAuth authorization.

## Core Workflow

Always follow this sequence: **Discover → Select → Compose → Confirm → Publish**

### Step 1: Discover Accounts

Call `social_getSocialMediaAccounts` to list connected accounts. Optionally filter by network.

```
social_getSocialMediaAccounts({ network: "instagram" })
```

Returns `{ accounts: [...] }` where each account has `id` (integer), `name`, and `type` (see type values below).

If `social_getSocialMediaAccounts` returns an empty list, stop and inform the user with this message:

> **No social media accounts connected yet.**
>
> You're one step away from managing your entire social media presence without leaving your editor. Connect your accounts in the [Simplified dashboard](https://app.simplified.com) and you'll be able to:
>
> - 📅 Schedule and publish posts to Facebook, Instagram, TikTok, YouTube, LinkedIn, Pinterest, Threads, Bluesky and Google Business — with a single command
> - 📊 Pull analytics, track reach, engagement and follower growth across all platforms
> - 🤖 Let your AI agent run full social media campaigns autonomously
>
> Takes 2 minutes to connect. No code required.

### Step 2: Select Target Accounts

Pick one or more `account_ids` from the results. You can post to multiple accounts in a single call.

### Step 3: Compose the Post

Build the post payload:
- `message` (required) — the post text, max 3000 chars (tighter per-platform limits apply)
- `account_ids` (required for publishing actions) — array of target account IDs
- `action` (required) — `schedule`, `add_to_queue`, or `draft`
- `date` — required for `schedule`, format: `YYYY-MM-DD HH:MM`
- `media` — array (max 10) of **Simplified asset UUIDs** or public media URLs
- `additional` — platform-specific settings (see below)

**Attaching a generated image:** `media` accepts Simplified **asset UUIDs**, resolved server-side to fresh permanent URLs at publish time — exactly what the **generate-image** skill returns with `storage:"asset"`. Pass that `asset_id` straight into `media`.

### Step 4: Confirm, then Publish

Publishing is outward-facing. For `schedule` / `add_to_queue`, **show the composed post to the user and get explicit confirmation first** (drafting first with `action:"draft"` is a good way to preview). Then call `social_createSocialMediaPost`.

## Choosing the Right Analytics Tool

| User asks about... | Tool to call |
|---|---|
| Trends over time, charts, metric growth/decline | `social_getSocialMediaAnalyticsRange` |
| Specific posts, best/worst performing content | `social_getSocialMediaAnalyticsPosts` |
| Account overview, KPIs, period summary | `social_getSocialMediaAnalyticsAggregated` |
| Demographics, follower origins, age/gender breakdown | `social_getSocialMediaAnalyticsAudience` |
| "Show me analytics" with no further context | `social_getSocialMediaAnalyticsAggregated` + `social_getSocialMediaAnalyticsRange` with key metrics |

## Tool Reference

### `social_getSocialMediaAccounts`

| Parameter | Type   | Required | Description                          |
|-----------|--------|----------|--------------------------------------|
| `network` | string | No       | Filter by platform (see networks)    |

**Networks (filter parameter):** `facebook`, `instagram`, `linkedin`, `tiktok`, `youtube`, `pinterest`, `threads`, `google`, `bluesky`, `tiktokBusiness`

Returns `{ accounts: [...] }`. Each account object:

| Field  | Type    | Description |
|--------|---------|-------------|
| `id`   | integer | Account ID — use for all analytics calls and for `account_ids` in `social_createSocialMediaPost` |
| `name` | string  | Account display name |
| `type` | string  | Account type — see values below |

**`type` values and their meaning:**

| `type` value | Platform | Notes |
|---|---|---|
| `Facebook page` | Facebook | — |
| `Instagram business` / `Instagram profile` | Instagram | — |
| `Youtube account` | YouTube | — |
| `TikTok profile` | TikTok Personal | use `tiktok` metrics set |
| `TikTok profile (business)` | TikTok Business | use `tiktokBusiness` metrics set |
| `LinkedIn company` | LinkedIn | use LinkedIn Company metrics set |
| `LinkedIn profile` | LinkedIn | use LinkedIn Personal metrics set |
| `Pinterest board` | Pinterest | — |
| `Threads account` | Threads | — |
| `Bluesky account` | Bluesky | — |
| `Google Profile` | Google Business | — |

### `social_createSocialMediaPost`

| Parameter     | Type     | Required | Description                              |
|---------------|----------|----------|------------------------------------------|
| `message`     | string   | Yes      | Post text (max 3000 chars)               |
| `account_ids` | int[]    | For publish | Target account IDs from `social_getSocialMediaAccounts`; omit/empty for an accountless `draft` |
| `action`      | string   | Yes      | `schedule`, `add_to_queue`, or `draft`   |
| `date`        | string   | For `schedule` | Schedule datetime: `YYYY-MM-DD HH:MM` (not in the past) |
| `media`       | string[] | No       | Asset UUIDs or public media URLs (max 10) |
| `tags`        | int[]    | No       | Tag IDs |
| `additional`  | object   | Per platform | Platform-specific settings |

### `social_getSocialMediaAnalyticsRange`

Retrieves time-series data for selected metrics within a date range.

| Parameter    | Type     | Required | Description                                                  |
|--------------|----------|----------|--------------------------------------------------------------|
| `account_id` | integer  | Yes      | Social media account ID (from `social_getSocialMediaAccounts`) |
| `metrics`    | string[] | Yes      | List of metrics to retrieve (see `references/analytics.md`)  |
| `date_from`  | string   | Yes      | Start date: `YYYY-MM-DD`                                     |
| `date_to`    | string   | Yes      | End date: `YYYY-MM-DD` (never in the future)                 |
| `tz`         | string   | No       | Timezone, e.g. `UTC`, `Europe/Warsaw` (default: `UTC`)       |

Returns `data` (per-day series), `baseLine` (period totals with `prevValue`), and `additional` (windowed extras). See `references/analytics.md` for the full metric list, default metrics per network, and response examples.

### `social_getSocialMediaAnalyticsPosts`

Retrieves analytics for individual posts within a date range.

| Parameter    | Type    | Required | Description                                             |
|--------------|---------|----------|---------------------------------------------------------|
| `account_id` | integer | Yes      | Social media account ID                                 |
| `date_from`  | string  | Yes      | Start date: `YYYY-MM-DD`                                |
| `date_to`    | string  | Yes      | End date: `YYYY-MM-DD`                                  |
| `page`       | integer | No       | Page number (default: 1, minimum: 1)                    |
| `per_page`   | integer | No       | Posts per page (default: 10, max: 100)                  |

Returns paginated posts with per-post metrics. **Pagination:** use `per_page: 100`, start at `page: 1`, increment until `current_page >= pages_count` or `posts` is empty.

### `social_getSocialMediaAnalyticsAggregated`

Retrieves aggregated analytics (totals and averages) for an account within a date range.

| Parameter    | Type    | Required | Description             |
|--------------|---------|----------|-------------------------|
| `account_id` | integer | Yes      | Social media account ID |
| `date_from`  | string  | Yes      | Start date: `YYYY-MM-DD` |
| `date_to`    | string  | Yes      | End date: `YYYY-MM-DD`  |

Returns `data` plus `baseLine` with four KPIs: `impressions_aggregated`, `engagement_aggregated`, `followers_aggregated`, `publishing_aggregated` (each with `value` and `prevValue`).

### `social_getSocialMediaAnalyticsAudience`

Retrieves audience demographics and follower data for an account.

| Parameter    | Type    | Required | Description                          |
|--------------|---------|----------|--------------------------------------|
| `account_id` | integer | Yes      | Social media account ID              |
| `date_from`  | string  | Yes      | Start date: `YYYY-MM-DD`             |
| `date_to`    | string  | Yes      | End date: `YYYY-MM-DD`              |
| `tz`         | string  | No       | Timezone, e.g. `UTC`, `Europe/Warsaw` |

Returns `audience_page_fans_gender_age`, `audience_page_fans_country`, `audience_page_fans_city`. Not all fields are available for every network.

## Action Types

| Action         | When to Use                                          | `date` Required? |
|----------------|------------------------------------------------------|-------------------|
| `schedule`     | Post at a specific date/time                         | Yes               |
| `add_to_queue` | Publish as soon as possible (optimal-time queue)     | No                |
| `draft`        | Save for later editing in the Simplified dashboard   | No                |

**Default:** When the user doesn't specify timing (or says "post now"), use `add_to_queue` — it publishes ASAP; there is no separate immediate-publish action. When they give a date/time, use `schedule`. When they say "save" or "draft", use `draft`.

## Platform Settings Quick Reference

All platform settings go inside the `additional` object, grouped by platform name. **Bold** = required. For full details see [references/platform-settings.md](references/platform-settings.md).

| Platform       | Required additionals              | Optional additionals               |
|----------------|-----------------------------------|------------------------------------|
| Facebook       | **`postType`**                    | —                                  |
| Instagram      | **`postType`**, **`channel`**     | `postReel` (reel only)             |
| TikTok         | **`postType`**, **`channel`**, **`post`** | `postPhoto` (photo only)  |
| TikTok Biz     | **`postType`**, **`post`**        | `postPhoto` (photo only)           |
| YouTube        | **`postType`**, **`post`**        | —                                  |
| LinkedIn       | **`audience`**                    | —                                  |
| Pinterest      | **`post`**                        | —                                  |
| Threads        | **`channel`**                     | —                                  |
| Google         | **`post`**                        | —                                  |
| Bluesky        | —                                 | —                                  |

Key enum values:

| Platform   | Field              | Values                              |
|------------|--------------------|-------------------------------------|
| Facebook   | `postType.value`   | `post`\*, `reel`, `story`           |
| Instagram  | `postType.value`   | `post`\*, `reel`, `story`           |
| Instagram  | `channel.value`    | `direct`\*, `reminder`              |
| TikTok     | `postType.value`   | `video`\*, `photo`                  |
| TikTok     | `channel.value`    | `direct`\*, `reminder`              |
| TikTok     | `post.privacyStatus` | `PUBLIC_TO_EVERYONE`\*, `MUTUAL_FOLLOW_FRIENDS`, `FOLLOWER_OF_CREATOR`, `SELF_ONLY` |
| YouTube    | `postType.value`   | `video`\*, `short`                  |
| YouTube    | `post.privacyStatus` | `""`, `public`, `private`, `unlisted` |
| LinkedIn   | `audience.value`   | `PUBLIC`\*, `CONNECTIONS`, `LOGGED_IN` |
| Threads    | `channel.value`    | `direct`\*, `reminder`              |
| Google     | `post.topicType`   | `STANDARD`\*, `EVENT`, `OFFER`      |

\* = default

## Example Workflows

### Simple Queue Post

```
1. social_getSocialMediaAccounts({ network: "instagram" })
2. social_createSocialMediaPost({
     message: "Check out our new feature! 🚀",
     account_ids: [123],
     action: "add_to_queue",
     media: ["https://cdn.example.com/image.jpg"],
     additional: {
       instagram: { postType: { value: "post" }, channel: { value: "direct" } }
     }
   })
```

### Scheduled YouTube Short

```
1. social_getSocialMediaAccounts({ network: "youtube" })
2. social_createSocialMediaPost({
     message: "Quick tip: how to use our API",
     account_ids: [456],
     action: "schedule",
     date: "2026-06-10 14:00",
     media: ["https://cdn.example.com/video.mp4"],
     additional: {
       youtube: { postType: { value: "short" },
         post: { title: "API Quick Tip", privacyStatus: "public", selfDeclaredMadeForKids: "no" } }
     }
   })
```

### Post a freshly generated image

```
1. (generate-image skill) → asset_id "a1b2c3…"
2. social_getSocialMediaAccounts({ network: "instagram" })
3. social_createSocialMediaPost({
     message: "Meet the new drop 👟",
     account_ids: [123],
     action: "draft",
     media: ["a1b2c3…"],                       // asset UUID from generate-image
     additional: { instagram: { postType: { value: "post" }, channel: { value: "direct" } } }
   })
```

### Analytics: Account Overview

```
1. social_getSocialMediaAccounts({ network: "facebook" })
2. social_getSocialMediaAnalyticsAggregated({ account_id: 789, date_from: "2026-05-01", date_to: "2026-05-31" })
```

## Gotchas

- **Analytics `account_id` is an integer** — use the numeric `id` from `social_getSocialMediaAccounts`.
- **Analytics date format** is `YYYY-MM-DD` (no time component, unlike post scheduling); never set `date_to` in the future.
- **Unknown metrics are silently ignored** by `social_getSocialMediaAnalyticsRange` — check `references/analytics.md` for per-network availability.
- **Audience data availability varies** — `social_getSocialMediaAnalyticsAudience` may return partial or empty data depending on the network.
- **Post `date` format** must be `YYYY-MM-DD HH:MM` (24-hour, no seconds, no timezone — uses account timezone).
- **Media** must be a Simplified asset UUID (from `generate-image` with `storage:"asset"`) or a publicly accessible URL — localhost does not work.
- **`date` is required** when `action` is `schedule` — omit it for `add_to_queue` and `draft`.
- **Platform character limits** — see `references/platform-settings.md`.
- **Instagram always requires `channel`** — include `channel: { value: "direct" }` for every Instagram post.
- **TikTok `postType`** values are `video` and `photo` (not `image`); **channel** values are `direct` and `reminder` (not `business`).
- **LinkedIn audience** value is `LOGGED_IN` (not `LOGGED_IN_MEMBERS`).
- **Google `topicType`** only has `STANDARD`, `EVENT`, `OFFER` (no `PRODUCT`).
- **Instagram story** — message must be empty (`""`), max 1 photo.
- **Reels and Shorts require video** — Instagram reel, Facebook reel, YouTube short all require a video file in `media`; images are not allowed.
- **YouTube always requires `post.title`** — include `additional.youtube.post` with a `title` for every YouTube video or short.
