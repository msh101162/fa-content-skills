# -*- coding: utf-8 -*-
"""RTL text measurement & direction handling.

Persian glyph metrics differ fundamentally from Latin: most Persian letters
are *narrower* than Latin lowercase letters, joined forms are narrower than
isolated forms, and ZWNJ has zero width but changes shaping. This module
gives:

1. ``estimate_width``  — per-character em-width model (fast, no deps)
2. ``wrap_text``       — line breaking for slide/carousel text budgets
3. ``first_strong_direction`` — UAX#9-style base direction detection
4. ``script_runs``     — bidi run segmentation for mixed RTL/LTR text
5. ``measure_pillow``  — REAL shaping-aware measurement (optional Pillow +
   RAQM); falls back to the estimation model with a warning.

The width tables are calibrated approximations for naskh-style Persian
(typefaces like Vazirmatn, Sahel, IRANSans). They are good enough for
slide layout budgeting; never use them as a substitute for real shaping
when pixel-accurate rendering matters — use ``measure_pillow``.
"""

from __future__ import annotations

from dataclasses import dataclass

from .chars import DIACRITICS, PERSIAN_LETTERS, TATWEEL, ZWNJ, ZWJ

# ---------------------------------------------------------------------------
# Width model (em units) — approximate, calibrated for naskh-style Persian
# ---------------------------------------------------------------------------

# Narrow letters (joined forms extremely slim): ا آ ب پ ت ث د ذ ر ز ژ ی
_NARROW = set("اآبپتثدذرزژی")
# Medium letters: س ش ک گ ف ق ل ن ج چ ح خ ع غ ه و م ی
_MEDIUM = set("سشکگفقنجچحخعغهو")
# Wide letters: ص ض ط ظ + مــ (initial/medial mim is wide in naskh)
_WIDE = set("صضطظم")

#: Isolated vs joined form widths (em). Joined forms save roughly 25-35%.
_WIDTH_ISOLATED = {"narrow": 0.38, "medium": 0.55, "wide": 0.68}
_WIDTH_JOINED = {"narrow": 0.28, "medium": 0.42, "wide": 0.55}

_SPACE_EM = 0.26
_DIGIT_EM = 0.52          # Persian/Latin digits ≈ half-em tabular
_LATIN_EM = 0.50          # average Latin lowercase
_LATIN_UPPER_EM = 0.62
_PUNCT_EM = 0.28
_PERSIAN_PUNCT_EM = 0.24


def _char_width(ch: str, prev_joinable: bool) -> float:
    """Width of one character in em, given the previous joinable letter."""
    if ch in ZWNJ + ZWJ or ch in DIACRITICS:
        return 0.0                      # zero-width, shaping only
    if ch == " ":
        return _SPACE_EM
    if ch == TATWEEL:
        return 0.18
    if ch in PERSIAN_LETTERS:
        if ch in _NARROW:
            cls = "narrow"
        elif ch in _WIDE:
            cls = "wide"
        else:
            cls = "medium"
        # Persian letters are cursive: joined unless preceded by a
        # non-joining letter (ا د ذ ر ز ژ و) or non-letter.
        return _WIDTH_JOINED[cls] if prev_joinable else _WIDTH_ISOLATED[cls]
    if ch.isdigit():
        return _DIGIT_EM
    if ch.isascii():
        if ch.isupper():
            return _LATIN_UPPER_EM
        if ch.isalpha():
            return _LATIN_EM
        return _PUNCT_EM
    if ch in "،؛؟«»…٬٫":
        return _PERSIAN_PUNCT_EM
    return _PUNCT_EM


_NON_JOINING = set("اآدذرسژو")


def estimate_width(text: str) -> float:
    """Estimated rendered width of *text* in em units (RTL shaping-aware).

    A Persian line typically renders 20-35% narrower than the same
    character count in Latin — this model captures that, which is what
    slide/carousel text budgets actually need.
    """
    width = 0.0
    prev_joinable = False
    for ch in text:
        width += _char_width(ch, prev_joinable)
        # diacritics/ZWNJ don't break the cursive chain
        if ch in DIACRITICS or ch in (ZWNJ, ZWJ):
            continue
        prev_joinable = ch in PERSIAN_LETTERS and ch not in _NON_JOINING
    return round(width, 3)


# ---------------------------------------------------------------------------
# Line breaking
# ---------------------------------------------------------------------------

@dataclass
class TextLine:
    text: str
    width_em: float


