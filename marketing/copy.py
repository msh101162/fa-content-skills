# -*- coding: utf-8 -*-
"""Persian copywriting frameworks — natively re-authored, not translated.

The analyzed copywriting skill's frameworks are ported as *structures*
with idiomatic Persian skeletons. Every framework comes with:

- ``name_fa``  — the Persian name practitioners actually use
- ``beats``    — the beat sequence with a Persian skeleton per beat
- ``guard``    — the characteristic failure mode to avoid

Editing checklist ported from the copy-editing skill, Persianized:
    «عدد به‌جای صفت، فعل به‌جای اسم، جمله کوتاه‌تر از آنچه می‌ترسی.»
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Framework:
    id: str
    name_fa: str
    name_en: str
    best_for: str
    beats: tuple[str, ...]
    guard_fa: str


FRAMEWORKS: tuple[Framework, ...] = (
    Framework(
        "PAS", "مسئله-درد-راه‌حل", "PAS", "فروش مستقیم، لندینگ، تبلیغ",
        (
            "مسئله: همان جمله‌ای که مخاطب با خواندنش سر تکان می‌دهد.",
            "درد: هزینه‌ی واقعی نکردن کاری — با عدد، نه با صفت.",
            "راه‌حل: یک تغییر مشخص + اثبات (عدد/اسم/نقل‌قول) + یک درخواست.",
        ),
        "درد را عروسی نکن؛ اگر درد درد واقعی باشد سه خط کافی است.",
    ),
    Framework(
        "AIDA", "توجه-علاقه-میل-اقدام", "AIDA", "پست فروش، ایمیل معرفی",
        (
            "توجه: عدد عجیب یا ادعای برعکس — نه سوال بلاغی.",
            "علاقه: چرا این برای «تو» مهم است؛ شما-محور بنویس.",
            "میل: تصویر نتیجه با جزئیات ملموس (بوی، صدا، عدد).",
            "اقدام: یک درخواست واحد با CTA تایپ‌شدنی.",
        ),
        "دو درخواست یعنی هیچ؛ میل را با صفت پر نکن، با جزئیات پر کن.",
    ),
    Framework(
        "BAB", "قبل-بعد-پل", "BAB", "توییتر، استوری، اسکریپت کوتاه",
        (
            "قبل: دنیای فعلی مخاطب با یک جزئیات آزاردهنده.",
            "بعد: همان دنیا پس از تغییر — قابل لمس.",
            "پل: محصول/روش به‌عنوان پل، در یک جمله.",
        ),
        "قبل و بعد باید «همان مخاطب» باشند؛ مخاطب دوم یعنی قصه دو نفر.",
    ),
    Framework(
        "4U", "چهار یو", "4U headline", "تیتر مقاله، عنوان یوتیوب",
        (
            "مفید: چه سودی، چند.",
            "فوری: تا کی.",
            "منحصربه‌فرد: چه چیزی که جای دیگر نیست.",
            "دقیق: کی، چقدر، چطور — نه «بهترین» و «بی‌نظیر».",
        ),
        "چهار یو با هم = تیتر؛ سه‌تایی خالی = اسلاب.",
    ),
    Framework(
        "FAB", "ویژگی-مزیت-سود", "FAB", "توضیح محصول، صفحه‌ی قیمت",
        (
            "ویژگی: چه دارد (فکت).",
            "مزیت: چه کار می‌کند برایت.",
            "سود: روزِ تو چطور عوض می‌شود.",
        ),
        "از ویژگی به سود نپر؛ مزیت را جا نینداز — آنجا جادوی فروش است.",
    ),
)


def framework(fid: str) -> Framework:
    for f in FRAMEWORKS:
        if f.id == fid:
            return f
    raise KeyError(f"unknown framework: {fid}")


# ---------------------------------------------------------------------------
# Persian editing checklist (copy-editing skill, re-authored)
# ---------------------------------------------------------------------------

#: «صفت‌های توخالی» — هر بار دیدی، جایگزین عدد یا جزئیات کن.
EMPTY_ADJECTIVES = ("عالی", "بی‌نظیر", "فوق‌العاده", "شگفت‌انگیز", "قدرتمند", "بهترین")

#: فعل ضعیف → فعل قوی (نمونه‌ها؛ قابل گسترش)
WEAK_VERB_MAP = {
    "انجام دادن": "کردن",
    "به دست آوردن": "گرفتن",
    "استفاده کردن از": "استفاده از",
    "قابل انجام است": "می‌شود",
}

#: قواعد خط‌کشی (بگذار یا خط بزن)
EDIT_CHECKLIST = (
    "عدد به‌جای صفت: «۴۷٪ توقف» به‌جای «توقف زیاد».",
    "فعل به‌جای اسم: «تصمیم‌گیری کنید» → «تصمیم بگیرید».",
    "جمله‌ی اول زیر ۱۲ کلمه؛ اگر بلندتر است دو جمله کن، نصفش نکن.",
    "یک ایده در هر پاراگراف؛ پاراگراف بیش از ۵ خط یعنی دو ایده.",
    "«شما» را جا بینداز: هر بند یک بار مستقیم خطاب کن.",
    "زمان حال برای نتیجه، گذشته برای اثبات؛ آینده‌ی مبهم (خواهد شد) را حذف کن.",
    "اگر جمله را بلند بخوانی و نفس کم بیاوری، آن جمله دو جمله است.",
    "هر ادعا یا عدد دارد یا اثبات، یا حذف می‌شود — «اگر عدد لازم است و نداری، جای {{عدد شما}} را خالی بگذار و پرچمش را بزن».",
)


@dataclass
class CopyEditReport:
    problems: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.problems


def quick_edit(text: str) -> CopyEditReport:
    """Fast mechanical pass over Persian copy — numbers-for-adjectives,
    weak verbs, sentence length. Judgement-level rewrites stay with the writer."""
    from core.counter import count as count_words

    rep = CopyEditReport()
    for adj in EMPTY_ADJECTIVES:
        if adj in text:
            rep.problems.append(f"صفت توخالی «{adj}» — عدد یا جزئیات بگذار.")
    for weak, strong in WEAK_VERB_MAP.items():
        if weak in text:
            rep.notes.append(f"فعل ضعیف «{weak}» → «{strong}».")
    stats = count_words(text)
    if stats.words and stats.persian_ratio < 0.5 and stats.latin_ratio > 0.4:
        rep.notes.append("متن لاتین‌محور است؛ برای مخاطب فارسی جمله‌های فارسی را پیش ببر.")
    # sentences over 25 words
    import re as _re
    for s in _re.split(r"(?<=[.!?؟…])\s+", text):
        if len(s.split()) > 25:
            rep.problems.append(f"جمله‌ی {len(s.split())}-کلمه‌ای — دو جمله کن: {s[:40]}…")
    return rep


__all__ = ["Framework", "FRAMEWORKS", "framework", "EMPTY_ADJECTIVES", "WEAK_VERB_MAP", "EDIT_CHECKLIST", "CopyEditReport", "quick_edit"]
