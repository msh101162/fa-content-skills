---
name: fa-marketing
description: >
  Persian SEO & copywriting: keyword orthographic variants (ZWNJ/Arabic/
  Persian folds), on-page checklist with RTL render width, PAS/AIDA/BAB/
  4U/FAB frameworks with idiomatic Persian skeletons and an editing
  checklist. Persian source of truth: SKILL.md.
---

# Persian Marketing — agent skill (English mirror)

## SEO part

### The real Persian SEO problem: orthographic variants
One keyword wears many skins on the Persian web: «خرید کتاب» / «خریدكتاب»
(Arabic kaf) / «کتاب‌ها» (ZWNJ plural). Search engines do not fold these
identically. `keyword_variants(keyword)` enumerates them for briefs.

### On-page audit with RTL render width
Title tag 45–60 chars (cap 65), but SERP truncation is by **rendered
width** — Persian is narrower, so the RTL width model is checked too
(~620px). Meta 140–160 chars, keyword in first 120. ZWNJ is never
stripped in headings/meta (stripping breaks word boundaries — and the
keyword with it). Keyword density 0.5–2.5%.

### Content brief
`BRIEF_SKELETON`: primary keyword + variants, search intent (inferred
from the live SERP, not guessed), H2/H3 outline, Persian entities, 3
internal links with descriptive anchors.

## Copywriting part
- `framework("PAS")` — also AIDA / BAB / 4U / FAB; each carries idiomatic
  Persian `beats` plus a `guard` field documenting its failure mode.
  Port the *structure*, never the translated template.
- `quick_edit(draft)`: empty adjectives → numbers/details; weak verbs →
  strong; 25+-word sentences split. Full checklist in `EDIT_CHECKLIST`.

## Anti-fabrication & slop rules
Numbers/names from the user (`{{عدد شما}}` placeholder + flag when
absent). Run the Persian slop lexicon before delivery — especially «باز
کردن قفل» (unlock), «قدرت‌بخشی» (empower), the «نه فقط …، بلکه …» cadence
and stacked adjective triads. Unproven SEO claims get cut.
