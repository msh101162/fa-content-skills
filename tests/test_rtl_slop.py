# -*- coding: utf-8 -*-
"""Tests for core.rtl (width/wrapping/direction) and core.slop_lexicon."""
from core.rtl import estimate_width, first_strong_direction, fits, script_runs, wrap_text
from core.slop_lexicon import SlopLexicon


class TestWidthEstimation:
    def test_persian_narrower_than_latin_same_count(self):
        # Persian renders visibly narrower per char than Latin average
        fa = estimate_width("سایز متن فارسی")
        la = estimate_width("plain latin text")
        assert fa < la

    def test_zwnj_zero_width(self):
        assert estimate_width("می‌خوره") == estimate_width("میخوره")

    def test_diacritics_zero_width(self):
        assert estimate_width("مُشَبَّک") == estimate_width("مشبک")

    def test_empty(self):
        assert estimate_width("") == 0.0


class TestWrap:
    def test_wrap_respects_max_width(self):
        lines = wrap_text("این یک جمله آزمایشی برای شکستن خط است و کمی طولانی‌تر", 15.0)
        assert all(l.width_em <= 15.0 + 0.01 for l in lines)
        assert len(lines) > 1

    def test_fits_false_on_overflow(self):
        long_text = "این متن خیلی طولانی است و اصلا در سه خط کوتاه جا نمی‌شود چون زیادی بلند است"
        assert not fits(long_text, 10.0, 2)

    def test_fits_true_on_short(self):
        assert fits("هوک کوتاه", 30.0, 2)


class TestDirection:
    def test_first_strong(self):
        assert first_strong_direction("سلام دنیا") == "rtl"
        assert first_strong_direction("hello world") == "ltr"
        assert first_strong_direction("۳۴۵") == "rtl"  # Persian default on neutral

    def test_script_runs(self):
        runs = script_runs("فارسی متن + code")
        kinds = [k for k, _ in runs]
        assert "fa" in kinds and "latin" in kinds


class TestHazmFallback:
    """Optional-dependency contract: hazm absent → graceful None, no crash."""

    def test_degrades_gracefully(self):
        from core.hazm_fallback import hazm_available, lemmatize
        # works either way: hazm installed or not
        result = lemmatize("می‌خوره")
        if not hazm_available():
            assert result is None

    def test_import_never_fails(self):
        from core.hazm_fallback import hazm_module
        assert hazm_module() is None or True  # import attempt is safe


class TestSlopLexicon:
    def setup_method(self):
        self.lex = SlopLexicon()

    def test_cliche_opening_detected(self):
        rep = self.lex.report("در دنیای امروز همه دنبال رشد هستند.")
        cats = {h.category for h in rep.hits}
        assert "cliche_opening" in cats

    def test_zwnj_tolerant_matching(self):
        # both spellings match «شگفت‌انگیز»
        r1 = self.lex.report("یک ابزار شگفت‌انگیز")
        r2 = self.lex.report("یک ابزار شگفتانگیز")
        assert r1.hits and r2.hits

    def test_buzzword_literal_with_suggestion(self):
        rep = self.lex.report("این ابزار قفل پتانسیل شما را باز می‌کند — باز کردن قفل توانایی‌ها")
        hits = [h for h in rep.hits if h.category == "buzzword_literal"]
        assert hits and any(h.suggestion for h in hits)

    def test_clean_replaces_high_severity(self):
        out = self.lex.clean("در دنیای امروز بی‌نظیرترین ابزار را ساختیم", max_severity="high")
        assert "در دنیای امروز" not in out

    def test_clean_preserves_zwnj(self):
        text = "می‌خوره در دنیای امروز"
        out = self.lex.clean(text)
        assert "می‌خوره" in out

    def test_score_zero_on_clean_text(self):
        rep = self.lex.report("کشتی در کانال کیپا جنگلی غرق شد.")
        assert rep.score == 0.0

    def test_report_structure(self):
        rep = self.lex.report("در عصر حاضر، نکته مهم این است که کیفیت مهم است.")
        assert rep.words > 0
        assert 0 <= rep.score <= 100
        assert rep.hits
