# -*- coding: utf-8 -*-
"""YouTube title optimizer + script outliner — Persian.

Title rules (Persian-native, not translated):
- کلیدواژه جلو ببار (۵ نویسه اول در SERP و پیشنهادهای موبایل دیده می‌شود)
- ۴۵–۷۰ نویسه نقطه‌ی شیرین؛ سقف ۱۰۰
- عدد فارسی جذاب‌تر از عدد لاتین جلوه می‌کند ولی هر دو را می‌شمارد
- clickbait فارسی (= حرف بدون پشتوانه) را با پنل slop جریمه می‌کند

Script spine: قلاب سرد (۰-۱۵ ثانیه، بدون اینترو) → وعده → بدنه‌ی سکشنی
→ جمع‌بندی سیو-شدنی → CTA. هر بیت با بودجه زمانی بر پایه سرعت گفتار
فارسی (۱۴۰ کلمه/دقیقه).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from core.counter import count as count_words
from core.slop_lexicon import SlopLexicon

from .limits import PERSIAN_NARRATION_WPM, TITLE_MAX_CHARS, TITLE_SEO_WINDOW


@dataclass
class TitleVerdict:
    title: str
    chars: int
    problems: list[str]
    score: float
    ok: bool


def optimize_title(title: str, keyword: str | None = None) -> TitleVerdict:
    problems: list[str] = []
    score = 75.0
    stats = count_words(title)

    if stats.chars > TITLE_MAX_CHARS:
        problems.append(f"{stats.chars} نویسه — سقف {TITLE_MAX_CHARS}.")
        score -= 35
    if not (TITLE_SEO_WINDOW[0] <= stats.chars <= TITLE_SEO_WINDOW[1]):
        problems.append(f"{stats.chars} نویسه؛ پنجره‌ی شیرین ۴۵–۷۰ است.")
        score -= 10

    if keyword:
        if keyword in title:
            pos = title.index(keyword)
            if pos > TITLE_SEO_WINDOW[0]:
                problems.append("کلیدواژه دیر می‌آید؛ ۵ نویسه‌ی اول را در نظر بگیر.")
                score -= 15
        else:
            problems.append(f"کلیدواژه «{keyword}» اصلاً در تیتر نیست.")
            score -= 25

    if not re.search(r"[\d\u06f0-\u06f9]", title):
        problems.append("عددی در تیتر نیست؛ عدد = اعتبار + توقف اسکرول.")
        score -= 10

    slop = SlopLexicon().report(title)
    if slop.hits:
        problems.append("تیتر بوی AI می‌دهد: " + "؛ ".join(sorted({h.phrase for h in slop.hits})))
        score -= 15 * min(3, len(slop.hits))

    if re.search(r"(?i)فجایع|غافلگیر|باور نکن|شوک[ه‌]?", title):
        problems.append("کلیک‌بیت خالی؛ یوتیوب ترک‌خوردگی را جریمه می‌کند.")
        score -= 20

    score = max(0.0, round(score, 1))
    return TitleVerdict(title=title, chars=stats.chars, problems=problems, score=score, ok=score >= 60)


# ---------------------------------------------------------------------------
# Script outliner
# ---------------------------------------------------------------------------

@dataclass
class Beat:
    role: str            # hook | promise | section | recap | cta
    seconds: int
    title_fa: str
    guidance_fa: str = ""

    @property
    def mmss_fa(self) -> str:
        m, s = divmod(self.seconds, 60)
        return f"{m:02d}:{s:02d}"


@dataclass
class ScriptOutline:
    beats: list[Beat] = field(default_factory=list)
    total_seconds: int = 0
    words_budget: int = 0


def outline_script(
    topic: str,
    sections: list[str],
    target_minutes: float = 10.0,
) -> ScriptOutline:
    """Build the Persian spine with time budgets at 140 wpm narration."""
    total = int(target_minutes * 60)
    hook_s, promise_s = 15, 12
    recap_s, cta_s = 30, 20
    body_total = total - hook_s - promise_s - recap_s - cta_s
    n = max(1, len(sections))
    per_section = max(30, body_total // n)
    # distribute the floor-division remainder onto the last section
    remainder = body_total - per_section * n

    beats: list[Beat] = [
        Beat("hook", hook_s, "قلاب سرد", "بدون لوگو، بدون سلام؛ از میانه‌ی داستان شروع کن."),
        Beat("promise", promise_s, f"وعده: {topic}", "چه چیزی تا انتها می‌گیرد؛ یک جمله، یک تعهد."),
    ]
    t = hook_s + promise_s
    for i, sec in enumerate(sections):
        extra = remainder if i == len(sections) - 1 else 0
        beats.append(Beat("section", per_section + extra, sec, "هر سکشن یک ایده؛ با یک مثال ملموس فارسی ببند."))
        t += per_section + extra
    beats.append(Beat("recap", recap_s, "جمع‌بندی سیو-شدنی", "۳ خط؛ همان چیزی که کامنت‌ها ازت می‌خواهند."))
    beats.append(Beat("cta", cta_s, "درخواست واحد", "یک درخواست. سابسکرایب + زنگ + کامنت = هیچ‌کدام."))
    return ScriptOutline(beats=beats, total_seconds=t, words_budget=round(t / 60 * PERSIAN_NARRATION_WPM))


__all__ = ["TitleVerdict", "optimize_title", "Beat", "ScriptOutline", "outline_script"]
