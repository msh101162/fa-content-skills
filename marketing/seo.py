# -*- coding: utf-8 -*-
"""Persian SEO module.

Language-agnostic checklists ported from the analyzed SEO skills +
Persian-specific re-engineering:

- **Persian keyword variants** — a real Persian SEO problem: the same
  keyword exists as «خرید کتاب» / «خریدكتاب» (Arabic ك) / «خرید
  کتاب‌ها» (ZWNJ plural). Search engines treat these differently.
  ``keyword_variants`` enumerates them so briefs never miss a variant.
- **RTL width on SERP** — Google truncates Persian title tags by
  *rendered width*, not codepoints; Persian renders narrower so the
  effective title budget is slightly longer than the Latin 60-char rule.
- ZWNJ in meta/heading text is preserved (never stripped) — stripping it
  changes word boundaries and therefore keyword matching.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from core.chars import ARABIC_TO_PERSIAN_LETTERS
from core.counter import count as count_words
from core.rtl import estimate_width

TITLE_TAG_WINDOW = (45, 60)        # Latin-anchored; Persian can run ~5% wider
TITLE_TAG_HARD_MAX = 65
META_DESCRIPTION_WINDOW = (140, 160)
H1_MAX_CHARS = 70
KEYWORD_DENSITY_TARGET = (0.5, 2.5)  # percent of words — beyond 2.5 is stuffing


@dataclass
class KeywordVariants:
    canonical: str
    arabic_folded: str
    with_zwnj_plural: str
    spaced: str


def keyword_variants(keyword: str) -> KeywordVariants:
    """Enumerate the orthographic variants a Persian keyword actually
    appears in on Persian web pages."""
    canonical = keyword.translate(ARABIC_TO_PERSIAN_LETTERS)
    return KeywordVariants(
        canonical=canonical,
        arabic_folded=canonical.replace("ی", "ی").replace("ک", "ک"),
        with_zwnj_plural=canonical + "\u200cها",
        spaced=canonical,
    )


@dataclass
class PageAudit:
    problems: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.problems


def audit_page(
    title_tag: str,
    meta_description: str,
    h1: str,
    body: str,
    keyword: str | None = None,
) -> PageAudit:
    """Language-agnostic on-page audit with Persian width/density rules."""
    audit = PageAudit()
    t_chars = count_words(title_tag).chars
    m_chars = count_words(meta_description).chars
    h_chars = count_words(h1).chars

    if not (TITLE_TAG_WINDOW[0] <= t_chars <= TITLE_TAG_HARD_MAX):
        audit.problems.append(f"title tag {t_chars} نویسه است؛ بازه‌ی شیرین ۴۵–۶۰، سقف {TITLE_TAG_HARD_MAX}.")
    # Persian renders narrower: width check catches the too-long-but-few-chars case
    title_width = estimate_width(title_tag) * 18  # ≈px at 18px desktop SERP font
    if title_width > 620:
        audit.notes.append(f"عرض رندر تیتر ~{int(title_width)}px است؛ SERP در ~۶۲۰px برش می‌خورد.")

    if not (META_DESCRIPTION_WINDOW[0] <= m_chars <= META_DESCRIPTION_WINDOW[1]):
        audit.problems.append(f"meta description {m_chars} نویسه است؛ بازه ۱۴۰–۱۶۰.")
    if "\u200c" not in h1 and any("\u200c" in w for w in h1.split()):
        audit.notes.append("H1 بدون ZWNJ — «می‌»، «ها» و ترکیب‌ها را با نیم‌فاصله بنویس؛ جدا شدن کلمه = شکستن کیورد.")
    if h_chars > H1_MAX_CHARS:
        audit.problems.append(f"H1 {h_chars} نویسه است؛ سقف {H1_MAX_CHARS}.")

    if keyword:
        stats = count_words(body)
        k = keyword.translate(ARABIC_TO_PERSIAN_LETTERS)
        occurrences = sum(
            1 for w in body.split() if k in w.translate(ARABIC_TO_PERSIAN_LETTERS)
        )
        density = occurrences * 100 / max(stats.words, 1)
        if density < KEYWORD_DENSITY_TARGET[0]:
            audit.problems.append(f"چگالی کیورد {density:.1f}% زیر حداقل است؛ کیورد و واریانت‌هایش را طبیعی پخش کن.")
        elif density > KEYWORD_DENSITY_TARGET[1]:
            audit.problems.append(f"چگالی کیورد {density:.1f}% — کیورد استافینگ؛ یوتیوب گوگل جریمه‌اش می‌کند.")
        if keyword not in h1:
            audit.problems.append("کیورد در H1 نیست.")
        if keyword not in meta_description[:120]:
            audit.notes.append("کیورد را در ۱۲۰ نویسه‌ی اول توضیحات متا بگذار.")

    return audit


#: Internal-linking checklist (language-agnostic, ported from the SEO trio).
INTERNAL_LINKING_CHECKLIST = (
    "هر صفحه‌ی عمقی حداکثر ۳ کلیک از صفحه‌ی اصلی فاصله دارد.",
    "لنگر (anchor) فارسی توصیفی است، نه «اینجا کلیک کنید».",
    "صفحات ستون (pillar) به ۳–۸ صفحه‌ی خوشه‌ای لینک می‌دهند و خوشه‌ها به ستون برمی‌گردند.",
    "لینک‌های شکسته با crawl هر ماه پیدا و ترمیم می‌شوند.",
    "URL فارسی یا اسلاگ لاتین؟ یکی را انتخاب کن و در کل سایت ثابت نگه دار؛ ترنسلیتریشن نیمه‌کاره نرو.",
)

#: Persian SEO brief skeleton — what a content brief must pin down.
BRIEF_SKELETON = {
    "primary_keyword_fa": "کیورد اصلی + واریانت‌های املایی (keyword_variants)",
    "search_intent_fa": "اطلاعاتی | مقایسه‌ای | تراکنشی — از SERP فعلی استنتاج کن نه از حدس",
    "outline_fa": "H2/H3ها با سوالاتی که «همه‌چیز درباره‌ی …» را کامل می‌کنند",
    "entities_fa": "نام‌های برند/ابزار/مکان فارسی که باید ذکر شوند",
    "internal_links_fa": "۳ لینک داخلی با انکر فارسی توصیفی",
    "serp_feature_fa": "اگر SERP جدول/FAQ دارد، بلافصل همان قالب را بده",
}

__all__ = ["KeywordVariants", "PageAudit", "keyword_variants", "audit_page", "INTERNAL_LINKING_CHECKLIST", "BRIEF_SKELETON"]
