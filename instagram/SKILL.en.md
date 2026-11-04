---
name: fa-instagram
description: >
  Persian Instagram content creation: captions, carousels, reel hooks and
  humanization. Use for writing captions (NOT slide-by-slide carousels —
  use the carousel workflow below), reel hooks, slide planning and
  AI-slop scrubbing of Persian text. Persian source of truth: SKILL.md.
---

# Persian Instagram — agent skill (English mirror)

> "These skills write. You post." Nothing is published without explicit
> approval; automated posting violates Instagram's Terms of Use and
> action-blocks accounts.

## Prerequisites

None. All tools are stdlib Python, run offline, need no keys. Every
workflow produces a useful zero-credential output.

## Global voice rule

**The model decides; the script measures.** Never eyeball length, the
feed fold or slop density — run the tools:

```python
from instagram import lint, score_hook, humanize, plan_carousel, audit_deck
```

## Workflows

### 1. Caption
- Decide **Job A vs Job B first**: video already hooked → caption carries
  the ask, context and search terms (A); caption is the content → line
  one is the hook (B).
- The feed folds at **125 characters**; almost every failing caption
  fails there. See `preview_fold()` for the stranger's view.
- Hashtag cap is **5** (since 18 Dec 2025). ZWNJ hashtags break tracking
  (`#می‌خوره` renders as `#می` on-platform). Write search terms as normal
  phrases in the text.
- One ask. Two asks is the same as none.

### 2. Carousel
- Spine: slide 1 = promise + open loop (never a dry title) → strongest
  value first → one idea per slide → saveable payoff → one CTA.
- Never pad: a 5-point idea is a 7-slide carousel.
- Slide text budgets use the **RTL width model**: Persian renders 20–35%
  narrower than Latin; a Latin budget over-constrains Persian slides.

### 3. Reel hooks
- 12 Persian formulas (`FA01`–`FA12`), each with a `trap` field
  documenting its own most common failure.
- Dealbreakers: no greeting, no "in this video", no hashtag/emoji in the
  hook.
- Calibrated honesty (inherited): the panel reliably kills obviously weak
  hooks (AUC≈0.83) but does not predict winners (AUC≈0.56). Trust the
  retention graph.

### 4. Humanizer
- Pass 1 invisible chars — **ZWNJ is never removed** (it is orthography,
  not noise).
- Pass 2 typography — em dashes capped (~1/100 words), not banned;
  replacement order comma → colon → parentheses → line break → rewrite,
  **never a period**.
- Pass 3 lexical — the Persian slop lexicon replaces literal AI-buzzword
  translations with idiomatic Persian.
- Pass 4 structural — flagged, never auto-rewritten: "نه فقط X، بلکه Y"
  cadence, stacked triads, opening rhetorical questions, uniform sentence
  length (CV < 0.35). Structural rewrites are the model's job.

## Anti-fabrication (hard rule)

Never invent numbers, brand names or results — not even as "placeholders"
you fill with plausible values. If the user gave nothing, keep
`{{عدد شما}}` empty and flag it. An invented number is a retraction; a
missing one is only a weaker post.

## This skill refuses

- Hooks that need line 2 to make sense (the fold eats them)
- Title-only slide 1; three competing CTAs in one caption
- 20–30 hashtag walls; "viral hashtag packs"; tags that don't match content
- Engagement bait ("comment YES", "tag 3 friends") — downranked by the platform

## Honest limits

Local heuristics, not detector APIs — no "beat the detector" promise.
Platform numbers are dated; if they contradict current Instagram behavior,
Instagram is right. No tool makes network calls, holds keys, or uploads data.
