# -*- coding: utf-8 -*-
"""Persian AI-slop lexicon: detection + idiomatic replacement.

This is the Persian-native counterpart of English slop linters: it targets
the clichés LLMs produce when *writing Persian* — including the signature
failure mode of literal-translation bias («باز کردن قفل پتانسیل» for
"unlock the potential"). Every pattern is ZWNJ-tolerant: «شگفت‌انگیز» and
«شگفتانگیز» both match.

Design notes
------------
- ``PHRASE_RULES``  — exact phrase patterns with severity + replacement.
- ``THRESHOLD_RULES`` — words that are fine once, slop when overused
  (counted per 100 words against a cap).
- ``score`` maps weighted density to 0 (clean) … 100 (slop soup).
- Replacements are *idiomatic Persian*, never literal translations.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .counter import count as count_words
from .regex_patterns import whole_word

# ZWNJ tolerance helper — «X‌Y» and «XY» both match
_Z = r"[\u200c]?"
_F = r"[\u0621-\u063a\u0641-\u064a\u067e\u0686\u0698\u06a9\u06af\u06cc]"  # Persian letter


def fa_phrase(phrase: str) -> str:
    """Compile a ZWNJ-tolerant, space-tolerant regex for a Persian phrase.

    Between words, both a real space and ZWNJ match («قدرت بخشیدن» and
    «قدرت‌بخشیدن»); inside a word, ZWNJ is optional («شگفت‌انگیز» and
    «شگفتانگیز»).
    """
    words = phrase.split(" ")
    pat = []
    for w in words:
        if w == "‌":
            pat.append(_Z)
        else:
            pat.append(re.escape(w).replace("‌", _Z))
    return r"[\s\u200c]*".join(pat)


@dataclass
class SlopHit:
    category: str
    phrase: str
    span: tuple[int, int]
    severity: str            # high | medium | low
    suggestion: str | None = None


@dataclass
class SlopReport:
    hits: list[SlopHit] = field(default_factory=list)
    words: int = 0
    score: float = 0.0

    @property
    def density(self) -> float:
        """Hits per 100 words."""
        return round(len(self.hits) * 100 / self.words, 2) if self.words else 0.0

    def by_category(self) -> dict[str, list[SlopHit]]:
        out: dict[str, list[SlopHit]] = {}
        for h in self.hits:
            out.setdefault(h.category, []).append(h)
        return out


# ---------------------------------------------------------------------------
# Persian slop categories
# ---------------------------------------------------------------------------

#: category → (fa_label, [(pattern_string, canonical_phrase, severity, suggestion)])
PHRASE_RULES: dict[str, tuple[str, list[tuple[str, str, str, str | None]]]] = {
    "cliche_opening": (
        "شروع‌های قالبی",
        [
            (fa_phrase("در دنیای امروز"), "در دنیای امروز", "high", "مستقیم شروع کن؛ از زمینه شروع کن نه از جهان."),
            (fa_phrase("در دنیای امروزی"), "در دنیای امروزی", "high", "مستقیم شروع کن."),
            (fa_phrase("در عصر حاضر"), "در عصر حاضر", "high", "حذفش کن یا زمان دقیق بگو."),
            (fa_phrase("در عصر دیجیتال"), "در عصر دیجیتال", "high", "مستقیم شروع کن."),
            (fa_phrase("در عصر فناوری"), "در عصر فناوری", "high", "مستقیم شروع کن."),
            (fa_phrase("در دنیای پرسرعت امروز"), "در دنیای پرسرعت امروز", "high", "بگو دقیقاً چه چیزی سریع شده و برای چه‌کسی."),
            (fa_phrase("در دنیای پرشتاب امروز"), "در دنیای پرشتاب امروز", "high", "همان بالا."),
            (fa_phrase("در جهان امروز"), "در جهان امروز", "high", "مستقیم شروع کن."),
            (fa_phrase("امروزه با پیشرفت فناوری"), "امروزه با پیشرفت فناوری", "high", "از یک مثال یا عدد واقعی شروع کن."),
            (fa_phrase("در سالهای اخیر شاهد"), "در سال‌های اخیر شاهد", "medium", "داده یا روند مشخص را نام ببر."),
        ],
    ),
    "buzzword_literal": (
        "ترجمه تحت‌اللفظی اصطلاحات هوش مصنوعی",
        [
            (fa_phrase("باز کردن قفل"), "باز کردن قفل", "high", "از این امکان استفاده کنید / بهره‌مند شوید"),
            (fa_phrase("قدرت بخشیدن"), "قدرت بخشیدن", "high", "امکان‌پذیر کردن / به ... کمک کردن"),
            (fa_phrase("قدرت بخشی"), "قدرت‌بخشی", "high", "امکان‌پذیری"),
            (fa_phrase("شیرجه زدن"), "شیرجه زدن", "medium", "وارد جزئیات شدن"),
            (fa_phrase("سفری شگفت انگیز"), "سفری شگفت‌انگیز", "high", "آغاز کردن"),
            (fa_phrase("سفر شگفت انگیز"), "سفر شگفت‌انگیز", "high", "آغاز کردن"),
            (fa_phrase("گنجینه ای از"), "گنجینه‌ای از", "medium", "مجموعه‌ای از"),
            (fa_phrase("کاوش در دنیای"), "کاوش در دنیای", "high", "با ... آشنا شوید"),
            (fa_phrase("دنیای را کاوش کنید"), "دنیای ... را کاوش کنید", "high", "با ... آشنا شوید"),
            (fa_phrase("رویای خود را به واقعیت تبدیل"), "رویای خود را به واقعیت تبدیل کنید", "high", "به هدف برسید / عملی کنید"),
            (fa_phrase("قدم برداشتن در مسیر"), "قدم برداشتن در مسیر", "medium", "شروع کنید"),
            (fa_phrase("مزیت رقابتی بی نظیر"), "مزیت رقابتی بی‌نظیر", "medium", "مزیت مشخص را اسم ببر"),
            (fa_phrase("ارزش افزوده بی نظیر"), "ارزش افزوده بی‌نظیر", "medium", "ارزش مشخص را اسم ببر"),
            (fa_phrase("راهکاری انقلابی"), "راهکاری انقلابی", "high", "راهکار + چه تغییری می‌دهد"),
            (fa_phrase("نقطه عطف"), "نقطه عطف", "low", "فقط وقتی واقعاً نقطه عطف است"),
        ],
    ),
    "empty_intensifier": (
        "شدت‌دهنده‌های خالی",
        [
            (fa_phrase("به طرز شگفت انگیزی"), "به‌طرز شگفت‌انگیزی", "high", "حذف؛ خود موضوع را قوی کن"),
            (fa_phrase("به طرز چشمگیری"), "به‌طرز چشمگیری", "medium", "عدد واقعی بگذار"),
            (fa_phrase("به شکل باور نکردنی"), "به‌شکل باورنکردنی", "high", "عدد واقعی بگذار"),
            (fa_phrase("شگفت انگیز"), "شگفت‌انگیز", "medium", None),
            (fa_phrase("حیرت انگیز"), "حیرت‌انگیز", "medium", None),
            (fa_phrase("بی نظیر"), "بی‌نظیر", "medium", None),
            (fa_phrase("خارق العاده"), "خارق‌العاده", "high", None),
            (fa_phrase("جادویی"), "جادویی", "medium", None),
            (fa_phrase("انقلابی"), "انقلابی", "medium", None),
            (fa_phrase("فوق العاده"), "فوق‌العاده", "low", None),
        ],
    ),
    "structural_tell": (
        "قالب‌های ساختاری",
        [
            (fa_phrase("نکته مهم این است که"), "نکته مهم این است که", "medium", "مستقیم همان نکته را بگو"),
            (fa_phrase("نکته کلیدی اینجاست"), "نکته کلیدی اینجاست", "medium", "مستقیم همان نکته را بگو"),
            (fa_phrase("همانطور که می دانید"), "همانطور که می‌دانید", "high", "حذف کامل؛ مخاطب می‌داند"),
            (fa_phrase("همانطور که قبلا اشاره شد"), "همانطور که قبلاً اشاره شد", "medium", "حذف یا ارجاع دقیق"),
            (fa_phrase("در این مقاله به بررسی"), "در این مقاله به بررسی", "high", "بدون مقدمه‌چینی وارد موضوع شو"),
            (fa_phrase("در این مطلب قصد داریم"), "در این مطلب قصد داریم", "high", "بدون مقدمه‌چینی وارد موضوع شو"),
            (fa_phrase("قصد داریم به بررسی"), "قصد داریم به بررسی", "medium", "مستقیم شروع کن"),
            (fa_phrase("بدون شک"), "بدون شک", "low", None),
            (fa_phrase("در نهایت"), "در نهایت", "low", None),
            (fa_phrase("به طور کلی"), "به‌طور کلی", "low", None),
            (fa_phrase("علاوه بر این"), "علاوه بر این", "low", None),
            (fa_phrase("از سوی دیگر"), "از سوی دیگر", "low", None),
            (fa_phrase("به عبارت دیگر"), "به عبارت دیگر", "low", None),
            (fa_phrase("در انتهای این مطلب"), "در انتهای این مطلب", "medium", "لینک یا CTA مستقیم"),
            (fa_phrase("فراموش نکنید که"), "فراموش نکنید که", "medium", "حذف؛ خود نکته را بگو"),
            (fa_phrase("با افتخار اعلام می کنیم"), "با افتخار اعلام می‌کنیم", "medium", "خبر را مستقیم بگو"),
        ],
    ),
    "stock_cta": (
        "CTAهای قالبی",
        [
            (fa_phrase("بیشتر بدانید"), "بیشتر بدانید", "low", "بگو دقیقاً چه چیزی یاد می‌گیرد"),
            (fa_phrase("همین حالا شروع کنید"), "همین حالا شروع کنید", "medium", "اقدام مشخص: چی را، از کجا"),
            (fa_phrase("با ما تماس بگیرید"), "با ما تماس بگیرید", "low", None),
            (fa_phrase("منتظر شما هستیم"), "منتظر شما هستیم", "low", None),
            (fa_phrase("سفر خود را آغاز کنید"), "سفر خود را آغاز کنید", "high", "فعل مشخص: ثبت‌نام کنید، دانلود کنید"),
            (fa_phrase("از مزایای بی نظیر"), "از مزایای بی‌نظیر", "high", "دو مزیت واقعی اسم ببر"),
        ],
    ),
    "ai_cadence": (
        "کادنس‌های شناخته‌شده AI (بازآفرینی فارسی الگوهای sloplint)",
        [
            # «نه فقط یک ابزار، بلکه …» — hallmark's "Not X. Y." cadence
            (r"نه\s+فقط\s+[\w\u200c\s،]+،\s*بلکه\s+", "نه فقط …، بلکه …", "medium",
             "رابطه را با یک جمله‌ی واقعی بگو؛ این قالب ریتمیک امضای AI است."),
            # «یکپارچه، قدرتمند و انقلابی» — the Persian buzzword triad seed
            (r"(?:یکپارچه|قدرتمند|انقلابی|هوشمند)[\s\u200c]*،\s*(?:یکپارچه|قدرتمند|انقلابی|هوشمند)[\s\u200c]*،?\s*و\s*(?:یکپارچه|قدرتمند|انقلابی|هوشمند)",
             "سه‌صفت پشت‌سرهم", "high", "دو مورد را ببر؛ هر صفت باید پشتوانه داشته باشد."),
            # «با ♥ ساخته شده» badge
            (r"با\s*♥\s*(ساخته|ساختم|طراحی)", "با ♥ ساخته شده", "low", None),
            # «دنیای X را تغییر می‌دهد» grandiosity
            (fa_phrase("دنیای را تغییر می دهد"), "دنیای … را تغییر می‌دهد", "high", "بگو دقیقاً چه چیزی برای چه‌کسی عوض می‌شود"),
            (fa_phrase("بازی را تغییر می دهد"), "بازی را تغییر می‌دهد", "high", "همان بالا"),
        ],
    ),
}

#: Overuse thresholds: (word, max per 100 words, severity)
THRESHOLD_RULES: list[tuple[str, float, str]] = [
    ("بی‌نظیر", 0.3, "medium"),
    ("شگفت‌انگیز", 0.3, "medium"),
    ("فوق‌العاده", 0.5, "low"),
    ("در نهایت", 0.5, "low"),
    ("علاوه بر این", 0.5, "low"),
    ("از سوی دیگر", 0.5, "low"),
    ("به عبارت دیگر", 0.4, "low"),
    ("بدون شک", 0.3, "low"),
    ("قطعاً", 0.4, "low"),
]

#: Rule-of-three: «X، Y و Z» — count per 100 words
RULE_OF_THREE_RE = re.compile(
    rf"{_F}+(?:{_Z}{_F}+)*\s*،\s*{_F}+(?:{_Z}{_F}+)*\s*و\s*{_F}+(?:{_Z}{_F}+)*"
)

#: Em-dash overuse — Persian barely uses «—» in human writing
EM_DASH = "—"

_SEVERITY_WEIGHT = {"high": 3.0, "medium": 2.0, "low": 1.0}


# ---------------------------------------------------------------------------
# Scanner
# ---------------------------------------------------------------------------

class SlopLexicon:
    """Detect and repair Persian AI-slop."""

    def __init__(self, extra_phrases: dict[str, list[tuple[str, str, str, str | None]]] | None = None):
        self.rules = dict(PHRASE_RULES)
        if extra_phrases:
            for cat, items in extra_phrases.items():
                label = self.rules.get(cat, (cat, []))[0]
                self.rules[cat] = (label, self.rules.get(cat, (cat, []))[1] + items)

    # -- detection ----------------------------------------------------------

    def scan(self, text: str) -> list[SlopHit]:
        hits: list[SlopHit] = []
        for cat, (_label, items) in self.rules.items():
            for pat, phrase, severity, suggestion in items:
                for m in re.finditer(pat, text, flags=re.IGNORECASE):
                    hits.append(SlopHit(cat, phrase, (m.start(), m.end()), severity, suggestion))

        stats = count_words(text)
        per100 = max(stats.words, 1) / 100.0

        # threshold words (ZWNJ-tolerant)
        for word, cap, severity in THRESHOLD_RULES:
            pat = whole_word(word)
            n = len(pat.findall(text))
            if n > 1 and (n / per100) > cap:
                for m in pat.finditer(text):
                    hits.append(SlopHit("overuse", word, (m.start(), m.end()), severity, "کمتر استفاده کن؛ مشخص بنویس"))

        # rule-of-three density
        n_rot = len(RULE_OF_THREE_RE.findall(text))
        if n_rot >= 2 and (n_rot / per100) > 0.4:
            for m in RULE_OF_THREE_RE.finditer(text):
                hits.append(SlopHit("rule_of_three", m.group(0), (m.start(), m.end()), "low", "اگر سه‌تایی اجباری نیست، دو مورد مهم را نگه دار"))

        # em-dash density
        n_dash = text.count(EM_DASH)
        if n_dash >= 2 and (n_dash / per100) > 0.5:
            for i, m in enumerate(re.finditer(re.escape(EM_DASH), text)):
                hits.append(SlopHit("em_dash", "—", (m.start(), m.end()), "low", "در فارسی به‌جای خط‌تیره از ویرگول یا نقطه استفاده کن"))

        hits.sort(key=lambda h: h.span[0])
        return hits

    def report(self, text: str) -> SlopReport:
        hits = self.scan(text)
        stats = count_words(text)
        weight = sum(_SEVERITY_WEIGHT[h.severity] for h in hits)
        per100 = max(stats.words, 1) / 100.0
        raw = (weight / per100)
        score = min(100.0, round(raw * 8, 1))
        return SlopReport(hits=hits, words=stats.words, score=score)

    # -- repair ---------------------------------------------------------------

    def clean(self, text: str, max_severity: str = "high") -> str:
        """Apply replacement suggestions for hits at-or-above *max_severity*."""
        order = {"low": 0, "medium": 1, "high": 2}
        text = text.replace("\u200c", "\u200c")  # explicit no-op: ZWNJ preserved
        for cat, (_label, items) in self.rules.items():
            for pat, _phrase, severity, suggestion in items:
                if suggestion is None or order[severity] < order[max_severity]:
                    continue
                text = re.sub(pat, lambda _m, s=suggestion: s, text, flags=re.IGNORECASE)
        return text


__all__ = ["SlopLexicon", "SlopHit", "SlopReport", "PHRASE_RULES", "THRESHOLD_RULES", "fa_phrase"]
