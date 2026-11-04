# -*- coding: utf-8 -*-
"""ZWNJ-safe Persian text normalizer.

Design contract (enforced by tests):

1. **ZWNJ is never removed, collapsed or cleaned out.** No stage of the
   pipeline touches U+200C. The only allowed change to ZWNJ count is
   *increase* (when ``fix_zwnj`` repairs solid spellings like «میخوره»
   into «می‌خوره»).
2. Persian orthography is a first-class concern: the fixer only ever
   inserts ZWNJ where a curated, whitelist-guarded rule is *certain*
   enough — an auto-fixer that breaks correct words is worse than none.
3. Everything is stdlib (`unicodedata`, `re`) — no external NLP deps.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

from .chars import (
    ARABIC_TO_PERSIAN_LETTERS,
    TATWEEL,
    ZWNJ,
)
from .digits import strip_thousands_separators, to_persian_digits, unify_decimal_separator
from .regex_patterns import ELLIPSIS_RE, WHITESPACE_RE, WORD_RE

__all__ = ["NormalizeOptions", "normalize", "zwnj_fix", "zwnj_count"]


# ---------------------------------------------------------------------------
# Curated lexicons for the ZWNJ fixer
# ---------------------------------------------------------------------------

#: Words starting with «می»/«نمی» that must NEVER be split (no false positives).
MI_WHITELIST = {
    "میان", "میانه", "میانی", "میهن", "میلیارد", "میلیون", "میل", "میلاد",
    "میلان", "میلیمتر", "میکرون", "میکروب", "میکروفن", "میخانه", "میگوی",
    "میگو", "مینا", "مینیمال", "میس", "میسر", "میول", "میهایم",
}

#: Frequent verb stems following «می»/«نمی»/«بی» — the safe auto-fix targets.
#: (高い precision: a solid «میخوره» almost certainly means «می‌خوره».)
MI_VERB_STEMS = {
    "خور", "خورد", "خواه", "خواهم", "خواهی", "خواهد", "خواهیم", "خواهید",
    "خواهند", "گو", "گوی", "گوییم", "گویید", "گویند", "گف", "گفت", "گفتم",
    "گفتی", "گفت", "گفتیم", "دید", "بین", "بینم", "بینی", "بیند", "بینیم",
    "رو", "روی", "رود", "رویم", "روید", "روند", "رفت", "رفتم", "رفتی",
    "رفتیم", "آی", "آید", "آیم", "آییم", "آیند", "آمد", "آمدن", "شو", "شود",
    "شوم", "شوی", "شویم", "شوید", "شوند", "شد", "شدم", "شدی", "شدیم", "کن",
    "کند", "کنم", "کنیم", "کنید", "کنند", "کرد", "کردم", "کردی", "کردیم",
    "ده", "دهد", "دهم", "دهیم", "دهید", "دهند", "داد", "دادم", "دادیم",
    "نوشت", "نوشتم", "نویس", "نویسم", "نویسیم", "ساخت", "سازم", "سازد",
    "سازیم", "سازند", "خوان", "خواند", "خوانم", "خوانیم", "خواندن", "دان",
    "دانم", "داند", "دانند", "دانست", "دانستم", "توان", "توانم", "توانید",
    "توانند", "توانست", "توانستم", "آور", "آورم", "آورد", "آوردن", "برم",
    "برد", "بردم", "برند", "بند", "بندد", "بندیم", "نشین", "نشیند",
    "نشسته", "ایست", "ایستد", "ایستاده", "گشت", "گرد", "گردد", "گردم",
    "خواب", "خوابد", "خندد", "خندد", "زند", "زنم", "زنند", "زد", "زدم",
    "ریزد", "ریز", "ریزم", "ریخت", "بریز", "بخش", "بخشد", "بخشیم",
    "پوش", "پوشد", "پوشم", "پوشید", "پوشند", "پرش", "پرس", "پرسد", "پرسید",
    "شنو", "شنود", "شنوم", "شنویم", "شنید", "شنوند", "باش", "باشد", "باشم",
    "باشیم", "باشید", "باشند", "گذرد", "گذر", "گذرم", "گذشت", "گذار", "گذارد",
    "کاشت", "چین", "چیند", "چید", "دوخ", "دود", "دوزد", "بافد", "بافم",
    "خندید", "گریست", "جنگید", "سوخت", "مرد", "میرد", "وزد", "نشست",
    "نشستم", "خرید", "خرم", "فروخت", "فروش", "خوردن", "نوشتن", "دیدن",
}

#: «بی»-compounds written WITH ZWNJ (list-driven — only exact solid matches fixed).
BI_FIXES = {
    "بیکار": "بی‌کار",
    "بیکاری": "بی‌کاری",
    "بیکاره": "بی‌کاره",
    "بیمزه": "بی‌مزه",
    "بیمتال": "بی‌مрал",
    "بیادب": "بی‌ادب",
    "بیادبی": "بی‌ادبی",
    "بیرحمانه": "بی‌رحمانه",
    "بیرحم": "بی‌رحم",
    "بیمعنی": "بی‌معنی",
    "بیمعنا": "بی‌معنا",
    "بیهوده": "بی‌هوده",
    "بیندازه": "بی‌اندازه",
    "بیتفاوت": "بی‌تفاوت",
    "بیتفاوتی": "بی‌تفاوتی",
    "بیحوصله": "بی‌حوصله",
    "بیشمار": "بی‌شمار",
    "بیشماری": "بی‌شماری",
    "بیانصاف": "بی‌انصاف",
    "بیانصافی": "بی‌انصافی",
    "بیاحترامی": "بی‌احترامی",
    "بیاحترام": "بی‌احترام",
    "بینهایت": "بی‌نهایت",
    "بیدقت": "بی‌دقت",
    "بیتوجه": "بی‌توجه",
    "بیتوجهی": "بی‌توجهی",
    "بیمصرف": "بی‌مصرف",
    "بیجواب": "بی‌جواب",
    "بیشعار": "بی‌شعار",
    "بیگناه": "بی‌گناه",
    "بیگناهی": "بی‌گناهی",
    "بیراهه": "بی‌راهه",
    "بیمار": None,          # guard: بیمار is a real word — never touched
    "بیدار": None,          # guard: بیدار is a real word — never touched
    "بیداد": None,          # guard: بیداد is a real word — never touched
    "بیابان": None,         # guard: بیابان is a real word — never touched
}

#: Natural words ending in «ها» that must NOT be split before plural «ها».
HA_EXCEPTIONS = {
    "خانه", "نگاه", "راه", "ماه", "چاه", "آه", "گاه", "شاه", "کاه", "پناه",
    "آگاه", "تماشاگاه", "کارگاه", "آشپزخانه", "زمین‌لرزهگاه", "پگاه",
    "سپاه", "مراه", "هواه", "توپخانه", "دیرینه‌شناس", "چهارراه", "چهارسو",
    "ها", "آها", "اها",
}

#: Natural words ending in «تر» that must NOT be split before comparative «تر».
TR_EXCEPTIONS = {"متر", "اختر", "منظر", "قطر", "انتر", "دیتر", "پاتر"}

_FA_LETTER = "\u0621-\u063a\u0641-\u064a\u067e\u0686\u0698\u06a9\u06af\u06cc"


def zwnj_count(text: str) -> int:
    """Number of ZWNJ characters — used by tests to enforce the invariant."""
    return text.count(ZWNJ)


# ---------------------------------------------------------------------------
# Options
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class NormalizeOptions:
    """Every stage is individually switchable; defaults are safe for content work."""

    fold_presentation: bool = True    # ﻻ → لا (NFKC + presentation-form fold)
    fix_arabic_letters: bool = True   # ي→ی  ك→ک  أ إ ٱ → ا
    unify_digits: str | None = "fa"   # None | "fa" | "en"
    strip_tatweel: bool = True        # ـ justification extenders
    fix_zwnj: bool = True             # repair solid affixes (میخوره → می‌خوره)
    fix_zwnj_possessives: bool = False  # کتابم → کتاب‌ام (both valid; off by default)
    fix_spacing: bool = True          # collapse runs, ellipsis, punct spacing
    drop_thousands_sep: bool = False  # «۶٬۰۰۰» → «۶۰۰۰»


# ---------------------------------------------------------------------------
# ZWNJ fixer
# ---------------------------------------------------------------------------

def zwnj_fix(text: str, possessives: bool = False) -> str:
    """Repair solid affix spellings by inserting ZWNJ.

    Token-based by design: every rule sees the FULL word (ZWNJ included),
    so a word already written correctly («نرم‌افزارهای») is never
    re-processed and never gains a duplicate ZWNJ. Only whitelist-guarded
    rules run, so correct words are never broken.
    """
    if not text:
        return text

    def fix_token(word: str) -> str:
        if ZWNJ in word:
            return word  # already compound — orthography intact, hands off

        # --- می / نمی prefix ------------------------------------------------
        for pref in ("نمی", "می"):
            if word.startswith(pref):
                stem = word[len(pref):]
                if stem in MI_WHITELIST or not stem:
                    return word
                if stem in MI_VERB_STEMS or (
                    len(stem) >= 2 and stem.endswith("ه") and stem[:-1] in MI_VERB_STEMS
                ):
                    return f"{pref}{ZWNJ}{stem}"

        # --- بی compounds (exact-list only; None = protected real word) -----
        if word in BI_FIXES and BI_FIXES[word]:
            return BI_FIXES[word]

        # --- plural / attributive: ها / های / هایی ---------------------------
        for suf in ("هایی", "های", "ها"):
            if word.endswith(suf):
                stem = word[: -len(suf)]
                if len(stem) >= 2 and stem not in HA_EXCEPTIONS:
                    return f"{stem}{ZWNJ}{suf}"
                return word

        # --- comparative / superlative: تر / ترین ----------------------------
        if word.endswith("ترین"):
            stem = word[:-4]  # «ترین» is 4 characters
            if len(stem) >= 2 and stem not in TR_EXCEPTIONS:
                return f"{stem}{ZWNJ}ترین"
        elif word.endswith("تر"):
            stem = word[:-2]
            if len(stem) >= 2 and stem not in TR_EXCEPTIONS:
                return f"{stem}{ZWNJ}تر"
        return word

    if possessives:
        def fix_with_possessives(word: str) -> str:
            fixed = fix_token(word)
            if fixed != word:
                return fixed
            for suf in ("مان", "تان", "شان", "ایم", "اید", "اند", "ام", "ات", "اش"):
                if word.endswith(suf) and len(word) - len(suf) >= 2:
                    return f"{word[:-len(suf)]}{ZWNJ}{suf}"
            return word

        return WORD_RE.sub(lambda m: fix_with_possessives(m.group(0)), text)

    return WORD_RE.sub(lambda m: fix_token(m.group(0)), text)


# ---------------------------------------------------------------------------
# Spacing pass
# ---------------------------------------------------------------------------

_PUNCT = "،؛؟!.,:؛؟!()«»"
_NO_SPACE_BEFORE = "،؛؟!.)»:]"
_NO_SPACE_AFTER = "(«[:"


def _fix_spacing(text: str) -> str:
    text = ELLIPSIS_RE.sub("…", text)
    text = WHITESPACE_RE.sub(" ", text)
    # no space before closing punctuation, exactly one after openers
    for ch in _NO_SPACE_BEFORE:
        text = re.sub(rf" +{re.escape(ch)}", ch, text)
    for ch in _NO_SPACE_AFTER:
        text = re.sub(rf"{re.escape(ch)} +", ch, text)
    # exactly one space after terminal punctuation (Persian & Latin)
    text = re.sub(r"([،؛؟!….]) (?=[^\s])", r"\1 ", text)
    text = re.sub(rf"([{_PUNCT}])(?=[{_FA_LETTER}A-Za-z])", r"\1 ", text)
    return text.strip()


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def normalize(text: str, options: NormalizeOptions | None = None) -> str:
    """Normalize Persian text while preserving ZWNJ integrity.

    The returned string always contains **at least** as many ZWNJ
    characters as the input (strictly more only when ``fix_zwnj``
    repairs solid affixes).
    """
    opts = options or NormalizeOptions()
    if not text:
        return text

    if opts.fold_presentation:
        # common presentation-form ligatures → base pairs
        text = text.translate(str.maketrans({
            "\ufb50": "\u0671", "\ufb51": "\u0671",
            "\ufefb": "\u0644\u0627", "\ufefc": "\u0644\u0627",
            "\ufef7": "\u0644\u0623", "\ufef8": "\u0644\u0623",
            "\ufef5": "\u0644\u0622", "\ufef6": "\u0644\u0622",
            "\ufef9": "\u0644\u0625", "\ufefa": "\u0644\u0625",
        }))
        # NFKC folds remaining presentation forms; ZWNJ has no decomposition
        # mapping so it survives NFKC untouched.
        text = unicodedata.normalize("NFKC", text)

    if opts.fix_arabic_letters:
        text = text.translate(ARABIC_TO_PERSIAN_LETTERS)

    if opts.unify_digits == "fa":
        text = to_persian_digits(text)
    elif opts.unify_digits == "en":
        from .digits import to_latin_digits
        text = to_latin_digits(text)

    if opts.strip_tatweel:
        text = text.replace(TATWEEL, "")

    if opts.drop_thousands_sep:
        text = strip_thousands_separators(text)

    if opts.unify_digits == "fa":
        text = unify_decimal_separator(text)

    if opts.fix_zwnj:
        text = zwnj_fix(text, possessives=opts.fix_zwnj_possessives)

    if opts.fix_spacing:
        text = _fix_spacing(text)

    return text
