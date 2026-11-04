---
name: fa-twitter
description: >
  Persian Twitter/X threads and one-line hooks: thread splitting with
  exact weighted-length math for bilingual text, Persian numbering
  «(۱/۵)», and hook scoring. Not for Instagram captions.
  Persian source of truth: SKILL.md.
---

# Persian Twitter/X — agent skill (English mirror)

## The Persian math fact on X

X length is **weighted**: Persian, Arabic and Latin weigh 1 per char;
CJK weighs 2; **ZWNJ weighs 0**. Persian therefore gets the full 280 —
the "RTL gets halved" belief is the old 140-era CJK rule, not Persian.
The tool is `core.counter.weighted_length`; nothing is eyeballed.

## Workflows

### 1. Thread splitting
```python
from twitter import thread_from_text
th = thread_from_text(long_text)
print(th.render())
```
- Sentence-first splitting (Persian terminals ؟ ! ؛ …); word-level split
  only for over-limit sentences — whitespace-only, so **ZWNJ compounds
  are never severed**.
- Persian-numeral badges «(۱/۵)» with badge-space reserved — no finalized
  tweet can exceed the limit.
- Default max 20 tweets; a 40-tweet thread is a sermon. Cut the text or
  raise `max_tweets` deliberately.

### 2. One-line hooks
```python
from twitter import fit_hook
```
- Persian renders fewer chars per timeline line — a hook that needs line
  2 is dead.
- Dealbreakers: greetings, thread announcements, 🧵 as content substitute,
  follow/RT asks in line one.
- Numbers stop the scroll: «۸۰٪», «۴۰۰ms». «خیلی» and «زیاد» don't.

## Anti-fabrication (hard rule)
Numbers and names come from the user; if absent, keep `{{عدد شما}}` empty
and flag it.

## Honest limit
These tools measure length exactly, not quality — trust impressions data
over the score.
