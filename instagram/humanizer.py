# -*- coding: utf-8 -*-
"""Persian humanizer — four passes + detection panel.

Adapted from the analyzed humanizer (`humanize.py` + `detect.py` +
`slop.json`), re-engineered for Persian on the core engine:

Pass 1  نویسه‌های نامرئی — invisible/control chars removed EXCEPT ZWNJ,
        which is Persian orthography, never noise.
Pass 2  تایپوگرافی — em-dash capped, not banned (1 per ~100 words);
        replacement order: ویرگول → دونقطه → پرانتز → خط جدید → بازنویسی،
        هرگز نقطه (نقطه‌کردنِ خط‌تیره از هم می‌پاشد).
Pass 3  واژگانی — core.slop_lexicon replace (idiomatic Persian, never
        literal-translation of English AI buzzwords).
Pass 4  ساختاری — flagged, NOT auto-rewritten (judgement is the model's
        job): triads at density, «نه فقط X، بلکه Y» cadence, rhetorical
        question lines, staccato bursts, uniform sentence length
        (coefficient of variation < 0.35).

Detection panel: BURSTINESS / SPECIFICITY / SLOP DENSITY / FINGERPRINT /
VOICE with anchors, weakest check weighted 40%:
    overall = mean * 0.6 + min * 0.4
PASS = overall ≥ 70 AND no check < 55.

Honest scope (inherited): this is not a detector-defeat promise.
«غیرقابل‌تشخیص شدن» هدف نیست؛ نوشتنِ انسانیِ خوب هدف است.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from core.chars import BIDI_CTRL, ZWNJ, ZWJ
from core.counter import count as count_words
from core.slop_lexicon import SlopLexicon

from .limits import PERSIAN_SPOKEN_WPM

# ---------------------------------------------------------------------------
# Pass 1 — invisible characters (ZWNJ/ZWJ are NEVER removed)
# ---------------------------------------------------------------------------

#: Control/invisible classes removed by pass 1. NOTE: ZWNJ (U+200C) and
#: ZWJ (U+200D) live in category Cf too but are Persian-essential and are
#: explicitly protected.
_INVISIBLE_RE = re.compile(
    "[\u00ad\u180e\u200b\u200e\u200f\u202a-\u202e\u2060-\u2064\u206a-\u206f"
    "\ufeff\ufff9-\ufffb]"
)

#: Bidi controls other than ZWNJ/ZWJ — RLM/LRM kept only if user passes
#: keep_bidi=True (rare); default removes them since they scramble platforms.
_BIDI_RE = re.compile("[" + re.escape("".join(set(BIDI_CTRL) - {ZWNJ, ZWJ})) + "]")


def pass_invisible(text: str, keep_bidi: bool = False) -> str:
    out = _INVISIBLE_RE.sub("", text)
    if not keep_bidi:
        out = _BIDI_RE.sub("", out)
    return out


# ---------------------------------------------------------------------------
# Pass 2 — typography: em-dash cap, not ban
# ---------------------------------------------------------------------------

_EM_DASH = "—"
_DASH_REPLACEMENTS = (r"،", r"؛ یعنی ", r" (", r"\n")


def em_dash_excess(text: str) -> int:
    """Dashes above the 1-per-100-words cap."""
    words = max(count_words(text).words, 1)
    allowed = max(1, words // 100)
    return max(0, text.count(_EM_DASH) - allowed)


def pass_typography(text: str) -> str:
    """Repair punctuation beyond the em-dash cap (never with a period)."""
    excess = em_dash_excess(text)
    if not excess:
        return text
    # replace the LAST excess dashes first (they read like afterthoughts)
    positions = [m.start() for m in re.finditer(re.escape(_EM_DASH), text)]
    for pos in sorted(positions, reverse=True)[:excess]:
        repl = _DASH_REPLACEMENTS[len(positions) % len(_DASH_REPLACEMENTS)]
        text = text[:pos] + repl + text[pos + 1:]
    # orphan punctuation repair: «، ،» «،.» «..»
    text = re.sub(r"\s*،\s*،", "،", text)
    text = re.sub(r"\s*،\s*\.", ".", text)
    text = re.sub(r"\.{2,}", "…", text)
    return text


# ---------------------------------------------------------------------------
# Pass 3 — lexical (delegates to the Persian slop lexicon)
# ---------------------------------------------------------------------------

def pass_lexical(text: str, lexicon: SlopLexicon | None = None) -> str:
    lex = lexicon or SlopLexicon()
    return lex.clean(text, max_severity="medium")


# ---------------------------------------------------------------------------
# Pass 4 — structural tells (FLAGGED, never auto-rewritten)
# ---------------------------------------------------------------------------

_NOT_JUST_RE = re.compile(r"نه\s+فقط\s+.+،\s*بلکه")
_RHETORICAL_Q_RE = re.compile(rf"^\s*(آیا\s+می[\s\u200c]*دانی|می[\s\u200c]*دانی\s+که|آیا\s+تا\s+به\s+حال)")
_STACCATO_RE = re.compile(r"(?:[^.!؟?\n]{2,30}[.!؟?]\s*){4,}$")
_TRIAD_RE = re.compile(r"[\w\u200c]+،\s*[\w\u200c]+(?:،)?\s*و\s*[\w\u200c]+")


@dataclass
class StructuralFlag:
    tell: str
    span: tuple[int, int]
    fix_fa: str          # directive for the model/user — judgement, not regex


def pass_structural(text: str) -> list[StructuralFlag]:
    flags: list[StructuralFlag] = []
    for m in _NOT_JUST_RE.finditer(text):
        flags.append(StructuralFlag("نه-فقط/بلکه", (m.start(), m.end()),
                     "این قالب ریتمیک AI است؛ یکی از دو نیمه را حذف کن یا رابطه را با جمله‌ی واقعی بگو."))
    for m in _RHETORICAL_Q_RE.finditer(text):
        flags.append(StructuralFlag("سوال بلاغی آغازین", (m.start(), m.end()),
                     "با یک واقعیت مشخص شروع کن، نه با «می‌دانی که…»."))
    stats = count_words(text)
    if stats.words >= 40:
        cv = _sentence_length_cv(text)
        if cv < 0.35:
            flags.append(StructuralFlag("طول جمله یکنواخت", (0, len(text)),
                         "طول جمله‌ها یکنواخت است؛ یکی را بلند کن و یکی را بی‌رحم کوتاه."))
        n_triads = len(_TRIAD_RE.findall(text))
        if n_triads >= 2:
            flags.append(StructuralFlag("سه‌تایی انباشته", (0, len(text)),
                         f"{n_triads} سه‌تایی؛ یکی طبیعی می‌ماند، بقیه را دو موردی کن."))
    return flags


def _sentence_length_cv(text: str) -> float:
    """Coefficient of variation of sentence lengths (in words).

    Humans land ~0.70; machine-clone text drifts below ~0.35.
    """
    sents = [s for s in re.split(r"(?<=[.!?؟…])\s+", text) if s.strip()]
    lens = [len(s.split()) for s in sents]
    if len(lens) < 3:
        return 1.0
    mean = sum(lens) / len(lens)
    if mean == 0:
        return 1.0
    var = sum((n - mean) ** 2 for n in lens) / len(lens)
    return round((var ** 0.5) / mean, 3)


# ---------------------------------------------------------------------------
# Detection panel
# ---------------------------------------------------------------------------

@dataclass
class HumanizeReport:
    checks: dict[str, float] = field(default_factory=dict)
    overall: float = 0.0
    verdict: str = "REVIEW"          # PASS | REVIEW | FAIL
    flags: list[StructuralFlag] = field(default_factory=list)
    delta_zwnj: int = 0

    @property
    def weakest(self) -> str | None:
        return min(self.checks, key=self.checks.get) if self.checks else None


def detect(text: str, lexicon: SlopLexicon | None = None) -> HumanizeReport:
    """Five-check panel, weakest weighted 40%. PASS ≥70 overall, none <55."""
    lex = lexicon or SlopLexicon()
    stats = count_words(text)
    rep = lex.report(text)

    # SLOP DENSITY — anchored: clean ≈ 0 hits, soup ≥ 5/100w
    density = rep.density
    slop_score = max(0.0, 100.0 - density * 30.0)

    # BURSTINESS — anchored on measured Persian caps (human ~0.70 / machine ~0.22)
    cv = _sentence_length_cv(text)
    burst = _scale(cv, human=0.70, machine=0.22)

    # SPECIFICITY — numbers/names per 100 words
    import re as _re
    concrete = len(_re.findall(r"[\d\u06f0-\u06f9]|«[^»]+»", text))
    per100 = concrete * 100 / max(stats.words, 1)
    spec = min(100.0, 40.0 + per100 * 25.0)

    # FINGERPRINT — remaining AI tells (flags + broken unicode)
    fingerprint = 100.0 - min(100.0, len(rep.hits) * 8.0)

    # VOICE — you-forms + first-person presence (Persian-safe boundaries,
    # NOT \b: ZWNJ compounds would false-match otherwise)
    from core.regex_patterns import whole_word
    you = sum(len(whole_word(w).findall(text)) for w in ("تو", "شما", "خودت"))
    first = sum(len(whole_word(w).findall(text)) for w in ("من", "ما"))
    voice = min(100.0, 45.0 + (you + first) * 12.0)

    checks = {
        "BURSTINESS": round(burst, 1),
        "SPECIFICITY": round(spec, 1),
        "SLOP DENSITY": round(slop_score, 1),
        "FINGERPRINT": round(fingerprint, 1),
        "VOICE": round(voice, 1),
    }
    mean = sum(checks.values()) / len(checks)
    overall = mean * 0.6 + min(checks.values()) * 0.4
    verdict = "PASS" if overall >= 70 and min(checks.values()) >= 55 else ("FAIL" if overall < 45 else "REVIEW")
    return HumanizeReport(checks=checks, overall=round(overall, 1), verdict=verdict,
                          flags=pass_structural(text), delta_zwnj=text.count(ZWNJ))


def _scale(value: float, human: float, machine: float) -> float:
    """Map a raw metric onto 0-100 with human/machine anchors."""
    lo, hi = machine, human
    t = (value - lo) / (hi - lo) if hi != lo else 0.5
    return max(0.0, min(100.0, t * 100.0))


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

def humanize(text: str, aggressive: bool = False) -> dict[str, object]:
    """Run passes 1-3 automatically; pass 4 only flags.

    Returns the cleaned text, before/after ZWNJ counts, structural flags
    and the detection panel. ZWNJ count can only grow (pass 3 may insert
    compounds) — never shrink.
    """
    before = text.count(ZWNJ)
    out = pass_invisible(text)
    out = pass_typography(out)
    out = pass_lexical(out)
    # typo-level ZWNJ repair is legitimate humanizing, not slop removal
    from core.normalizer import zwnj_fix
    out = zwnj_fix(out)
    after = out.count(ZWNJ)
    panel = detect(out)
    panel.delta_zwnj = after - before
    return {
        "text": out,
        "panel": panel,
        "flags": panel.flags,
        "aggressive_note": "پاس ۴ بازنویسی نمی‌کند؛ بازنویسی ساختاری کار مدل/انسان است." if not aggressive else None,
    }


__all__ = [
    "pass_invisible",
    "pass_typography",
    "pass_lexical",
    "pass_structural",
    "StructuralFlag",
    "HumanizeReport",
    "detect",
    "humanize",
    "em_dash_excess",
    "PERSIAN_SPOKEN_WPM",
]
