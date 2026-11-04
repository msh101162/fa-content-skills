# -*- coding: utf-8 -*-
"""Instagram caption linter — Persian-native.

Adapted from the analyzed caption linter (eight checks + truncation
preview), re-engineered on the Persian core: bilingual counting, ZWNJ-safe
hashtags, and a fold preview that renders the caption the way a scrolling
stranger actually sees it (the 125-character window before «… بیشتر»).

Verdicts: READY / REVIEW / FIX. ``lint().ready`` maps to exit-code 0.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from core.chars import ZWNJ
from core.counter import count as count_words
from core.regex_patterns import broken_hashtags, hashtags

from .limits import (
    ASKS_MAX,
    CAPTION_MAX_CHARS,
    EMOJI_MAX_PER_CAPTION,
    FEED_FOLD_CHARS,
    HASHTAG_CAP,
)

#: CTA kinds — regex per ask type; «دو درخواست یعنی هیچ».
_ASK_PATTERNS = {
    "comment": r"کامنت\s*(?:کن|بذار|بگذار)|نظرت\s*(?:چیه|رو)",
    "save": r"سیو\s*(?:کن|ش)|ذخیره\s*(?:کن|ش)",
    "share": r"(?:فوروارد|شیر)\s*(?:کن|ش)|به\s+(?:رفیق|دوست)\s+(?:بده|بفرست)",
    "follow": r"فالو\s*کن|دنبال\s*کن",
    "link": r"لینک\s*(?:بیو|در\s*بیو|پروفایل)",
}

_EMOJI_RE = re.compile(r"[\U0001F000-\U0001FAFF\u2600-\u27BF\u2190-\u21FF]")

_VERDICT_ORDER = {"READY": 0, "REVIEW": 1, "FIX": 2}


@dataclass
class CaptionCheck:
    name: str            # Persian label
    status: str          # ok | warn | fail
    detail: str


@dataclass
class CaptionReport:
    verdict: str = "READY"
    checks: list[CaptionCheck] = field(default_factory=list)

    @property
    def ready(self) -> bool:
        return self.verdict == "READY"


def preview_fold(caption: str) -> str:
    """The visible window a stranger sees before «… بیشتر» (125 chars).

    Persian folds at the same character budget; ZWNJ counts as part of a
    word and is not truncated mid-compound (fold snaps to the last whole
    word or ZWNJ-compound boundary).
    """
    window = caption[:FEED_FOLD_CHARS]
    if len(caption) <= FEED_FOLD_CHARS:
        return window
    # snap back to the last whitespace boundary so a compound never splits
    cut = window.rfind(" ")
    if cut > FEED_FOLD_CHARS // 2:
        window = window[:cut]
    return window + " …"


def lint(caption: str, keywords: list[str] | None = None) -> CaptionReport:
    """Run the eight Persian caption checks."""
    checks: list[CaptionCheck] = []
    caption = caption.replace("\r\n", "\n")
    stats = count_words(caption)
    tags = hashtags(caption)
    broken = broken_hashtags(caption)
    lines = [l for l in caption.split("\n") if l.strip()]

    # 1. LENGTH — 2200 hard cap
    status = "ok" if stats.chars <= CAPTION_MAX_CHARS else "fail"
    checks.append(CaptionCheck("طول کپشن", status, f"{stats.chars}/{CAPTION_MAX_CHARS} نویسه، {stats.words} واژه"))

    # 2. FIRST LINE — the hook must survive the fold
    first = lines[0] if lines else ""
    first_status = "ok" if 0 < len(first) <= FEED_FOLD_CHARS else "fail"
    checks.append(CaptionCheck("خط اول (پنجره فید)", first_status, f"{len(first)} نویسه از {FEED_FOLD_CHARS}"))

    # 3. HOOK IS CONCRETE — numbers/names inside the visible window
    window = preview_fold(caption)
    has_concrete = bool(re.search(r"[\d\u06f0-\u06f9]", window)) or bool(re.search(r"«.+»", window))
    checks.append(CaptionCheck(
        "هوک ملموس", "ok" if has_concrete else "warn",
        "عدد یا نقل‌قول در پنجره‌ی فید" if has_concrete else "عدد/اسم/نقل‌قول ملموس در ۱۲۵ نویسه‌ی اول بگذار",
    ))

    # 4. HASHTAGS — cap of 5 (since 18 Dec 2025), zero ZWNJ tags
    tag_status = "ok"
    detail = f"{len(tags)} هشتگ (سقف {HASHTAG_CAP})"
    if len(tags) > HASHTAG_CAP:
        tag_status = "fail"
        detail += " — سقف ۵تایی از ۱۴۰۴/۰۹/۲۷ (۱۸ Dec 2025)"
    if broken:
        tag_status = "fail"
        detail += f" — هشتگ ZWNJ-دار می‌شکند: {', '.join(broken[:3])}"
    checks.append(CaptionCheck("هشتگ‌ها", tag_status, detail))

    # 5. TAG PLACEMENT — tags live at the end (or first comment), not mid-text
    if tags:
        tail = caption[caption.rfind(tags[-1]) + len(tags[-1]):]
        tags_at_end = not tail.strip()
        checks.append(CaptionCheck("جای هشتگ", "ok" if tags_at_end else "warn",
                                   "انتهای کپشن یا کامنت اول؛ وسط متن نه" if tags_at_end else "هشتگ وسط متن است"))
    else:
        checks.append(CaptionCheck("جای هشتگ", "ok", "هشتگی نیست — عبارت‌های جست‌وجو را داخل متن بنویس"))

    # 6. LINKS — captions are not clickable
    has_url = bool(re.search(r"https?://|www\.", caption))
    checks.append(CaptionCheck("لینک", "fail" if has_url else "ok",
                               "لینک در کپشن کلیک‌شدنی نیست؛ ببرش بیو یا استوری"))

    # 7. ONE ASK — regex-detected CTA types; two asks is the same as none
    asks = [name for name, pat in _ASK_PATTERNS.items() if re.search(pat, caption)]
    ask_status = "ok" if len(asks) <= ASKS_MAX else "fail"
    checks.append(CaptionCheck("درخواست واحد", ask_status,
                               f"{len(asks)} درخواست: {', '.join(asks) or 'هیچ'}"))

    # 8. EMOJI density — proportionally louder in Persian short text
    emoji_n = len(_EMOJI_RE.findall(caption))
    emoji_status = "ok" if emoji_n <= EMOJI_MAX_PER_CAPTION else "warn"
    checks.append(CaptionCheck("اموجی", emoji_status, f"{emoji_n} اموجی (حداکثر {EMOJI_MAX_PER_CAPTION}، خط هوک صفر)"))

    # 9. SEARCH TERMS (optional) — keywords present as normal phrases
    if keywords:
        missing = [k for k in keywords if k not in caption]
        checks.append(CaptionCheck("عبارت‌های جست‌وجو",
                                   "ok" if not missing else "warn",
                                   "همه حاضرند" if not missing else f"غایب: {', '.join(missing)}"))

    # verdict: any fail → FIX; any warn → REVIEW
    statuses = {c.status for c in checks}
    verdict = "FIX" if "fail" in statuses else ("REVIEW" if "warn" in statuses else "READY")
    return CaptionReport(verdict=verdict, checks=checks)


def render(report: CaptionReport, caption: str) -> str:
    """Receipt the way the source pack renders it: fold box first, then checks."""
    lines = ["┌─ پنجره‌ی فید (۱۲۵ نویسه) ─", *(f"│ {l}" for l in preview_fold(caption).split("\n")), "└─", ""]
    icons = {"ok": "✓", "warn": "!", "fail": "✗"}
    for c in report.checks:
        lines.append(f"[{icons[c.status]}] {c.name}: {c.detail}")
    lines.append("")
    lines.append(f"نتیجه: {report.verdict} — «همان یکی را درست کن و دوباره اجرا کن.»")
    return "\n".join(lines)


__all__ = ["CaptionReport", "CaptionCheck", "lint", "preview_fold", "render"]
