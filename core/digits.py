# -*- coding: utf-8 -*-
"""Digit conversion: Persian ۰-۹ ↔ Arabic ٠-٩ ↔ Latin 0-9, plus separator handling."""

from __future__ import annotations

import re

from .chars import (
    ARABIC_DIGITS,
    DECIMAL_SEPARATORS,
    FA_TO_ARABIC,
    FA_TO_LATIN,
    LATIN_TO_FA,
    PERSIAN_DIGITS,
    THOUSANDS_SEPARATORS,
)
from .regex_patterns import CONCRETE_RE

_num_class = f"[{PERSIAN_DIGITS}{ARABIC_DIGITS}0-9]"

# «۶٬۰۰۰» / «6,000» → drop thousands separators inside numbers
_THOUSANDS_IN_NUMBER = re.compile(
    rf"(?<={_num_class})[{re.escape(THOUSANDS_SEPARATORS)}](?={_num_class}{{3}})"
)


def to_latin_digits(text: str) -> str:
    """Convert every Persian/Arabic digit to Latin. ZWNJ and letters untouched."""
    return text.translate(FA_TO_LATIN)


def to_persian_digits(text: str) -> str:
    """Convert Latin (and Arabic) digits to Persian ۰-۹.

    Deliberately skips digits inside URLs, e-mail addresses, file names and
    hashtag-like tokens so «requirements.txt» or «#پایتون۳» stay intact.
    """
    out: list[str] = []
    protect = re.compile(r"[A-Za-z][A-Za-z0-9._/#@:\-]*|https?://\S+|#\S+|@\w+")
    last_protect_end = 0
    for m in protect.finditer(text):
        # translate the plain span before this protected token
        out.append(text[last_protect_end:m.start()].translate(LATIN_TO_FA))
        out.append(m.group(0))
        last_protect_end = m.end()
    out.append(text[last_protect_end:].translate(LATIN_TO_FA))
    return "".join(out)


def to_arabic_digits(text: str) -> str:
    """Convert Persian digits to Arabic-Indic digits (rare, kept for completeness)."""
    return text.translate(FA_TO_ARABIC)


def strip_thousands_separators(text: str) -> str:
    """Remove grouping separators inside numbers: «۶٬۰۰۰»/«6,000» → «۶۰۰۰»/«6000».

    Commas between *words* («سلام، دنیا») are never touched.
    """
    return _THOUSANDS_IN_NUMBER.sub("", text)


def unify_decimal_separator(text: str) -> str:
    """Use the Persian decimal separator «٫» between Persian digits,
    «.» between Latin digits."""
    out = []
    for m in CONCRETE_RE.finditer(text):
        token = m.group(0)
        has_fa = any(c in PERSIAN_DIGITS for c in token)
        sep = "٫" if has_fa else "."
        fixed = re.sub(f"[{re.escape(DECIMAL_SEPARATORS)}]", sep, token)
        out.append((m.start(), m.end(), fixed))
    if not out:
        return text
    res, prev = [], 0
    for start, end, fixed in out:
        res.append(text[prev:start])
        res.append(fixed)
        prev = end
    res.append(text[prev:])
    return "".join(res)


def latin_int(value: int | float) -> str:
    """Format a Python number with Persian digits and «٬» thousands grouping."""
    if isinstance(value, float) and not value.is_integer():
        s = f"{value:,.2f}".rstrip("0").rstrip(".")
    else:
        s = f"{int(value):,}"
    return s.replace(",", "٬").translate(LATIN_TO_FA)


__all__ = [
    "to_latin_digits",
    "to_persian_digits",
    "to_arabic_digits",
    "strip_thousands_separators",
    "unify_decimal_separator",
    "latin_int",
]
