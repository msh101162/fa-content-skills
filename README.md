# fa-content-skills — مجموعه مهارت محتوای فارسی

مهارت‌های تولید محتوای شبکه‌های اجتماعی، **به‌طور بومی برای زبان فارسی**
بازطراحی شده‌اند — نه ترجمه‌شده. این مخزن نقص‌های نظام‌مند ابزارهای فارسی
را حل می‌کند: خطای مرزواژه در regex، حذف نیم‌فاصله (ZWNJ)، شمارش اشتباه
متن دوزبانه، سنجش نادرست عرض خط RTL و ترجمه تحت‌اللفظی اصطلاحات هوش
مصنوعی.

> English version: [README.en.md](README.en.md)

## معماری

```
fa-content-skills/
  core/          ← هسته مشترک (~۷۰٪ منطق): tokenizer دوزبانه، شمارنده،
                   واژه‌نامه ضد-AI-slop فارسی، قواعد ZWNJ، تایپوگرافی RTL
  instagram/     ← کاروسل، کپشن، هوک ریلز، انسانی‌ساز + SKILL.md
  twitter/       ← محاسبه وزنی ترد، هوک یک‌خطی + SKILL.md
  youtube/       ← اسکریپت، تیتر، فصل‌بندی + SKILL.md
  marketing/     ← سئو فارسی و کپی‌رایتینگ فارسی + SKILL.md
  tests/         ← ۱۰۷ تست: متن دوزبانه، ارقام فارسی، حفظ ZWNJ
  docs/          ← راهنمای توسعه و مستندات عمیق
  examples/      ← نمونه‌های اجرایی
```

## حل‌شده‌ها (چرا این هسته متفاوت است)

| نقص رایج | در fa-content-skills |
|---|---|
| `\b` پایتون روی «می‌خوره» خطا می‌دهد (ZWNJ مرزواژه نیست) | کلاس نویسه فارسی + lookaround؛ «می‌خوره» یک توکن کامل |
| نرمال‌سازی ZWNJ را پاک می‌کند | قرارداد تست‌محور: تعداد ZWNJ فقط **افزایش** می‌یابد |
| شمارنده لاتینِ متن دوزبانه | توکن‌ساز دوزبانه؛ «pip» و «requirements.txt» شمرده، ترکیب‌ها یکی |
| `CONCRETE_RE` فقط `0-9` | «۶۰۰۰» و «۶٬۰۰۰» و «6,000» و «۱٫۵» همه شمرده |
| هشتگ فارسی نمی‌گیرد | `#گیت_هاب` و `#پایتون۳`؛ هشتگ ZWNJ-دار به‌عنوان «خراب» پرچم می‌شود |
| بودجه متن اسلاید با معیار لاتین | مدل عرض RTL: فارسی ۲۰–۳۵٪ باریک‌تر رندر می‌شود |
| «باز کردن قفل پتانسیل» | واژه‌نامه slop فارسی با جایگزین اصطلاح‌محور |

## شروع سریع

```bash
pip install -e ".[dev]"
pytest                      # ۱۰۷ تست
```

```python
from core import normalize, tokenize, count, estimate_width, SlopLexicon
from instagram import lint, score_hook, plan_carousel, humanize
from twitter import thread_from_text, fit_hook
from youtube import optimize_title, outline_script, validate_block
from marketing import keyword_variants, audit_page, framework, quick_edit

# ZWNJ-safe normalization: «میخوره» → «می‌خوره»؛ «می‌خوره» دست‌نخورده می‌ماند
print(normalize("کتابهای جدید را میخوانم"))
# → «کتاب‌های جدید را می‌خوانم»

print(count("با pip پکیجی با ۶٬۰۰۰ ستاره نصب کردم"))   # دوزبانه، دقیق
print(SlopLexicon().report("در دنیای امروز قفل پتانسیلت را باز کن").score)

th = thread_from_text("متن طولانی فارسی + Tailwind CSS …")   # ترد (۱/۵)
print(thread_from_text("متن طولانی").render())
```

## اصول طراحی (از تحلیل ۴ مخزن الگو)

۱. **مدل تصمیم می‌گیرد؛ اسکریپت اندازه می‌گیرد** — هر قضاوت عددی به ابزار
   stdlib سپرده شده؛ هیچ‌چیز چشمی حدس زده نمی‌شود.
۲. **درِ تأیید، نه تنظیم** — این مهارت‌ها می‌نویسند؛ انتشار با انسان است.
۳. **عدد ساختنی ممنوع** — فرمول‌ها عدد می‌خواهند؛ اگر کاربر نداد،
   `{{عدد شما}}` خالی می‌ماند و پرچم می‌خورد.
۴. **صداقت کالیبراسیون** — ابزارها می‌گویند در چه چیزی بد هستند (مثلاً
   پنل هوک: کشتن هوک ضعیف مؤثر است، پیش‌بینی برنده نه).
۵. **اقدام محور** — قواعد فقط در یک فایل؛ هر مهارت فقط override خودش.

## الهام (بدون فورک)

این مخزن بازآفرینی مستقل است؛ الهام از:

- [Jakeschincariol/instagram-agent-skill](https://github.com/Jakeschincariol/instagram-agent-skill) — معماری بسته‌ی مهارت، پنل هوک، انسانی‌ساز، درِ تأیید
- [sergebulaev/instagram-skills](https://github.com/sergebulaev/instagram-skills) — فرمول‌های هوک هدفمند، لایه‌بندی مراجع، چک‌های CI
- [Nutlope/hallmark](https://github.com/Nutlope/hallmark) — ایده lint ساختاری (sloplint) و قالب‌گذاری visual
- [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills) — سازماندهی مهارت‌های سئو/کپی‌رایتینگ

همه کد فارسی، regex فارسی و واژه‌نامه‌های فارسی **اصیل** هستند — هیچ فایل
منبعی کپی یا فورک نشده. مجوز MIT؛ ثبت الهام در [LICENSE](LICENSE).

## مستندات

- [docs/EXTENDING.md](docs/EXTENDING.md) — افزودن فرمول، قاعده slop، پلتفرم جدید
- [docs/ANALYSIS.md](docs/ANALYSIS.md) — خلاصه تحلیل ۴ مخزن و تصمیمات بازآفرینی
- `instagram/SKILL.md`، `twitter/SKILL.md`، `youtube/SKILL.md`، `marketing/SKILL.md` — مهارت هر پلتفرم (فارسی، با آینه انگلیسی `SKILL.en.md`)

## مجوز

MIT — کامل در [LICENSE](LICENSE).
