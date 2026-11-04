# -*- coding: utf-8 -*-
"""Shared Persian test fixtures: bilingual text, digits, ZWNJ edge cases.

Used by tests and by downstream platform modules as a regression corpus.
"""

ZWNJ = "\u200c"

MIXED_BILINGUAL = (
    "با pip و requirements.txt کار می‌کنم؛ "
    "پروژه در GitHub است و ۶٬۰۰۰ ستاره دارد."
)

PERSIAN_COMPOUNDS = [
    "می‌خوره", "نمی‌دانم", "نرم‌افزار", "کتاب‌ها", "بزرگ‌ترین",
    "می‌توانید", "بی‌نهایت", "هم‌خانه", "تاکنون‌ها",
]

# Words that LOOK like they need ZWNJ but are real words (regression guards)
FALSE_POSITIVES = ["میان", "میوه", "میهن", "بیدار", "بیمار", "بیابان", "خانه", "متر"]

PERSIAN_DIGIT_CASES = [
    ("۶۰۰۰", "6000"),
    ("۶٬۰۰۰", "6000"),
    ("۶,۰۰۰", "6000"),
    ("۳٫۵", "3.5"),
    ("۲۰۲۴", "2024"),
]

HASHTAG_CASES = {
    "valid": ["#گیت_هاب", "#پایتون۳", "#python3", "#دی_جی_کاled"],
    "broken_zwnj": ["#می‌خوره"],
    "invalid": ["#123", "#", "#!"],
}

SLOP_SAMPLES = {
    "cliche": "در دنیای امروز، در عصر دیجیتال هرکسی به دنبال موفقیت است.",
    "buzzword": "این دوره قفل پتانسیل شما را باز می‌کند و قدرت بخشیدن به تیم‌تان را ممکن می‌سازد.",
    "clean": "شبکه لوله‌های شهر پس از باران سنگین جوشید و چند کوچه غرق شد.",
}

THREAD_BILINGUAL = (
    "۱. Tailwind CSS در پروژه‌های فارسی هم جواب می‌دهد.\n"
    "۲. فونت Vazirmatn را با ۴ وزن لود کنید.\n"
    "۳. دیزاین RTL یعنی آینه‌کردن کامل، نه فقط text-align.\n"
    "۴. نکته آخر: خطای bidi را در console ببینید."
)
