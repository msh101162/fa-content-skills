# -*- coding: utf-8 -*-
"""YouTube chapter handling — Persian.

Format: «۰۰:۰۰ مقدمه» — Persian digits accepted on input and emitted on
output; Latin digits accepted for compatibility. Validation mirrors
YouTube's real chapter bar rules: starts at 00:00, ≥3 chapters, each ≥10s,
strictly ascending, no overlap.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from core.digits import to_latin_digits, to_persian_digits

from .limits import CHAPTER_MIN_SECONDS, CHAPTERS_MIN_COUNT

# ۰۰:۰۰ / 00:00 / ۱:۰۲:۳۰ / 1:02:30 — seconds and minutes components may
# be 1-2 digits in either digit system.
_TS_RE = re.compile(r"^(?:(\d{1,2}):)?(\d{1,2}):(\d{1,2})$")


@dataclass
class Chapter:
    seconds: int
    title_fa: str

    @property
    def timestamp_fa(self) -> str:
        return seconds_to_fa(self.seconds)

    @property
    def timestamp_en(self) -> str:
        return seconds_to_latin(self.seconds)


def parse_timestamp(ts: str) -> int:
    """«۰۱:۰۲:۳۰» / «01:02:30» / «۴:۲۰» → seconds. Raises ValueError on junk."""
    ts = to_latin_digits(ts.strip())
    m = _TS_RE.match(ts)
    if not m:
        raise ValueError(f"فرمت تایم‌استمپ نامعتبر است: {ts!r} (مثال: 01:23 یا 1:02:30)")
    h, mnt, sec = (int(m.group(1) or 0), int(m.group(2)), int(m.group(3)))
    if mnt > 59 or sec > 59:
        raise ValueError(f"دقیقه/ثانیه خارج از بازه: {ts!r}")
    return h * 3600 + mnt * 60 + sec


def seconds_to_latin(total: int) -> str:
    h, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def seconds_to_fa(total: int) -> str:
    return to_persian_digits(seconds_to_latin(total))


def parse_chapters(text: str) -> list[Chapter]:
    """Parse a Persian chapter block (timestamp + title per line).

    Lines without a leading timestamp are ignored; a line like
    «۰۰:۰۰ مقدمه: چیزی که یاد می‌گیرید» parses with title «مقدمه: …».
    """
    chapters: list[Chapter] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        m = re.match(r"^([\d\u06f0-\u06f9٠-٩:]+)\s+(.+)$", to_latin_digits(line))
        if not m or ":" not in m.group(1):
            continue
        chapters.append(Chapter(seconds=parse_timestamp(m.group(1)), title_fa=m.group(2).strip()))
    return chapters


@dataclass
class ChapterReport:
    problems: list[str]
    ok: bool
    count: int


def validate(chapters: list[Chapter]) -> ChapterReport:
    problems: list[str] = []
    if len(chapters) < CHAPTERS_MIN_COUNT:
        problems.append(f"{len(chapters)} فصل — یوتیوب حداقل {CHAPTERS_MIN_COUNT} فصل لازم دارد.")
    if chapters and chapters[0].seconds != 0:
        problems.append("فصل اول باید دقیقاً ۰۰:۰۰ شروع شود.")
    for prev, cur in zip(chapters, chapters[1:]):
        if cur.seconds <= prev.seconds:
            problems.append(f"ترتیب: «{prev.title_fa}» و «{cur.title_fa}» مرتب نیستند.")
        elif cur.seconds - prev.seconds < CHAPTER_MIN_SECONDS:
            problems.append(f"فصل «{prev.title_fa}» زیر {CHAPTER_MIN_SECONDS} ثانیه است.")
    return ChapterReport(problems=problems, ok=not problems, count=len(chapters))


def format_chapters(chapters: list[Chapter], persian_digits: bool = True) -> str:
    """Emit the copy-ready chapter block."""
    lines = []
    for c in chapters:
        ts = c.timestamp_fa if persian_digits else c.timestamp_en
        lines.append(f"{ts} {c.title_fa}")
    return "\n".join(lines)


def validate_block(text: str) -> ChapterReport:
    return validate(parse_chapters(text))


__all__ = ["Chapter", "ChapterReport", "parse_timestamp", "seconds_to_fa", "seconds_to_latin", "parse_chapters", "validate", "format_chapters", "validate_block"]
