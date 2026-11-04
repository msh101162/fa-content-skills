# -*- coding: utf-8 -*-
"""fa-content-skills core: Persian-native NLP engine for content work.

Modules
-------
``chars``           character classes, digit maps, script helpers
``regex_patterns``  Persian-safe regex (no ``\\b``), hashtags, numbers
``digits``          Persian ۰-۹ ↔ Latin digit conversion
``normalizer``      ZWNJ-safe normalization pipeline
``counter``         bilingual token/word statistics
``rtl``             width estimation, wrapping, direction runs
``slop_lexicon``    Persian AI-slop detection + idiomatic repair

Zero external dependencies. Optional: ``pillow`` for real RTL shaping
measurement (``core.rtl.measure_pillow``), ``hazm`` for optional
lemmatization fallbacks in downstream tools.
"""

from .chars import ZWNJ, PERSIAN_LETTERS
from .regex_patterns import WORD_RE, CONCRETE_RE, HASHTAG_RE, tokenize, whole_word
from .normalizer import NormalizeOptions, normalize, zwnj_fix, zwnj_count
from .counter import TextStats, count, weighted_length
from .rtl import estimate_width, wrap_text, fits, first_strong_direction
from .slop_lexicon import SlopLexicon, SlopReport

__version__ = "0.1.0"

__all__ = [
    "ZWNJ",
    "PERSIAN_LETTERS",
    "WORD_RE",
    "CONCRETE_RE",
    "HASHTAG_RE",
    "tokenize",
    "whole_word",
    "NormalizeOptions",
    "normalize",
    "zwnj_fix",
    "zwnj_count",
    "TextStats",
    "count",
    "weighted_length",
    "estimate_width",
    "wrap_text",
    "fits",
    "first_strong_direction",
    "SlopLexicon",
    "SlopReport",
    "__version__",
]
