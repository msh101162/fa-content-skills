# -*- coding: utf-8 -*-
"""Thread splitting for X — bilingual Persian/Latin, ZWNJ-safe.

The splitter is the one place where Persian thread tooling breaks today:
naive implementations split at 280 *codepoints*, which (a) severs ZWNJ
compounds mid-word and (b) counts CJK-style for nothing. This module
splits on Persian sentence terminals (؟ ! ؛ …) and Latin periods, keeps
ZWNJ compounds intact, numbers tweets with Persian numerals «(۱/۵)», and
guarantees every tweet fits X's weighted limit.

Hook rules for the first tweet (inherited, Persian-adapted):
    - no greeting, no «در این ترد» preamble
    - the promise lands inside the first two lines
    - «ادامه در توییت بعدی» is never spelled out — the (۱/۵) badge does it
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from core.counter import weighted_length
from core.digits import latin_int

from .limits import STANDARD_LIMIT, THREAD_DEFAULT_MAX

# Persian + Latin sentence terminals; newline is always a hard boundary.
_SENTENCE_SPLIT = re.compile(r"(?<=[.!?؟…؛])\s+|\n+")
#: Word-level fallback split that never severs a ZWNJ compound:
#: split on spaces only — ZWNJ never carries a space.
_WORD_SPLIT = re.compile(r"(?<=\s)")


@dataclass
class Tweet:
    index: int                     # 1-based
    body: str                      # WITHOUT the numbering badge
    badge: str                     # «(۱/۵)» or ""
    weighted: int

    @property
    def text(self) -> str:
        return f"{self.body} {self.badge}".strip() if self.badge else self.body

    @property
    def fits(self) -> bool:
        return self.weighted <= STANDARD_LIMIT


@dataclass
class Thread:
    tweets: list[Tweet] = field(default_factory=list)

    @property
    def fits(self) -> bool:
        return all(t.fits for t in self.tweets)

    def render(self) -> str:
        return "\n\n---\n\n".join(t.text for t in self.tweets)


def split_thread(
    text: str,
    limit: int = STANDARD_LIMIT,
    max_tweets: int = THREAD_DEFAULT_MAX,
    number: bool = True,
) -> Thread:
    """Split Persian/Latin text into an X thread under the weighted limit.

    Sentence-first splitting; a single sentence longer than the limit is
    split at word boundaries (ZWNJ compounds are never broken because the
    word split happens on whitespace only).
    """
    text = text.strip()
    if not text:
        return Thread()

    # badge reserve so a finalized «(۱/۵)» never pushes a tweet over
    effective = limit - (8 if number else 0)
    chunks = _split_on_sentences(text)
    pieces: list[str] = []
    for chunk in chunks:
        if weighted_length(chunk) <= effective:
            pieces.append(chunk)
        else:
            pieces.extend(_split_long_sentence(chunk, effective))

    tweets: list[Tweet] = []
    current: list[str] = []
    current_len = 0
    for piece in pieces:
        piece_len = weighted_length(piece) + 1  # joining space
        if current and current_len + piece_len > effective:
            tweets.append(_make_tweet(current, len(tweets) + 1))
            current, current_len = [], 0
        current.append(piece)
        current_len += piece_len
    if current:
        tweets.append(_make_tweet(current, len(tweets) + 1))

    if len(tweets) > max_tweets:
        raise ValueError(
            f"ترد {len(tweets)} توییتی شد (سقف {max_tweets}). "
            "یا متن را کوتاه کن یا max_tweets را بالا ببر — خزانه‌نوشتن ترد نیست."
        )
    return Thread(tweets=tweets)


def _split_on_sentences(text: str) -> list[str]:
    return [s for s in _SENTENCE_SPLIT.split(text) if s and s.strip()]


def _split_long_sentence(sentence: str, limit: int) -> list[str]:
    """Whitespace split — ZWNJ compounds survive by construction."""
    words = sentence.split(" ")
    out: list[str] = []
    buf: list[str] = []
    buf_len = 0
    for w in words:
        w_len = weighted_length(w) + (1 if buf else 0)
        if buf and buf_len + w_len > limit:
            out.append(" ".join(buf))
            buf, buf_len = [w], weighted_length(w)
        else:
            buf.append(w)
            buf_len += w_len
    if buf:
        out.append(" ".join(buf))
    return out


def _make_tweet(pieces: list[str], index: int) -> Tweet:
    """Intermediate tweet — badges finalized later by :func:`finalize_badges`
    once the total count is known."""
    body = " ".join(p.strip() for p in pieces).strip()
    return Tweet(index=index, body=body, badge="", weighted=weighted_length(body))


def finalize_badges(thread: Thread, number: bool = True) -> Thread:
    """Fill the «(۱/۵)» badges once the total count is known, re-verifying limits."""
    n = len(thread.tweets)
    if not number or n == 0:
        for t in thread.tweets:
            t.badge, t.weighted = "", weighted_length(t.body)
        return thread
    for t in thread.tweets:
        t.badge = f"({latin_int(t.index)}/{latin_int(n)})"
        t.weighted = weighted_length(t.text)
    return thread


def thread_from_text(text: str, **kwargs) -> Thread:
    """One-call API: split + finalize badges."""
    number = kwargs.pop("number", True)
    th = split_thread(text, number=number, **kwargs)
    return finalize_badges(th, number=number)


__all__ = ["Tweet", "Thread", "split_thread", "finalize_badges", "thread_from_text"]
