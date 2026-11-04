# -*- coding: utf-8 -*-
"""نمونه‌های سریع fa-content-skills — اجرا: python examples/quickstart.py

پوشش کامل قابلیت‌های هسته و پلتفرم‌ها در ~۴۰ خط.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core import SlopLexicon, count, estimate_width, normalize, tokenize
from instagram import audit_deck, lint, plan_carousel, preview_fold, score_hook
from marketing import framework, keyword_variants, quick_edit
from twitter import fit_hook, thread_from_text
from youtube import optimize_title, outline_script, validate_block

print("=== ۱. نرمال‌ساز ZWNJ-مصون ===")
print(normalize("کتابهای جدید را میخوانم و نمیخواهم از دستشان بدهم"))
print(normalize("می‌خوره نمی‌دانم نرم‌افزارهای 2024 را کجا می‌بینید؟"))

print("\n=== ۲. توکن‌سازی و شمارش دوزبانه ===")
print(tokenize("با pip پکیج requirements را نصب کردم"))
print(count("با pip پکیجی با ۶٬۰۰۰ ستاره نصب کردم؛ پروژه در GitHub است."))

print("\n=== ۳. ارقام فارسی ===")
from core.digits import latin_int, to_latin_digits, to_persian_digits
print(to_persian_digits("2024"))
print(to_latin_digits("۶٬۰۰۰"))
print(latin_int(1250000))

print("\n=== ۴. عرض RTL ===")
print("عرض فارسی:", estimate_width("متن نمونه فارسی"))
print("عرض لاتین:", estimate_width("sample latin text"))

print("\n=== ۵. واژه‌نامه ضد-AI-slop ===")
lex = SlopLexicon()
rep = lex.report("در دنیای امروز این نه فقط یک ابزار، بلکه یک انقلاب یکپارچه، قدرتمند و انقلابی است.")
for h in rep.hits[:5]:
    print(f"  [{h.severity}] {h.category}: {h.phrase} → {h.suggestion or '—'}")
print("امتیاز:", rep.score, "| پس از پاک‌سازی:", lex.clean(rep and "در دنیای امروز قفل پتانسیلت را باز کن", max_severity="high"))

print("\n=== ۶. اینستاگرام ===")
r = score_hook("این اشتباه دو سال از من گرفت تا بفهمم")
print("هوک:", r.total, r.verdict, "| ضعیف‌ترین ویژگی:", r.weakest)
cap = "۳ خطی که امروز نوشتم فالوورم را دو برابر کرد.\nهمین تکنیک را تمرین کن."
print("برش فید:", preview_fold(cap)[:60], "…")
print("لینت کپشن:", lint(cap).verdict)
slides = plan_carousel("سه اشتباه رزومه", ["عنوان کلی", "عکس بی‌ربط", "بدون عدد"])
print("کاروسل:", audit_deck(slides)["slides"], "اسلاید")

print("\n=== ۷. توییتر/X ===")
th = thread_from_text(
    "۱. Tailwind در فارسی جواب می‌دهد. "
    "۲. فونت Vazirmatn را preload کن. "
    "۳. RTL یعنی آینه‌کردن کامل. "
    "۴. تست را با متن فارسی واقعی بگیر نه lorem ipsum."
)
print("ترد:", len(th.tweets), "توییتی، جا می‌شود:", th.fits)
v = fit_hook("۸۰٪ پروژه‌های فارسی فونت را غلط لود می‌کنند — هزینه‌اش ۴۰۰ms است.")
print("هوک:", v.score, v.ok)

print("\n=== ۸. یوتیوب ===")
t = optimize_title("آموزش فلاتر در ۱۰ دقیقه — از صفر تا اولین اپ", keyword="آموزش فلاتر")
print("تیتر:", t.score, t.ok, t.problems or "بدون مشکل")
print(validate_block("۰۰:۰۰ مقدمه\n۰۱:۲۳ نصب\n۰۳:۴۰ اولین پروژه").ok)
o = outline_script("آموزش گراف‌کیو", ["تعریف", "پیاده‌سازی", "اشتباه‌ها"], target_minutes=10)
print("اسکریپت:", len(o.beats), "بیت |", o.words_budget, "کلمه بودجه")

print("\n=== ۹. مارکتینگ ===")
print("واریانت‌های کیورد:", keyword_variants("خرید کتاب").canonical)
f = framework("PAS")
print("PAS:", f.name_fa, "|", len(f.beats), "بیت")
print("ویرایش سریع:", quick_edit("این محصول بی‌نظیر است.").problems)

print("\nهمه قابلیت‌ها اجرا شدند — ۱۰۷ تست در tests/")
