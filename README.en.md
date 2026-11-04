# fa-content-skills — Persian Content Skill Suite

Social-media content-creation skills, **natively re-engineered for
Persian** — not translated. This repository fixes the systemic Persian
NLP flaws: regex word-boundary failures, zero-width-non-joiner (ZWNJ)
stripping, wrong bilingual text counting, incorrect RTL line-width
measurement, and literal translations of AI buzzwords.

> Persian source of truth: [README.md](README.md)

## Architecture

```
fa-content-skills/
  core/          ← shared engine (~70% of logic): bilingual tokenizer,
                   counter, Persian AI-slop lexicon, ZWNJ rules, RTL typography
  instagram/     ← carousel, caption, reel hooks, humanizer + SKILL.md
  twitter/       ← weighted thread math, one-line hooks + SKILL.md
  youtube/       ← scripts, titles, chapters + SKILL.md
  marketing/     ← Persian SEO & copywriting + SKILL.md
  tests/         ← 107 tests: bilingual text, Persian digits, ZWNJ preservation
  docs/          ← extension guidelines and analysis notes
  examples/      ← runnable examples
```

## What gets fixed (why this core is different)

| Common flaw | fa-content-skills |
|---|---|
| Python's `\b` fails on «می‌خوره» (ZWNJ is not a `\w` char) | Persian char class + lookarounds; «می‌خوره» is ONE token |
| Normalizers strip ZWNJ | test-enforced contract: ZWNJ count only ever **grows** |
| Latin counters on bilingual text | bilingual tokenizer; «pip» / «requirements.txt» count, compounds stay one |
| `CONCRETE_RE` only matches `0-9` | «۶۰۰۰», «۶٬۰۰۰», «6,000», «۱٫۵» all match |
| Hashtag regexes reject Persian | `#گیت_هاب`, `#پایتون۳`; ZWNJ hashtags flagged as broken |
| Slide budgets measured Latin-style | RTL width model: Persian renders 20–35% narrower |
| «باز کردن قفل پتانسیل» (unlock-the-potential literal) | Persian slop lexicon with idiomatic replacements |

## Quick start

```bash
pip install -e ".[dev]"
pytest                      # 107 tests
```

```python
from core import normalize, count, SlopLexicon
from instagram import lint, score_hook, plan_carousel, humanize
from twitter import thread_from_text, fit_hook
from youtube import optimize_title, outline_script, validate_block
from marketing import keyword_variants, audit_page, framework, quick_edit

print(normalize("کتابهای جدید را میخوانم"))   # → «کتاب‌های جدید را می‌خوانم»
print(count("با pip پکیجی با ۶٬۰۰۰ ستاره نصب کردم"))
th = thread_from_text("متن طولانی …")          # «(۱/۵)» Persian badges
```

## Design principles (from the 4-repo analysis)

1. **The model decides; the script measures.**
2. **Approval gate, not a setting** — skills write; humans publish.
3. **No fabricated numbers** — `{{عدد شما}}` stays empty + flagged.
4. **Calibrated honesty** — tools state what they are bad at.
5. **Canonical rules, local overrides** — one source of truth per rule.

## Attribution (inspiration, not forks)

Independent clean-room re-engineering inspired by:

- [Jakeschincariol/instagram-agent-skill](https://github.com/Jakeschincariol/instagram-agent-skill)
- [sergebulaev/instagram-skills](https://github.com/sergebulaev/instagram-skills)
- [Nutlope/hallmark](https://github.com/Nutlope/hallmark)
- [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills)

All Persian code, Persian regex and Persian lexicons are original. MIT
license; attribution in [LICENSE](LICENSE).

## Docs

- [docs/EXTENDING.md](docs/EXTENDING.md)
- [docs/ANALYSIS.md](docs/ANALYSIS.md)
- Per-platform skills: `*/SKILL.md` (Persian) + `*/SKILL.en.md`
