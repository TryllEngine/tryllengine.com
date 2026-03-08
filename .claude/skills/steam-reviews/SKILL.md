---
name: steam-reviews
description: Fetch and analyze Steam reviews for Tryll products. Use this skill when the user wants to check Steam reviews, see what players are saying, analyze feedback, get a sentiment summary, find negative reviews, or track review trends for Tryll Assistant or BoscoTryll. Also trigger when the user mentions player feedback, Steam ratings, or review analysis.
---

# Steam Reviews

Fetch and analyze Steam user reviews for Tryll Engine products, summarize sentiment and themes, and flag actionable feedback.

## Steam App IDs

- **Tryll Assistant**: `3442530`
- **BoscoTryll**: `4193780`

## Workflow

### Step 1: Determine which product

Ask the user which product, or default to Tryll Assistant (`3442530`). If "all" or "both", run for each.

### Step 2: Fetch reviews

The Steam Store Review API is public — no API key needed.

```bash
curl -s "https://store.steampowered.com/appreviews/3442530?json=1&language=all&num_per_page=100&filter=recent&purchase_type=all"
```

**Parameters:**

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `json` | `1` | JSON format |
| `language` | `all` | All languages |
| `num_per_page` | `100` | Max per request |
| `filter` | `recent` | Most recent first |
| `purchase_type` | `all` | All purchase types |

**Pagination**: Use `cursor` from response for more pages:
```bash
curl -s "https://store.steampowered.com/appreviews/3442530?json=1&language=all&num_per_page=100&filter=recent&cursor={CURSOR}"
```

### Step 3: Parse the response

Key fields from the API:

```json
{
  "query_summary": {
    "review_score_desc": "Mostly Positive",
    "total_positive": 85,
    "total_negative": 15,
    "total_reviews": 100
  },
  "reviews": [{
    "review": "Review text...",
    "voted_up": true,
    "language": "english",
    "timestamp_created": 1709856000,
    "author": {
      "playtime_forever": 120,
      "playtime_at_review": 60
    },
    "votes_up": 5
  }]
}
```

### Step 4: Sentiment summary

```
# Steam Review Analysis — {Product Name}
App ID: {id} | Date: {today}

## Overview
Score: {review_score_desc}
Total reviews: {total}
Positive: {pos} ({%}) | Negative: {neg} ({%})
```

### Step 5: Identify themes

Group English reviews by recurring topics:

| Theme | Keywords to look for |
|-------|---------------------|
| Performance | FPS, lag, slow, fast, smooth, stuttering |
| GPU/Hardware | VRAM, CUDA, Vulkan, AMD, NVIDIA, GPU |
| Accuracy | wrong, hallucination, correct, helpful, accurate |
| Ease of use | easy, confusing, setup, install, intuitive |
| Privacy | offline, local, no internet, data, privacy |
| Specific games | game names |
| Bugs | crash, error, broken, fix, bug |
| Feature requests | wish, hope, would be nice, should add, please |

Present themes with example quotes:

```
## Common Themes

### Positive
1. **Privacy/Local AI** (N reviews)
   - "Love that it runs locally..."

### Negative / Concerns
1. **Performance** (N reviews)
   - "Drops my FPS by 20..."
```

### Step 6: Flag actionable negatives

List negative reviews with specific, actionable feedback:

```
## Actionable Feedback

| Review excerpt | Playtime | Issue | Potential fix |
|---------------|----------|-------|---------------|
| "Overlay blocks minimap..." | 2.5 hrs | UI overlap | Position config |
| "Crashes on alt-tab..." | 0.8 hrs | Stability | Alt-tab handling |
```

Prioritize by:
1. Specific bug reports
2. Feature requests with multiple mentions
3. Performance issues with hardware details
4. Reviews with high vote counts

### Step 7: Timeline analysis (optional)

If enough reviews, show trends:

```
## Timeline

| Period | Positive | Negative | Notes |
|--------|----------|----------|-------|
| Feb 2026 | 12 | 3 | Launch week |
| Mar 2026 | 25 | 5 | v0.0.8 release |
```

### Step 8: Present the full report

Offer to:
- Save the report as a markdown file
- Generate a "Community Q&A" blog post responding to feedback (use `changelog-from-steam` or `blog-from-linkedin` pipeline)
- Create a summary for the team

## Important conventions

- **No API key needed** — the Steam review endpoint is public
- **Rate limiting**: Space multiple fetches if paginating
- **Privacy**: Do not include Steam user IDs or usernames — keep reviews anonymous
- **Low playtime context**: Note reviews from users with <30 min playtime
- **Non-English reviews**: Count in totals, focus analysis on English
- **Steam app IDs**: Tryll Assistant = `3442530`, BoscoTryll = `4193780`
