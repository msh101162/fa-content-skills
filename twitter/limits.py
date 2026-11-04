# -*- coding: utf-8 -*-
"""Twitter/X platform constants for Persian content.

Length is *weighted* (X 2018+): Persian, Arabic and Latin each weigh 1
per character; CJK weighs 2; ZWNJ weighs 0. Persian therefore gets the
full 280 characters — a common misconception claims RTL text is halved;
that is the old 140-era CJK rule, not Persian's.
"""

from __future__ import annotations

STANDARD_LIMIT = 280          # weighted length for standard accounts
PREMIUM_LIMIT = 25_000        # long-post tier (X Premium); keep threads default 280
HOOK_LIMIT = 280              # the hook tweet is a full tweet — no half-measures
THREAD_DEFAULT_MAX = 20       # sane thread depth before «thread» becomes «sermon»
NUMBERING_STYLE = "fa"        # «(۱/۵)» — Persian numerals in Persian threads

#: Spoken Persian in a 45s voice-over tweet ≈ 105 words; readable skim
#: budget for one tweet is ~45 words.
TWEET_READ_WORDS = 45

__all__ = [n for n in dir() if n.isupper()]