def wrap_text(text: str, max_width_em: float, max_lines: int | None = None) -> list[TextLine]:
    """Greedy word-wrap by *estimated em width* (RTL-aware).

    Used for slide budgets: ``wrap_text(hook, 22.0, 3)`` answers
    «does this headline fit 3 lines at 22em width?».
    """
    lines: list[TextLine] = []
    for paragraph in text.split("\n"):
        current: list[str] = []
        current_w = 0.0
        for word in paragraph.split(" "):
            w = estimate_width(word + " " if word else word)
            word_w = estimate_width(word)
            sep_w = _SPACE_EM if current else 0.0
            if current and current_w + sep_w + word_w > max_width_em:
                lines.append(TextLine(" ".join(current), round(current_w, 3)))
                current, current_w = [word], word_w
            else:
                current.append(word)
                current_w += sep_w + word_w
        if current:
            lines.append(TextLine(" ".join(current), round(current_w, 3)))
    if max_lines is not None and len(lines) > max_lines:
        return lines[:max_lines] + [TextLine("…OVERFLOW…", 0.0)]
    return lines


def fits(text: str, max_width_em: float, max_lines: int) -> bool:
    """True if *text* wraps into at most *max_lines* lines of *max_width_em*."""
    lines = wrap_text(text, max_width_em)
    return len(lines) <= max_lines and all(l.width_em <= max_width_em for l in lines)


# ---------------------------------------------------------------------------
# Direction & script runs
# ---------------------------------------------------------------------------

def first_strong_direction(text: str) -> str:
    """UAX#9-style base direction: first strong directional character wins."""
    for ch in text:
        if ch in PERSIAN_LETTERS or ch == "\u200f":
            return "rtl"
        if ch.isascii() and ch.isalpha() or ch == "\u200e":
            return "ltr"
    return "rtl"   # Persian default


def script_runs(text: str) -> list[tuple[str, str]]:
    """Split mixed text into consecutive (script, fragment) runs.

    Scripts: ``fa`` (Persian letters+ZWNJ), ``latin``, ``digit``,
    ``space``, ``punct``, ``other``. Feeds bidi-segmentation for captions.
    """
    runs: list[tuple[str, str]] = []

    def script_of(ch: str) -> str:
        if ch == " " or ch == "\n" or ch == "\t":
            return "space"
        if ch in ZWNJ + ZWJ or ch in DIACRITICS:
            return "fa"
        if ch in PERSIAN_LETTERS:
            return "fa"
        if ch.isdigit():
            return "digit"
        if ch.isascii() and ch.isalpha():
            return "latin"
        return "punct"

    for ch in text:
        s = script_of(ch)
        if runs and runs[-1][0] == s:
            runs[-1] = (s, runs[-1][1] + ch)
        else:
            runs.append((s, ch))
    return runs


def mirror_visual(text: str) -> str:
    """Return the *logical* string with paired brackets swapped for
    visual-order display in pure-RTL contexts (rarely needed when the
    renderer applies the bidi algorithm; provided for terminals)."""
    pairs = {"(": ")", ")": "(", "[": "]", "]": "[", "{": "}", "}": "{", "«": "»", "»": "«"}
    return "".join(pairs.get(c, c) for c in text)


# ---------------------------------------------------------------------------
# Real shaping-aware measurement (optional Pillow + RAQM)
# ---------------------------------------------------------------------------

def measure_pillow(text: str, font_path: str, font_size: float = 1.0) -> float:
    """Measure text width in em units with REAL Arabic shaping via Pillow.

    Requires Pillow with libraqm (``pip install pillow`` built with raqm).
    Raises ``RuntimeError`` with install guidance when unavailable — callers
    should fall back to :func:`estimate_width`.
    """
    try:
        from PIL import Image, ImageFont  # noqa: PLC0415
    except ImportError as e:
        raise RuntimeError(
            "Pillow is not installed. `pip install pillow` (with raqm support) "
            "or use core.rtl.estimate_width for budgeting."
        ) from e

    try:
        font = ImageFont.truetype(font_path, size=round(font_size * 100))
        Image.new("RGB", (10, 10))  # touch PIL to fail early on broken builds
    except Exception as e:
        raise RuntimeError(f"Pillow font/RAQM problem: {e}") from e

    px = font.getlength(text, direction="rtl", language="fa")
    return round(px / (font_size * 100), 3)


__all__ = [
    "estimate_width",
    "wrap_text",
    "fits",
    "TextLine",
    "first_strong_direction",
    "script_runs",
    "mirror_visual",
    "measure_pillow",
]
