# -*- coding: utf-8 -*-
"""Persian/Arabic character classes, digit maps and script constants.

This module is the single source of truth for every character class used
across the Persian NLP engine. Nothing here ever strips or drops ZWNJ
(U+200C) — it is an orthographic character in Persian, not noise.

Convention:
  - ``PERSIAN_*`` names mean *Persian script as written in Iran*.
  - ``ARABIC_*``  names mean *characters inherited from the Arabic block*.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Invisible control characters (all preserved by the normalizer)
# ---------------------------------------------------------------------------

ZWNJ = "\u200c"   # Zero-Width Non-Joiner — essential Persian orthography (می‌خوره)
ZWJ = "\u200d"    # Zero-Width Joiner (rare; preserved)
LRM = "\u200e"    # Left-to-Right Mark
RLM = "\u200f"    # Right-to-Left Mark
BIDI_CTRL = LRM + RLM + ZWNJ + ZWJ

# ---------------------------------------------------------------------------
# Letters
# ---------------------------------------------------------------------------

def _expand(spec: str) -> str:
    """Expand 'a-z' style range specs into real characters.

    Range specs are valid *inside regex character classes* only; everywhere
    else (membership tests like ``ch in X``) they silently fail because
    ``in`` is substring search, not range membership. We expand once here so
    every constant below works correctly for BOTH uses.
    """
    out: list[str] = []
    i = 0
    while i < len(spec):
        if i + 2 < len(spec) and spec[i + 1] == "-":
            lo, hi = ord(spec[i]), ord(spec[i + 2])
            out.extend(chr(c) for c in range(lo, hi + 1))
            i += 3
        else:
            out.append(spec[i])
            i += 1
    return "".join(out)


# Arabic block letters (U+0621–U+063A, U+0641–U+064A) — includes the Persian
# subset but also Arabic-only letters (ث ح ض ظ غ …) which occur in loanwords.
ARABIC_BLOCK_LETTERS = _expand("\u0621-\u063a\u0641-\u064a")

# Persian-specific letters missing from the contiguous Arabic ranges:
#   پ U+067E   چ U+0686   ژ U+0698   ک U+06A9   گ U+06AF   ی U+06CC
PERSIAN_EXTRAS = "\u067e\u0686\u0698\u06a9\u06af\u06cc"

# Every Persian letter (Arabic-inherited + Persian-specific), real chars.
PERSIAN_LETTERS = ARABIC_BLOCK_LETTERS + PERSIAN_EXTRAS

# Diacritics (harakat), superscript alef, small high letters, quranic marks.
DIACRITICS = _expand("\u064b-\u0655\u0670")

# Tatweel / kashida (justification extender) — removable *only* on demand.
TATWEEL = "\u0640"

# Arabic presentation forms (ﻻ ﻷ …) — folded to base letters when matching.
PRESENTATION_FORMS = _expand("\ufb50-\ufdff\ufe70-\ufeff")

# ---------------------------------------------------------------------------
# Digits
# ---------------------------------------------------------------------------

LATIN_DIGITS = "0123456789"
LATIN_LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
PERSIAN_DIGITS = "۰۱۲۳۴۵۶۷۸۹"     # U+06F0–U+06F9 (Extended Arabic-Indic)
ARABIC_DIGITS = "٠١٢٣٤٥٦٧٨٩"       # U+0660–U+0669 (Arabic-Indic)
ALL_DIGITS = LATIN_DIGITS + PERSIAN_DIGITS + ARABIC_DIGITS

# ---------------------------------------------------------------------------
# Separators & punctuation
# ---------------------------------------------------------------------------

# Thousands separators: Latin comma, Persian thousands sep U+066C (٬), plain comma
THOUSANDS_SEPARATORS = ",٬\u066c"
# Decimal separators: Latin period, Persian decimal sep U+066B (٫)
DECIMAL_SEPARATORS = ".٫\u066b"

PERSIAN_PUNCTUATION = "،؛؟«»…٬٫"
SENTENCE_TERMINALS = ".!?؟…؛!؟"

# ---------------------------------------------------------------------------
# Regex-ready composite classes (safe to drop into f"[{...}]")
# ---------------------------------------------------------------------------

#: Characters that can appear *inside* a Persian word token.
#: Includes ZWNJ so that «می‌خوره» tokenizes as ONE word — Python's ``\w``
#: and ``\b`` do NOT include ZWNJ, which is exactly why ``\b`` fails on
#: Persian (it splits the compound at the ZWNJ).
WORD_CHARS = PERSIAN_LETTERS + DIACRITICS + TATWEEL + ZWNJ + LATIN_LETTERS + ALL_DIGITS + "_"

#: Same as WORD_CHARS minus ZWNJ — for contexts where a ZWNJ is invalid
#: (e.g. inside a hashtag, where platforms break tracking).
WORD_CHARS_NO_ZWNJ = WORD_CHARS.replace(ZWNJ, "")

#: Letters only (no digits, no underscore) — for "starts with a letter" rules.
LETTER_START = PERSIAN_LETTERS + DIACRITICS + TATWEEL + LATIN_LETTERS

# ---------------------------------------------------------------------------
# Digit translation maps
# ---------------------------------------------------------------------------

FA_TO_LATIN = str.maketrans(PERSIAN_DIGITS + ARABIC_DIGITS, LATIN_DIGITS + LATIN_DIGITS)
LATIN_TO_FA = str.maketrans(LATIN_DIGITS, PERSIAN_DIGITS)
ARABIC_TO_FA = str.maketrans(ARABIC_DIGITS, PERSIAN_DIGITS)
FA_TO_ARABIC = str.maketrans(PERSIAN_DIGITS, ARABIC_DIGITS)

# ---------------------------------------------------------------------------
# Arabic → Persian letter unification (standard hazm-style fold)
# ---------------------------------------------------------------------------

#: Arabic Yeh → Persian Yeh, Arabic Kaf → Persian Keheh, etc.
ARABIC_TO_PERSIAN_LETTERS = str.maketrans({
    "\u064a": "\u06cc",  # ي Arabic Yeh → ی Persian Yeh
    "\u0643": "\u06a9",  # ك Arabic Kaf → ک Persian Kaf
    "\u0623": "\u0627",  # أ → ا
    "\u0625": "\u0627",  # إ → ا
    "\u0671": "\u0627",  # ٱ → ا
    "\u0649": "\u06cc",  # ى Alef Maksura → ی
})

# ---------------------------------------------------------------------------
# Script detection helpers
# ---------------------------------------------------------------------------

def is_persian_char(ch: str) -> bool:
    """True if *ch* is a Persian/Arabic-block letter or diacritic."""
    if not ch:
        return False
    return ch in PERSIAN_LETTERS or ch in DIACRITICS

def is_rtl_char(ch: str) -> bool:
    """True if *ch* renders right-to-left (Persian letters + RTL controls)."""
    return is_persian_char(ch) or ch in (ZWNJ, ZWJ, RLM)

def is_digit_char(ch: str) -> bool:
    """True for Latin, Persian or Arabic digits."""
    return ch in ALL_DIGITS
