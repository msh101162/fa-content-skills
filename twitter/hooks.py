# -*- coding: utf-8 -*-
"""One-line X hooks — Persian.

X rewards the 1-line hook; Persian rewards it *more* because the timeline
renders fewer characters per line. A Persian hook that needs line 2 to
land is a dead hook.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from core.counter import weighted_length
from core.regex_patterns import CONCRETE_RE

from .limits import STANDARD_LIMIT

#: Dealbreakers — same philosophy as the Instagram panel, X-tuned.
DEALBREAKERS: tuple[tuple[str, str], ...] = (
    (r"(?i)(سلام|درود)\b|سلام\s*(دوستان|همه)", "سلام. در تایم‌لاین X کسی منتظر سلام نیست."),
    (r"ترد\s*(جدید|امروز)|در\s*این\s*ترد", "اعلان ترد. ترد با خودِ خط اول شروع می‌شود."),
    (r"(?i)thread\s*(1/|🧵)", "پرچم ترد به‌جای محتوا. نشان (۱/۵) خودش گوینده است."),
    (r"فالو\s*کن|RT\s*کن|ریتوییت", "درخواست در خط اول. اول ارزش بده، بعد بخواه."),
)

_STAKES = {"اشتباه", "هزینه", "دروغ", "از دست", "شکست", "پشیمان", "خطر", "بباخ"}


@dataclass
class HookVerdict:
    text: str
    weighted: int
    score: float
    problems: list[str]
    ok: bool


def fit_hook(hook: str) -> HookVerdict:
    """Score + fit a 1-line Persian hook for X."""
    problems: list[str] = []
    score = 70.0
    wl = weighted_length(hook)

    if wl > STANDARD_LIMIT:
        problems.append(f"{wl} نویسه وزنی — سقف {STANDARD_LIMIT}. یا ببرش ترد کن یا تیزش کن.")
        score -= 40
    if not hook.strip():
        problems.append("هوک خالی است.")
        score = 0

    if CONCRETE_RE.search(hook):
        score += 15
    else:
        problems.append("عدد یا اسم مشخص ندارد؛ «خیلی» را با عدد عوض کن.")
        score -= 10

    if any(w in hook for w in _STAKES):
        score += 10
    else:
        problems.append("ترازو ندارد؛ یک ریسک یا هزینه واقعی اضافه کن.")
        score -= 5

    for pattern, reason in DEALBREAKERS:
        if re.search(pattern, hook):
            problems.append(reason)
            score -= 25

    score = max(0.0, round(score, 1))
    return HookVerdict(text=hook, weighted=wl, score=score, problems=problems, ok=score >= 60 and wl <= STANDARD_LIMIT)


__all__ = ["HookVerdict", "fit_hook", "DEALBREAKERS"]
