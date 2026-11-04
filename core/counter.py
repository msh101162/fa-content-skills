# -*- coding: utf-8 -*-
"""Bilingual (Persian/Latin) text statistics.

Counts are *token-based*: a ZWNJ compound («نرم‌افزار») is one word,
numbers in any digit system count as one token, and inline Latin technical
terms («repo slug», «requirements.txt») count as words without breaking
Persian counting.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .chars import (
    ALL_DIGITS,
    LATIN_DIGITS,
    PERSIAN_DIGITS,
    WORD_CHARS,
    ZWNJ,
)
from .regex_patterns import SENTENCE_SPLIT_RE, strip_token_edges, WORD_RE

_FA = f"[{PERSIAN_DIGITS}]"
_DIG = f"[{ALL_DIGITS}]"
_LATIN = "[A-Za-z]"

_WORD_BODY = f"[{WORD_CHARS}]"

# X/Twitter-style weighted length: most scripts weigh 1; CJK & hangul weigh 2.
_CJK_RE = re.compile(r"[\u1100-\u11ff\u2e80-\u9fff\uac00-\ud7a3\uf900-\ufaff\ufe30-\ufe4f]")


@dataclass
class TextStats:
    words: int = 0
    persian_words: int = 0
    latin_words: int = 0
    numeric_tokens: int = 0
    chars: int = 0
    chars_no_space: int = 0
    lines: int = 1
    sentences: int = 0
    zwnj_count: int = 0
    hashtags: int = 0
    mentions: int = 0
    reading_seconds: int = 0          # at ~200 Persian words/min
    persian_ratio: float = 0.0        # Persian words / total words
    latin_ratio: float = 0.0
    weighted_length: int = 0          # X-style (CJK×2) — tweets use this


def _script_of(token: str) -> str:
    # digits first: Persian digits (U+06F0-9) sit inside the Arabic block,
    # so a digits-only token must be classified before the fa check.
    if all(c in ALL_DIGITS or c in "_-.,٬٫:؛" for c in token) and any(c in ALL_DIGITS for c in token):
        return "num"
    has_fa = any("\u0600" <= c <= "\u06ff" for c in token)
    has_latin = any(c.isascii() and c.isalpha() for c in token)
    if has_fa:
        return "fa"
    if has_latin:
        return "latin"
    return "other"


def count(text: str, reading_wpm: int = 200) -> TextStats:
    """Full bilingual statistics for mixed Persian/Latin content."""
    stats = TextStats()
    if not text:
        return stats

    stats.chars = len(text)
    stats.chars_no_space = len(text.replace(" ", "").replace("\n", "").replace("\t", ""))
    stats.lines = text.count("\n") + 1
    stats.zwnj_count = text.count(ZWNJ)
    stats.sentences = len([s for s in SENTENCE_SPLIT_RE.split(text) if s and s.strip()])

    for raw in WORD_RE.findall(text):
        t = strip_token_edges(raw)
        if not t:
            continue
        stats.words += 1
        script = _script_of(t)
        if script == "fa":
            stats.persian_words += 1
        elif script == "latin":
            stats.latin_words += 1
        elif script == "num":
            stats.numeric_tokens += 1

    total_words = stats.words or 1
    stats.persian_ratio = round(stats.persian_words / total_words, 3)
    stats.latin_ratio = round(stats.latin_words / total_words, 3)
    stats.reading_seconds = round(stats.words * 60 / max(reading_wpm, 1))
    stats.weighted_length = weighted_length(text)
    stats.hashtags = len(re.findall(r"#\w", text))
    stats.mentions = len(re.findall(r"@[A-Za-z0-9_]", text))
    return stats


def weighted_length(text: str) -> int:
    """X/Twitter-style weighted length: every char = 1 except CJK/Hangul = 2.

    Persian, Arabic and Latin characters all weigh 1 — matches X's actual
    weighted counting since 2018. ZWNJ weighs 0 (invisible).
    """
    n = len(text) - text.count(ZWNJ)
    n += len(_CJK_RE.findall(text))   # CJK chars weigh 2 (they were counted 1)
    return n


def words(text: str) -> list[str]:
    """Token list (compounds kept whole) — convenience re-export."""
    from .regex_patterns import tokenize
    return tokenize(text)


__all__ = ["TextStats", "count", "weighted_length", "words"]
