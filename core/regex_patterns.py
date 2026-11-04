# -*- coding: utf-8 -*-
"""Persian-safe regex patterns.

WHY NOT ``\\b``?
    Python's ``\\b`` word boundary is defined in terms of ``\\w`` (Unicode
    word characters).  ZWNJ (U+200C), diacritics and tatweel are **not**
    ``\\w`` characters, so ``\\b`` treats every ZWNJ as a word boundary:

        re.search(r"\\bمی\\b", "می‌خوره")   # MATCHES  ← wrong!
        re.search(r"\\bخوره\\b", "می‌خوره") # MATCHES  ← wrong!

    The prefix «می» must never be treated as a standalone word, and a
    compound like «می‌خوره» must stay one token.  Every pattern here uses
    explicit lookarounds over a Persian-aware character class instead.
"""

from __future__ import annotations

import re

from .chars import (
    ALL_DIGITS,
    DECIMAL_SEPARATORS,
    LETTER_START,
    THOUSANDS_SEPARATORS,
    WORD_CHARS,
    WORD_CHARS_NO_ZWNJ,
    ZWNJ,
)

# ---------------------------------------------------------------------------
# Word tokenization
# ---------------------------------------------------------------------------

#: Matches one Persian/Latin word token. ZWNJ-joined compounds («می‌خوره»,
#: «نرم‌افزار») are a SINGLE token. Bilingual text is handled transparently:
#: «فایل requirements.txt» tokenizes as «فایل» + «requirements» + «txt».
WORD_RE = re.compile(f"[{WORD_CHARS}]+")

#: Same tokenization but ZWNJ never glues two sides (for linting raw platforms
#: that mangle ZWNJ).
WORD_RE_NO_ZWNJ = re.compile(f"[{WORD_CHARS_NO_ZWNJ}]+")


def whole_word(word: str) -> re.Pattern[str]:
    """Compile a *whole-word* matcher for a Persian/Latin word.

    Replaces ``\\b`` semantics: the match is surrounded by lookarounds over
    the Persian word-character class (which INCLUDES ZWNJ), so:

        whole_word("می").findall("می‌خوره")   -> []        (prefix blocked)
        whole_word("خوره").findall("می‌خوره") -> []        (compound intact)
        whole_word("کتاب").findall("این کتاب خوب است") -> ['کتاب']

    A match inside «کتاب‌ها» is blocked too, because ZWNJ counts as a
    word-internal character — the compound is one word.
    """
    escaped = re.escape(word)
    return re.compile(f"(?<![{WORD_CHARS}]){escaped}(?![{WORD_CHARS}])")


def strip_token_edges(token: str) -> str:
    """Remove stray ZWNJ/diacritics stuck to the *edges* of a token.

    Interior ZWNJ is never touched: «می‌خوره» → «می‌خوره» (unchanged),
    but a typo like «‌کلمه‌» → «کلمه».
    """
    return token.strip(ZWNJ + "\u0640").strip()


def tokenize(text: str) -> list[str]:
    """Tokenize mixed Persian/Latin text; compounds stay whole."""
    return [strip_token_edges(t) for t in WORD_RE.findall(text) if strip_token_edges(t)]


# ---------------------------------------------------------------------------
# Concrete numbers (Persian + Arabic + Latin digits, both separator styles)
# ---------------------------------------------------------------------------

_NUM = f"[{ALL_DIGITS}]"

#: Matches concrete numbers in every Persian content convention:
#:   «۶۰۰۰»  «۶٬۰۰۰»  «۶,۰۰۰»  «6000»  «6,000»  «۱٫۵»  «3.14»  «۲۰:۳۰» (time digits)
#: Thousands groups are constrained to 3 digits so «,» inside lists does not
#: glue unrelated numbers together.
CONCRETE_RE = re.compile(
    rf"{_NUM}+(?:[{THOUSANDS_SEPARATORS}]{_NUM}{{3}})*(?:[{DECIMAL_SEPARATORS}]{_NUM}+)?"
)

#: Percentages: «۲۰٪» «۲۰ درصد» «45%»
PERCENT_RE = re.compile(
    rf"{CONCRETE_RE.pattern}\s*(?:٪|%|درصد)"
)

#: Currency-ish: «۵۰۰ تومان» «۱۰۰۰ ریال» «$50»
CURRENCY_RE = re.compile(
    rf"(?:{CONCRETE_RE.pattern}\s*(?:تومان|ریال|دلار|یورو|هزار تومان|میلیون تومان)|(?:\$|€)\s*{CONCRETE_RE.pattern})"
)

# ---------------------------------------------------------------------------
# Hashtags & mentions
# ---------------------------------------------------------------------------

#: Persian-capable hashtag: #گیت_هاب  #پایتون۳  #python3
#: A valid hashtag starts with a LETTER (Persian or Latin — pure-numeric
#: tags like #۱۲۳ are not clickable) and never contains ZWNJ (platforms
#: break tracking on ZWNJ tags — see :func:`broken_hashtags`).
HASHTAG_RE = re.compile(f"#[{LETTER_START}][{WORD_CHARS_NO_ZWNJ}]*")

#: Raw hashtag tokens — everything word-like directly after #, used to
#: classify malformed tags.
RAW_HASHTAG_RE = re.compile(f"#[^{WORD_CHARS}\\s#]+|#[{WORD_CHARS}]+")

#: Mentions: @username (Latin, underscore, digits — platform convention).
MENTION_RE = re.compile(r"@[A-Za-z0-9_](?:[A-Za-z0-9_.]*[A-Za-z0-9_])?")


def _raw_tags(text: str) -> list[str]:
    return re.findall(f"#[{WORD_CHARS}]+", text)


def hashtags(text: str) -> list[str]:
    """All well-formed hashtags (with the leading ``#``).

    Tags containing ZWNJ or starting with a digit are excluded —
    see :func:`broken_hashtags` for the malformed ones.
    """
    out = []
    for tag in _raw_tags(text):
        body = tag[1:]
        if not body or ZWNJ in body:
            continue
        if body[0] not in LETTER_START:
            continue
        out.append(tag)
    return out


def broken_hashtags(text: str) -> list[str]:
    """Hashtags containing ZWNJ (or otherwise malformed) — content bugs.

    «#می‌خوره» breaks tracking on Instagram/X: the platform sees «#می».
    """
    out = []
    for tag in _raw_tags(text):
        body = tag[1:]
        if not body:
            continue
        if ZWNJ in body or body[0] not in LETTER_START:
            out.append(tag)
    return out


# ---------------------------------------------------------------------------
# Sentences / ellipsis / whitespace
# ---------------------------------------------------------------------------

#: Sentence split — Latin AND Persian terminals (؟ ؛ !) and newline.
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?؟…؛])\s+|\n+")

#: Runs of 3+ dots (…) — normalizable.
ELLIPSIS_RE = re.compile(r"\.{2,}|…+")

#: Whitespace runs — ZWNJ is not whitespace, never touched by this pattern.
WHITESPACE_RE = re.compile(r"[ \t\u00a0\u2000-\u200b\u202f\u205f\u3000]+")

__all__ = [
    "WORD_RE",
    "WORD_RE_NO_ZWNJ",
    "whole_word",
    "strip_token_edges",
    "tokenize",
    "CONCRETE_RE",
    "PERCENT_RE",
    "CURRENCY_RE",
    "HASHTAG_RE",
    "RAW_HASHTAG_RE",
    "MENTION_RE",
    "hashtags",
    "broken_hashtags",
    "SENTENCE_SPLIT_RE",
    "ELLIPSIS_RE",
    "WHITESPACE_RE",
]
