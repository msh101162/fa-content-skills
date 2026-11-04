# -*- coding: utf-8 -*-
"""Tests for core.counter (bilingual) and core.digits."""
from core.chars import ZWNJ
from core.counter import count, weighted_length
from core.digits import (
    latin_int,
    strip_thousands_separators,
    to_latin_digits,
    to_persian_digits,
)


class TestBilingualCounter:
    def test_mixed_script_counts(self):
        s = "با pip دو پکیج requirements را نصب کردم"
        st = count(s)
        assert st.persian_words == 6   # با، دو، پکیج، را، نصب، کردم
        assert st.latin_words == 2

    def test_zwnj_compound_is_one_word(self):
        st = count("نرم‌افزار خوب")
        assert st.words == 2
        st2 = count("نرمافزار خوب")
        assert st2.words == 2

    def test_zwnj_counted(self):
        st = count("می‌خوره" + " " + "کتاب‌ها")
        assert st.zwnj_count == 2

    def test_persian_digits_are_numeric_tokens(self):
        st = count("۶۰۰۰ کاربر و 2500 فایل")
        assert st.numeric_tokens == 2

    def test_reading_time_reasonable(self):
        st = count(" ".join(["کلمه"] * 400))
        assert 100 <= st.reading_seconds <= 140  # 400 words @200wpm = 120s

    def test_empty(self):
        st = count("")
        assert st.words == 0

    def test_sentences_persian_terminal(self):
        st = count("سلام! خوبی؟ خوبم.")
        assert st.sentences == 3


class TestWeightedLength:
    def test_zwnj_weighs_zero(self):
        assert weighted_length("می‌خوره") == weighted_length("میخوره") == 6

    def test_persian_weighs_one(self):
        # X counts Persian as 1 per char since 2018
        assert weighted_length("سلام") == 4

    def test_cjk_weighs_two(self):
        assert weighted_length("中文") == 4


class TestDigits:
    def test_fa_to_latin(self):
        assert to_latin_digits("۶,۰۰۰ و ۲۰۲۴") == "6,000 و 2024"

    def test_to_persian_digits(self):
        assert to_persian_digits("2024 سال خوبی است") == "۲۰۲۴ سال خوبی است"

    def test_to_persian_digits_protects_latin_tokens(self):
        out = to_persian_digits("requirements.txt v2 را در pip3 نصب کن ۱۲")
        assert "requirements.txt" in out
        assert "v2" in out          # latin token with digit — protected
        assert "pip3" in out
        assert "۱۲" in out

    def test_thousands_strip_keeps_word_commas(self):
        assert strip_thousands_separators("۶٬۰۰۰ تومان") == "۶۰۰۰ تومان"
        assert strip_thousands_separators("6,000 items") == "6000 items"
        # comma between words must survive (Persian comma or Latin in Latin run)
        assert strip_thousands_separators("شیر، نان") == "شیر، نان"

    def test_latin_int_formatting(self):
        assert latin_int(6000) == "۶٬۰۰۰"
        assert latin_int(1250000) == "۱٬۲۵۰٬۰۰۰"
