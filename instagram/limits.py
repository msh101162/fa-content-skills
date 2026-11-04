# -*- coding: utf-8 -*-
"""Instagram platform constants — every time-sensitive number carries its date.

Policy (inherited from the analyzed sources): «اگر عددی اینجا با رفتار
فعلی اینستاگرام تناقض داشت، رفتار اینستاگرام درست است.» Platform numbers
go stale; the date is part of the fact.
"""

from __future__ import annotations

from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Caption
# ---------------------------------------------------------------------------

CAPTION_MAX_CHARS = 2_200                 # hard platform cap
FEED_FOLD_CHARS = 125                     # visible in feed before «… بیشتر»
#: Instagram cut the hashtag cap from 30 to 5 per post (announcement dated
#: 18 Dec 2025; Mosseri had called tags "a label, not a distribution lever").
HASHTAG_CAP = 5
HASHTAG_CAP_DATE = "2025-12-18"

# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------

NAME_FIELD_MAX_CHARS = 30                 # NAME field (not @handle) is search-indexed
BIO_MAX_CHARS = 150
HIGHLIGHTS_RECOMMENDED = (4, 6)           # ordered by the visitor's next question
PINNED_POSTS_MAX = 3

# ---------------------------------------------------------------------------
# Visual geometry (pixels on standard exports)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SafeZone:
    width: int
    height: int
    top_clear: int
    bottom_clear: int
    side_clear: int = 0

STORY_SAFE = SafeZone(1080, 1920, top_clear=250, bottom_clear=1600)
REEL_SAFE = SafeZone(1080, 1920, top_clear=230, bottom_clear=1440, side_clear=230)
CAROUSEL_FRAME = SafeZone(1080, 1350, top_clear=0, bottom_clear=0, side_clear=120)
#: Grid crop eats the outer 120px of a 1080×1350 carousel frame.

SLIDE_MIN_COUNT = 2
SLIDE_SWEET_SPOT = (6, 10)                # never pad: a 5-point idea is a 5-point carousel
SLIDE_READ_SECONDS = 2                    # one point per slide, readable in ~2s

# ---------------------------------------------------------------------------
# Engagement-signal weighting (2026 heuristics, evidence-tier: [weak])
# ---------------------------------------------------------------------------

#: sends-per-reach is the headline metric; saves second; likes low-weight.
SIGNAL_ORDER = ("sends_per_reach", "saves", "comments_with_replies", "likes")

# ---------------------------------------------------------------------------
# Script pacing (spoken Persian)
# ---------------------------------------------------------------------------

#: Spoken Persian lands around 130–150 words/min for reels; use 140.
PERSIAN_SPOKEN_WPM = 140
HOOK_MAX_SECONDS = 3.0                    # the hook is decided in ~2s, dead by 3s
BEAT_MAX_SECONDS = 4.0                    # any single beat past 4s drags
REEL_LENGTH_RANGE_SECONDS = (15, 45)

# ---------------------------------------------------------------------------
# Emoji / asks
# ---------------------------------------------------------------------------

EMOJI_MAX_PER_CAPTION = 3                 # one emoji max in the hook line
ASKS_MAX = 1                              # two asks is the same as none

__all__ = [n for n in dir() if n.isupper()]
