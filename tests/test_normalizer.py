# -*- coding: utf-8 -*-
"""Tests for core.normalizer — the ZWNJ-integrity invariant + repair rules."""
from core.chars import ZWNJ
from core.normalizer import NormalizeOptions, normalize, zwnj_count, zwnj_fix

MID = ZWNJ


class TestZwnjInvariant:
    def test_never_removes_zwnj(self):
        text = "من می‌خوره نمی‌دانم نرم‌افزارها را می‌بینم."
        out = normalize(text)
        assert zwnj_count(out) >= zwnj_count(text)
        # every original ZWNJ position (inside words) is preserved in output
        assert "می" + MID + "خوره" in out
        assert "نمی" + MID + "دانم" in out
        assert "نرم" + MID + "افزار" in out

    def test_nfkc_does_not_touch_zwnj(self):
        import unicodedata
        s = "می‌خوره"
        assert unicodedata.normalize("NFKC", s) == s

    def test_fix_zwnj_only_increases_count(self):
        text = "میخوره کتابها بزرگترین نرم‌افزار"
        out = normalize(text)
        assert zwnj_count(out) >= zwnj_count(text)
        assert "می" + MID + "خوره" in out
        assert "کتاب" + MID + "ها" in out
        assert "بزرگ" + MID + "ترین" in out


class TestZwnjFixer:
    def test_mi_prefix_repairs_common_verb(self):
        assert zwnj_fix("میخوره") == "می" + MID + "خوره"
        assert zwnj_fix("میخواهم") == "می" + MID + "خواهم"
        assert zwnj_fix("نمیدانم") == "نمی" + MID + "دانم"
        assert zwnj_fix("نمیرود") == "نمی" + MID + "رود"

    def test_mi_whitelist_protects_real_words(self):
        # میان / میوه / میکروب must never be split
        assert zwnj_fix("میان") == "میان"
        assert zwnj_fix("میوه") == "میوه"
        assert zwnj_fix("میکروب") == "میکروب"
        assert zwnj_fix("میهن") == "میهن"

    def test_mi_unknown_stem_untouched(self):
        # unknown stem → no auto-fix (never break correct words)
        assert zwnj_fix("می‌زرقلی") == "می" + MID + "زرقلی"
        assert zwnj_fix("میزرقلی") == "میزرقلی"

    def test_plural_suffix(self):
        assert zwnj_fix("کتابها") == "کتاب" + MID + "ها"
        assert zwnj_fix("کتابهای") == "کتاب" + MID + "های"
        assert zwnj_fix("کتابهایی") == "کتاب" + MID + "هایی"

    def test_plural_exceptions_untouched(self):
        assert zwnj_fix("خانه") == "خانه"
        assert zwnj_fix("راهها") == "راهها"  # «راه» in exceptions → no fix

    def test_comparative(self):
        assert zwnj_fix("بزرگتر") == "بزرگ" + MID + "تر"
        assert zwnj_fix("بزرگترین") == "بزرگ" + MID + "ترین"

    def test_comparative_exception(self):
        assert zwnj_fix("متر") == "متر"  # «متر» is a word, not comparative

    def test_bi_compounds_list_driven(self):
        assert zwnj_fix("بیکار") == "بی" + MID + "کار"
        assert zwnj_fix("بیدار") == "بیدار"    # real word — protected
        assert zwnj_fix("بیمار") == "بیمار"    # real word — protected

    def test_existing_zwnj_untouched(self):
        assert zwnj_fix("می" + MID + "خوره") == "می" + MID + "خوره"


class TestNormalizePipeline:
    def test_arabic_letters_fold(self):
        assert normalize("كتاب يخ") == "کتاب یخ"

    def test_digits_unified_to_fa(self):
        assert normalize("سال 2024 مهم بود") == "سال ۲۰۲۴ مهم بود"

    def test_digits_kept_when_none(self):
        opts = NormalizeOptions(unify_digits=None)
        assert normalize("2024", opts) == "2024"

    def test_spacing_cleanup(self):
        out = normalize("سلام    دنیا  !")
        assert out == "سلام دنیا!"

    def test_ellipsis(self):
        assert normalize("چه اتفاقی...") == "چه اتفاقی…"

    def test_full_pipeline_keeps_compounds(self):
        text = "در دنیای امروز،  نرم‌افزارهای جدید 2024 را می‌بینید؟"
        out = normalize(text)
        assert "نرم‌افزارهای" in out
        assert "می‌بینید" in out
        assert "۲۰۲۴" in out

    def test_empty_string(self):
        assert normalize("") == ""
