# -*- coding: utf-8 -*-
"""Optional hazm integration — deep token analysis when hazm is installed.

Policy: hazm is a *fallback analyzer*, never a text rewriter. Our own
normalizer owns Persian orthography (and is test-enforced on the ZWNJ
invariant); hazm only supplies lemmas/POS for downstream heuristics
(e.g. the mi-prefix verb-stem check). If hazm is absent, every function
here degrades to a no-op None and callers proceed with the stdlib path.

    pip install fa-content-skills[nlp]   # or: pip install hazm
"""

from __future__ import annotations

from typing import Any

_HAZM: Any = None
_HAZM_TRIED = False


def hazm_module() -> Any:
    """Import hazm once, cache it, return None when unavailable."""
    global _HAZM, _HAZM_TRIED
    if not _HAZM_TRIED:
        _HAZM_TRIED = True
        try:
            import hazm  # type: ignore[import-untyped]
            _HAZM = hazm
        except ImportError:
            _HAZM = None
    return _HAZM


def hazm_available() -> bool:
    return hazm_module() is not None


def lemmatize(token: str) -> str | None:
    """Lemmatize one Persian token via hazm; None when hazm is absent.

    Callers must treat None as «no opinion» and fall back to their own
    heuristics — never as «not a word».
    """
    h = hazm_module()
    if h is None:
        return None
    try:
        return h.Lemmatizer().lemmatize(token)
    except Exception:
        return None


def is_verb_stem_pair(token: str) -> bool:
    """True if hazm says this token carries a verb lemma (می‌/نمی- prefixed).

    Used by tools that want *deeper* precision than the curated
    ``MI_VERB_STEMS`` list in ``core.normalizer`` — an optional upgrade,
    not a dependency.
    """
    h = hazm_module()
    if h is None:
        return False
    try:
        lemma = h.Lemmatizer().lemmatize(token)
    except Exception:
        return False
    if not lemma:
        return False
    # hazm returns lemma pairs like «خورد#خوردن» for verbs
    return "#" in lemma or " " not in lemma and lemma != token


__all__ = ["hazm_module", "hazm_available", "lemmatize", "is_verb_stem_pair"]
