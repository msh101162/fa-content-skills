# -*- coding: utf-8 -*-
"""Tests for core.regex_patterns — Persian word boundaries, digits, hashtags."""
import pytest

from core.regex_patterns import (
    CONCRETE_RE,
    HASHTAG_RE,
    WORD_RE,
    broken_hashtags,
    hashtags,
    tokenize,
    whole_word,
)


class TestWordBoundary:
    """Python's \\b fails on Persian because ZWNJ is not a \\w char —
    our lookaround class must not reproduce that failure."""

    def test_word_re_compound_is_single_token(self):
        tokens = WORD_RE.findall("می‌خوره")
        assert tokens == ["می‌خوره"]

    def test_whole_word_blocks_prefix_mi(self):
        assert whole_word("می").findall("می‌خوره") == []

    def test_whole_word_blocks_compound_part(self):
        assert whole_word("خوره").findall("می‌خوره") == []

    def test_whole_word_finds_standalone(self):
        assert whole_word("کتاب").findall("این کتاب خوب است") == ["کتاب"]

    def test_whole_word_blocks_inside_suffix_compound(self):
        # «کتاب‌ها» is one word — searching «کتاب» must not match there
        assert whole_word("کتاب").findall("کتاب‌ها") == []

    def test_whole_word_matches_plain_suffix_run(self):
        # without ZWNJ, کتابها tokenizes as one word too — no false match
        assert whole_word("کتاب").findall("کتابها") == []

    def test_tokenize_mixed_scripts(self):
        tokens = tokenize("با pip پکیج requirements.txt را نصب کن")
        assert tokens == ["با", "pip", "پکیج", "requirements", "txt", "را", "نصب", "کن"]

    def test_tokenize_numbers_attached(self):
        assert tokenize("پایتون۳ و ۶۰۰۰ کاربر") == ["پایتون۳", "و", "۶۰۰۰", "کاربر"]

    def test_word_re_includes_persian_specific_letters(self):
        for word in ["پژوهش", "گچ", "کابوس", "یخ"]:
            assert WORD_RE.fullmatch(word), word

    def test_diacritics_inside_words(self):
        assert len(WORD_RE.findall("مُشَبَّک")) == 1


class TestConcreteNumbers:
    @pytest.mark.parametrize("num", ["۶۰۰۰", "6000", "۶٬۰۰۰", "۶,۰۰۰", "6,000", "٠٥٠"])
    def test_all_digit_systems_and_separators(self, num):
        assert CONCRETE_RE.fullmatch(num)

    def test_decimal_both_styles(self):
        assert CONCRETE_RE.fullmatch("۱٫۵")
        assert CONCRETE_RE.fullmatch("3.14")

    def test_no_gluing_of_lists(self):
        # «۵، ۷» (list) must NOT be one number
        m = CONCRETE_RE.findall("۵، ۷ و ۹")
        assert m == ["۵", "۷", "۹"]

    def test_thousands_grouping_repeated(self):
        assert CONCRETE_RE.fullmatch("۱۲٬۳۴۵٬۶۷۸")


class TestHashtags:
    def test_persian_hashtag_with_underscore(self):
        assert hashtags("حالا #گیت_هاب را ببین") == ["#گیت_هاب"]

    def test_persian_hashtag_with_number(self):
        assert hashtags("#پایتون۳") == ["#پایتون۳"]

    def test_latin_hashtag(self):
        assert hashtags("follow #python3 now") == ["#python3"]

    def test_zwnj_hashtag_is_broken(self):
        # platforms break ZWNJ hashtags — must be detected as a bug
        assert hashtags("#می‌خوره") == []
        assert broken_hashtags("#می‌خوره") != []

    def test_pure_numeric_hashtag_rejected(self):
        assert hashtags("#۱۲۳") == []
