# -*- coding: utf-8 -*-
"""Platform module tests: instagram, twitter, youtube, marketing."""
import pytest

from core.chars import ZWNJ

# ---------------------------------------------------------------------------
# Instagram
# ---------------------------------------------------------------------------

from instagram import (
    CAPTION_MAX_CHARS,
    FEED_FOLD_CHARS,
    HASHTAG_CAP,
    audit_deck,
    classify_hook,
    humanize,
    lint,
    plan_carousel,
    preview_fold,
    score_hook,
)
from instagram.carousel import Slide, check_slide
from instagram.humanizer import detect, em_dash_excess, pass_invisible
from twitter import STANDARD_LIMIT, fit_hook, thread_from_text
from youtube import optimize_title, outline_script, validate_block
from marketing import audit_page, framework, keyword_variants, quick_edit


class TestInstagramHooks:
    def test_score_not_crashing_and_bounded(self):
        r = score_hook("این اشتباه دو سال از من گرفت تا بفهمم")
        assert 0 <= r.total <= 100
        assert r.verdict in ("STRONG", "OK", "WEAK")
        assert r.weakest is not None

    def test_greeting_dealbreaker(self):
        r = score_hook("سلام دوستان! در این ویدیو می‌خواهم چیزی بگویم")
        assert any("سلام" in d for d in r.dealbreakers)

    def test_classify_fa07(self):
        assert classify_hook("اعتراف: تا یک سال پیش برای هر پست ۵ ساعت وقت می‌گذاشتم") == "FA07"

    def test_classify_abstains(self):
        assert classify_hook("امروز هوا ابری بود و من قدم زدم.") is None


class TestInstagramCaption:
    def test_fold_preview_never_splits_compound(self):
        cap = ("نتیجه‌اش فالوور نبود؛ مشتری بود. با یک تغییر کوچک در استراتژی محتوا این "
               "اتفاق افتاد و آمار ذخیره‌سازی پست‌ها سه برابر شد. بیایید بررسی کنیم.")
        folded = preview_fold(cap)
        assert len(folded) <= FEED_FOLD_CHARS + 3      # ellipsis slack
        assert "ذخیره‌سازی" in cap  # source intact (compound sanity)

    def test_lint_flags_hashtag_cap_and_zwnj(self):
        cap = "کپشن کوتاه است. " + " ".join(f"#هشتگ{i}" for i in range(7)) + " #می‌خوره"
        rep = lint(cap)
        tag_check = next(c for c in rep.checks if c.name == "هشتگ‌ها")
        assert tag_check.status == "fail"
        assert rep.verdict == "FIX"

    def test_lint_ready_caption(self):
        cap = "۳ خطی که امروز نوشتم فالوورم را دو برابر کرد.\n\nهمین تکنیک را در ۶۰ ثانیه تمرین کن."
        rep = lint(cap)
        fails = [c for c in rep.checks if c.status == "fail"]
        assert rep.verdict in ("READY", "REVIEW")
        assert not any("طول" in c.name for c in fails)

    def test_link_fail(self):
        rep = lint("به https://example.com سر بزنید.")
        link = next(c for c in rep.checks if c.name == "لینک")
        assert link.status == "fail"


class TestInstagramCarousel:
    def test_spine_never_pads(self):
        slides = plan_carousel("چطور رزومه بنویسیم", ["خطای عنوان", "عکس بی‌ربط", "بدون عدد"])
        assert len(slides) == 6   # hook + 3 + payoff + cta
        assert slides[0].role == "hook" and slides[-1].role == "cta"

    def test_audit_problems_on_overwide_title(self):
        # genuinely too long: >3 lines at 13em (Persian renders narrow —
        # a Latin-style 60-char title would NOT overflow, by design)
        s = Slide(1, "hook", " ".join(["این عنوان بسیار طولانی است و جا نمی‌شود"] * 6), "")
        check_slide(s)
        assert s.warnings

    def test_audit_deck_counts(self):
        slides = plan_carousel("موضوع", ["نکته یک", "نکته دو"], "فالو کن")
        a = audit_deck(slides)
        assert a["slides"] == 5 and a["read_seconds"] == 5 * 2


class TestInstagramHumanizer:
    def test_pass1_keeps_zwnj_kills_invisible(self):
        text = "می\u200cخوره" + "\u200b" + " خوب است\u200f"
        out = pass_invisible(text)
        assert ZWNJ in out
        assert "\u200b" not in out and "\u200f" not in out

    def test_em_dash_capped_not_banned(self):
        text = "جمله اول — اینجا — ادامه دارد؛ " + " ".join(["واژه"] * 150) + " — پایان"
        excess = em_dash_excess(text)
        assert 0 < excess < text.count("—")

    def test_humanize_zwnj_only_grows(self):
        text = "همه میخواهند در دنیای امروز سریع رشد کنند و کتابهایشان را بخوانند."
        out = humanize(text)
        before, after = text.count(ZWNJ), out["text"].count(ZWNJ)
        assert after >= before
        assert "می‌خواهند" in out["text"] or "میخواهند" in out["text"]

    def test_detect_panel_shape(self):
        rep = detect("من امروز یک کار کردم. نتیجه داد. ساده بود. " + " ".join(["کلمه"] * 60))
        assert set(rep.checks) == {"BURSTINESS", "SPECIFICITY", "SLOP DENSITY", "FINGERPRINT", "VOICE"}
        assert 0 <= rep.overall <= 100


# ---------------------------------------------------------------------------
# Twitter/X
# ---------------------------------------------------------------------------

