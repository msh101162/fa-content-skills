# -*- coding: utf-8 -*-
"""Persian hook formula catalog for Instagram.

Adapted natively (not translated) from two analyzed hook catalogs:
the 26-formula English catalog (`hooks.json`) and the 10 goal-tagged
formulas (IG1–IG10). Each Persian formula keeps the four-field contract:

- ``template``  — slot skeleton in idiomatic Persian
- ``goal``      — the engagement signal it is built for
                  (saves / shares / comments / follows)
- ``trap``      — the formula's own most common failure mode, in Persian
- ``match``     — regex for classifying hooks found in the wild
                  (ZWNJ-tolerant, Persian-safe — never ``\\b``)

Anti-fabrication rule (hard): every formula that needs a number or a
named entity takes it from the user — ``{{عدد شما}}`` placeholders stay
placeholders. A missing number is a weaker post; an invented one is a
retraction.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from core.regex_patterns import WORD_CHARS, ZWNJ as _Z

_F = f"[{WORD_CHARS}]"

# ---------------------------------------------------------------------------
# Catalog
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class HookFormula:
    id: str
    name_fa: str
    template_fa: str
    example_fa: str
    goal: str                 # saves | shares | comments | follows
    trap_fa: str
    match: str                # regex source (ZWNJ-tolerant)


HOOKS: tuple[HookFormula, ...] = (
    HookFormula(
        "FA01", "عدد عجیب", "{{عدد}} نتیجه بود؛ نتیجه‌ی واقعی چیز دیگری بود.",
        "۳۰ روز نوشتم؛ نتیجه‌ی واقعی چیزی نبود که فکر می‌کردم.",
        "follows",
        "عدد قلابی. «هزینه‌اش آرامشم بود» عدد نیست و همه می‌فهمند.",
        rf"[\d\u06f0-\u06f9][\d\u06f0-\u06f9٬,]{{1,7}}\s*نتیجه",
    ),
    HookFormula(
        "FA02", "برگشت‌زنی برعکس", "همه می‌گویند {{باور رایج}}؛ برعکس است.",
        "همه می‌گویند برای فالوور باید روزی سه پست گذاشت؛ برعکس است.",
        "shares",
        "ادعای برعکسی که پشتش داده نیست، ریش‌سازی می‌شود.",
        rf"(همه|اکثر)\s*[\s{_Z}]*می[\s{_Z}]*گویند",
    ),
    HookFormula(
        "FA03", "آمار تکان‌دهنده", "{{درصد}} از {{مخاطب}} اشتباه می‌کنند در {{موضوع}}.",
        "۸۰٪ فریلنسرها قیمت را غلط می‌دهند — اشتباه همین یک عدد.",
        "saves",
        "عدد بدون منبع؛ اگر منبع نداری، عدد را از خود کاربر بگیر.",
        rf"[\d\u06f0-\u06f9]+\s*(?:٪|%|درصد)",
    ),
    HookFormula(
        "FA04", "اشتباه خودم", "این اشتباه {{زمان}} از من گرفت تا بفهمم.",
        "این اشتباه دو سال از من گرفت تا بفهمم.",
        "comments",
        "اشتباه کلی و بی‌هویت؛ باید مال خودت باشد نه الگو.",
        rf"این\s+اشتباه",
    ),
    HookFormula(
        "FA05", "نتیجه‌ی دیگری", "نتیجه‌اش {{خواسته}} نبود؛ {{چیز دیگر}} بود.",
        "نتیجه‌اش فالوور نبود؛ مشتری بود.",
        "follows",
        "دو اسم که تفاوت‌شان حس نشود، برگشت‌زن نیست.",
        rf"نتیجه[\s{_Z}]*اش\s*(نبود|چیز\s*دیگری)",
    ),
    HookFormula(
        "FA06", "غول‌آسا به‌خاطر یک چیز", "{{چیز بزرگ}} فقط به‌خاطر یک چیز شکست خورد.",
        "استارتاپ ۱۰ نفره‌مان فقط به‌خاطر یک چیز شکست خورد.",
        "shares",
        "دلیل در اسلاید دوم لو نرود — لوپ باز بماند.",
        rf"فقط\s*به[\s{_Z}]*خاطر\s*یک\s*چیز",
    ),
    HookFormula(
        "FA07", "اعتراف", "اعتراف: من {{کاری ناجور}} می‌کردم؛ از اینجا برو بچه‌ها نگفتم.",
        "اعتراف: تا یک سال پیش برای هر پست ۵ ساعت وقت می‌گذاشتم.",
        "comments",
        "اعتراف ساختگی برای ترخون شدن؛ باید هزینه واقعی داشته باشد.",
        rf"اعتراف\s*[،:\s]",
    ),
    HookFormula(
        "FA08", "دستور بدون مقدمه", "اگر {{مشکل}} داری، همین {{اقدام}} را انجام بده.",
        "اگر کپشن‌هایت دیده نمی‌شود، همین یک کار را انجام بده.",
        "saves",
        "اقدام مبهم («روی خودت کار کن») سیو نمی‌گیرد.",
        rf"اگر\s+.+\s+داری",
    ),
    HookFormula(
        "FA09", "لیست با تعدد", "{{تعداد}} چیز که اگر بدانی {{نتیجه}} می‌شود.",
        "۳ چیزی که اگر بدانی دیگر اسلاید اضافه نمی‌سازی.",
        "saves",
        "تعداد نمایشی؛ لیست ۳تایی با ۳ آیتم واقعی پشتیبانی شود.",
        rf"[\d\u06f0-\u06f9]+\s*چیز",
    ),
    HookFormula(
        "FA10", "سوال بی‌پاسخ قابل حدس", "چرا {{رفتار عجیب}}؟ جوابش عجیب‌تر است.",
        "چرا ریلزهای بی‌کیفیت‌تر بازدید بیشتر می‌گیرند؟ جوابش عجیب‌تر است.",
        "comments",
        "سوالی که در همان خط جوابش را لو می‌دهی.",
        rf"چرا\s+.+\s*[؟?]",
    ),
    HookFormula(
        "FA11", "قبل/بعد شخص ثالث", "او با {{اقدام}} در {{زمان}} به {{نتیجه}} رسید؛ بدون {{چیز غلط رایج}}.",
        "او با یک تغییر در ۶ ماه به ۲ برابر درآمد رسید؛ بدون تبلیغ.",
        "follows",
        "نتیجه‌ی دیگری که خودت نساخته‌ای — فقط با اجازه و واقعی.",
        rf"او\s+با",
    ),
    HookFormula(
        "FA12", "افشاگری الگو", "الگویی که در {{تعداد}} پست دیدم؛ تقریباً هیچ‌کس نگفته.",
        "الگویی که در ۴۰ ریلز برتر دیدم؛ تقریباً هیچ‌کس نگفته.",
        "shares",
        "عدد نمونه کوچک را مثل آمار ملی جا نزن؛ حجم نمونه را بگو.",
        rf"الگوی\s*(که|ی)",
    ),
)

#: Most-specific-first classification order (mirrors `classify_order`).
CLASSIFY_ORDER = ("FA03", "FA09", "FA11", "FA12", "FA05", "FA06", "FA02", "FA04", "FA07", "FA10", "FA08", "FA01")

_COMPILED = {h.id: re.compile(h.match) for h in HOOKS}


def classify_hook(text: str) -> str | None:
    """Classify a Persian hook found in the wild; abstain when nothing fits.

    Abstention is correct behavior: much of short-form speech has no
    formula at all — forcing a label is noise.
    """
    for fid in CLASSIFY_ORDER:
        if _COMPILED[fid].search(text):
            return fid
    return None


def get_formula(fid: str) -> HookFormula:
    for h in HOOKS:
        if h.id == fid:
            return h
    raise KeyError(f"unknown formula id: {fid}")


# ---------------------------------------------------------------------------
# Hook scoring (five properties, Persian-native weights)
# ---------------------------------------------------------------------------

DEALBREAKERS: tuple[tuple[str, str], ...] = (
    (rf"(?i)(سلام|درود)\s*(به\s*(همه|دوستان|همگی))?", "سلام‌ورود. کسی به فید نیامده تا سلام بگیرد."),
    (rf"(?i)(در\s*(این|این\s*ویدیو|این\s*پست))", "مقدمه‌ی ویدیویی. هوک از جمله‌ای شروع می‌شود که معمولاً در ثانیه‌ی ششم می‌گویی."),
    (rf"#[{WORD_CHARS}]+", "هشتگ در هوک. هشتگ دیده می‌شود، نه شنیده."),
    (rf"[\U0001F300-\U0001FAFF\u2600-\u27BF]", "اموجی در هوک متنی؛ در خط اول ریپلای کمرنگش می‌کند."),
    (rf"فالو\s*(کن|کردن)|دنبال\s*کن", "فالو‌بیت در هوک. اول ارزش، بعد درخواست."),
)

_STAKES_WORDS = {
    "اشتباه", "هزینه", "دروغ", "خطر", "از دست", "نابود", "شکست",
    "ریش", "داغ", "خطرناک", "مرگبار", "پشیمانی", "بباخ", "باختن",
}

_YOU_WORDS = {"تو", "شما", "توئت", "خودت", "تو را", "شما را"}


@dataclass
class HookScore:
    total: float
    verdict: str            # STRONG | OK | WEAK
    properties: dict[str, float]
    dealbreakers: list[str]

    @property
    def weakest(self) -> str | None:
        if not self.properties:
            return None
        return min(self.properties, key=self.properties.get)


def score_hook(text: str) -> HookScore:
    """Five-property Persian hook panel.

    Honest calibration note (matches the source repo's published AUC):
    this panel kills obviously weak hooks reliably; it does NOT reliably
    predict winners. «به گراف نگه‌داشتن مخاطب بیشتر از این اسکریپت اعتماد کن.»
    Verdict weighting: overall = mean * 0.6 + min * 0.4 — a detector only
    needs one failing signal.
    """
    from core.counter import count as _count

    stats = _count(text)
    props: dict[str, float] = {}
    words = max(stats.words, 1)

    # LENGTH: 4-12 words is the spoken sweet spot
    props["LENGTH"] = 100.0 if 4 <= words <= 12 else (70.0 if 2 <= words <= 16 else 40.0)

    # SPECIFICITY: numbers / proper-noun-ish tokens / percentages
    concrete = 0
    from core.regex_patterns import CONCRETE_RE
    concrete += len(CONCRETE_RE.findall(text))
    concrete += len(re.findall(r"[\d\u06f0-\u06f9]+\s*(?:٪|%|درصد)", text))
    props["SPECIFICITY"] = min(100.0, 45.0 + concrete * 27.5)

    # STAKES: tension lexicon
    hits = sum(1 for w in _STAKES_WORDS if w in text)
    props["STAKES"] = min(100.0, 40.0 + hits * 30.0)

    # FRONTLOAD: payload (numbers/stakes) should not come after filler
    first12 = " ".join(text.split()[:3]).lower()
    weak_openers = ("سلام", "درود", "در این ویدیو", "قصد دارم", "همانطور که")
    props["FRONTLOAD"] = 35.0 if any(w in first12 for w in weak_openers) else 85.0

    # ADDRESS: direct you-forms beat third person
    props["ADDRESS"] = 90.0 if any(w in text for w in _YOU_WORDS) else 60.0

    dealbreakers = []
    penalty = 0.0
    for pattern, reason in DEALBREAKERS:
        if re.search(pattern, text):
            dealbreakers.append(reason)
            penalty += 15.0

    mean = sum(props.values()) / len(props)
    minimum = min(props.values())
    total = mean * 0.6 + minimum * 0.4 - penalty
    total = max(0.0, round(total, 1))
    verdict = "STRONG" if total >= 75 else ("OK" if total >= 55 else "WEAK")
    return HookScore(total=total, verdict=verdict, properties={k: round(v, 1) for k, v in props.items()}, dealbreakers=dealbreakers)


__all__ = [
    "HookFormula",
    "HOOKS",
    "CLASSIFY_ORDER",
    "classify_hook",
    "get_formula",
    "HookScore",
    "score_hook",
    "DEALBREAKERS",
]
