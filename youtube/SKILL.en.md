---
name: fa-youtube
description: >
  Persian YouTube: SEO titles, timestamped chapters and video scripts
  with time budgets. Not for Twitter threads or Instagram captions.
  Persian source of truth: SKILL.md.
---

# Persian YouTube — agent skill (English mirror)

## Workflows

### 1. Titles
- Front-load the keyword in the first ~5 characters (SERP + mobile
  suggestions). Sweet window 45–70 chars, hard cap 100.
- Persian numerals read better; both digit systems count.
- Empty clickbait («باورنکردنی», «شوک») is penalized; the slop panel
  catches AI-scented titles.

### 2. Chapters
- Input accepts Persian or Latin digits; output defaults to Persian
  numerals («۰۰:۰۰ مقدمه»).
- Real YouTube rules enforced: starts exactly at 00:00, ≥3 chapters,
  each ≥10s, strictly ascending.

### 3. Scripts
- Spine: cold-open hook (0–15s, no logo/greeting) → promise → sections →
  saveable recap → one CTA.
- Time budgets use spoken-Persian pace (140 wpm); verify scripts with
  `core.counter`, not by eye.

## Persian writing rules for scripts
- Spoken register: write it as you say it; let the ZWNJ normalizer fix
  orthography.
- Persian examples with Persian names and places.
- Numbers: spoken «چهارصد هزار تومان», written «۴۰۰٬۰۰۰ تومان» — both
  parse.

## Anti-fabrication & honest limit
Numbers/names come from the user; otherwise placeholder + flag. The tool
scores titles, it does not predict CTR — trust your retention reports.
