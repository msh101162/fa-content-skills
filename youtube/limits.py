# -*- coding: utf-8 -*-
"""YouTube platform constants for Persian content."""

from __future__ import annotations

TITLE_MAX_CHARS = 100
DESCRIPTION_MAX_CHARS = 5_000
CHAPTERS_MIN_COUNT = 3            # YouTube needs ≥3 chapters to show a bar
CHAPTER_MIN_SECONDS = 10          # each chapter ≥10s
CHAPTERS_MUST_START_AT_ZERO = True
TAGS_MAX_CHARS = 500
TAGS_MAX_COUNT = 15

#: Spoken Persian narration pace (dollgoun-to-dars style): 130-150 wpm.
PERSIAN_NARRATION_WPM = 140

#: Retention beat budgets (seconds) for a standard 8-12min video.
HOOK_SECONDS = (0, 15)            # cold open — no intro screen
INTRO_MAX_SECONDS = 20

TITLE_SEO_WINDOW = (45, 70)       # sweet spot: keyword front-loaded, fits SERP truncation

__all__ = [n for n in dir() if n.isupper()]
