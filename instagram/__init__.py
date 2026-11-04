# -*- coding: utf-8 -*-
"""fa-content-skills — Instagram module (Persian-native)."""

from .limits import (
    BIO_MAX_CHARS,
    CAPTION_MAX_CHARS,
    CAROUSEL_FRAME,
    FEED_FOLD_CHARS,
    HASHTAG_CAP,
    HASHTAG_CAP_DATE,
    NAME_FIELD_MAX_CHARS,
    PERSIAN_SPOKEN_WPM,
    REEL_SAFE,
    STORY_SAFE,
)
from .hooks import HOOKS, classify_hook, get_formula, score_hook, HookScore
from .caption import CaptionReport, lint, preview_fold, render
from .carousel import Slide, audit_deck, plan_carousel
from .humanizer import detect, humanize, HumanizeReport

__all__ = [
    "BIO_MAX_CHARS", "CAPTION_MAX_CHARS", "CAROUSEL_FRAME", "FEED_FOLD_CHARS",
    "HASHTAG_CAP", "HASHTAG_CAP_DATE", "NAME_FIELD_MAX_CHARS",
    "PERSIAN_SPOKEN_WPM", "REEL_SAFE", "STORY_SAFE",
    "HOOKS", "classify_hook", "get_formula", "score_hook", "HookScore",
    "CaptionReport", "lint", "preview_fold", "render",
    "Slide", "audit_deck", "plan_carousel",
    "detect", "humanize", "HumanizeReport",
]