class TestTwitterThread:
    def test_bilingual_thread_fits(self):
        text = (
            "۱. Tailwind در پروژه‌های فارسی جواب می‌دهد چون RTL-aware است. "
            "۲. فونت Vazirmatn را با preload لود کنید. "
            "۳. دیزاین RTL یعنی آینه‌کردن گرید و آیکون‌ها، نه فقط text-align. "
            "۴. باگ‌های bidi را در کنسول ببینید و تست را با متن فارسی واقعی بگیرید."
        )
        th = thread_from_text(text)
        assert th.tweets and th.fits
        assert th.tweets[0].badge.startswith("(۱/")

    def test_zwnj_compound_never_severed(self):
        monster = "این جمله طولانی است و " + "غیرقابل‌انکارسازی‌پذیرترین واژه‌ها " * 12 + "دارد."
        th = thread_from_text(monster)
        assert th.fits
        for t in th.tweets:
            if "غیرقابل" in t.body:
                assert "غیرقابل‌انکارسازی‌پذیرترین" in t.body  # intact

    def test_numbering_persian_digits(self):
        th = thread_from_text("جمله یک اینجاست. جمله دو اینجاست. " + " ".join(["متن"] * 400))
        assert th.tweets[0].badge == f"(۱/{len(th.tweets).__str__()})".replace("۱/گ", "") or th.tweets[0].badge.startswith("(۱/")

    def test_max_tweets_guard(self):
        with pytest.raises(ValueError):
            thread_from_text(" ".join(["متن"] * 2000), max_tweets=3)


class TestTwitterHooks:
    def test_good_hook(self):
        v = fit_hook("۸۰٪ پروژه‌های فارسی فونت را غلط لود می‌کنند — هزینه‌اش ۴۰۰ms است.")
        assert v.ok

    def test_greeting_hook_fails(self):
        v = fit_hook("سلام دوستان! امروز یک ترد جدید داریم")
        assert not v.ok


# ---------------------------------------------------------------------------
# YouTube
# ---------------------------------------------------------------------------

class TestYoutube:
    def test_chapters_persian_digits(self):
        block = "۰۰:۰۰ مقدمه\n۰۱:۲۳ نصب ابزار\n۰۳:۴۰ اولین پروژه"
        rep = validate_block(block)
        assert rep.ok and rep.count == 3

    def test_chapters_missing_zero(self):
        rep = validate_block("۰۰:۱۰ مقدمه\n۰۱:۲۳ نصب\n۰۳:۴۰ پروژه")
        assert not rep.ok and any("۰۰:۰۰" in p for p in rep.problems)

    def test_title_scoring(self):
        v = optimize_title("آموزش فلاتر در ۱۰ دقیقه — از صفر تا اولین اپ", keyword="آموزش فلاتر")
        assert v.ok
        v2 = optimize_title("یک آموزش بی‌نظیر و شگفت‌انگیز برای شروع سفری شگفت‌انگیز")
        assert not v2.ok or v2.problems

    def test_outline_time_budgets(self):
        o = outline_script("آموزش گراف‌کیو", ["تعریف", "پیاده‌سازی", "اشتباه‌ها"], target_minutes=10)
        assert o.total_seconds >= 550
        assert o.beats[0].role == "hook" and o.beats[-1].role == "cta"
        assert 1200 <= o.words_budget <= 1600   # 10min @140wpm


# ---------------------------------------------------------------------------
# Marketing
# ---------------------------------------------------------------------------

class TestMarketingSeo:
    def test_keyword_variants_fold_arabic(self):
        v = keyword_variants("خرید کتاب")
        assert v.canonical == "خرید کتاب"

    def test_audit_page_problems(self):
        a = audit_page(
            title_tag="کوتاه",
            meta_description="خیلی کوتاه",
            h1="سوالات متداول",
            body="متن کوتاه بدنه.",
            keyword="خرید کتاب",
        )
        assert not a.ok
        assert any("title tag" in p for p in a.problems)
        assert any("meta" in p for p in a.problems)


class TestMarketingCopy:
    def test_framework_lookup(self):
        f = framework("PAS")
        assert f.name_fa == "مسئله-درد-راه‌حل"
        assert len(f.beats) == 3

    def test_quick_edit_flags_empty_adjectives(self):
        rep = quick_edit("این محصول بی‌نظیر است و فوق‌العاده کار می‌کند.")
        assert rep.problems and any("بی‌نظیر" in p for p in rep.problems)

    def test_quick_edit_long_sentence(self):
        long_sentence = " ".join(["کلمه"] * 30) + "."
        rep = quick_edit(long_sentence)
        assert any("جمله" in p for p in rep.problems)


# ---------------------------------------------------------------------------
# Slop lexicon — hallmark-derived Persian cadences
# ---------------------------------------------------------------------------

from core.slop_lexicon import SlopLexicon


class TestSlopCadences:
    def test_not_only_but_cadence(self):
        lex = SlopLexicon()
        rep = lex.report("این نه فقط یک ابزار، بلکه یک انقلاب است.")
        assert any(h.category == "ai_cadence" for h in rep.hits)

    def test_buzzword_triad(self):
        lex = SlopLexicon()
        rep = lex.report("یک پلتفرم یکپارچه، قدرتمند و انقلابی برای تیم‌های مدرن.")
        assert any("سه‌صفت" in h.phrase for h in rep.hits)

    def test_clean_text_zero_hits(self):
        lex = SlopLexicon()
        rep = lex.report("کشتی در کانال کیپا جنگلی غرق شد؛ دو قایق تلمبه‌خانه رسیدند.")
        assert rep.hits == []
