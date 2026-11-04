# -*- coding: utf-8 -*-
"""Carousel slide planner — Persian-native slide budgets.

Spine (from the analyzed slide-architecture reference):

    slide 1: هوک (وعده + لوپ باز، نه یک عنوان خشک)
    slides 2-3: قوی‌ترین ارزش‌ها (فرسایش سوایپ با عمق؛ جلو ببار)
    middle: هر اسلاید «یک» ایده — خواندنی در ~۲ ثانیه
    slide N: پرداخت (خلاصه‌ی سیو-شدنی) + یک درخواست

Persian specificity: text budgets are measured with the RTL width model
(``core.rtl``), because Persian renders 20-35% narrower per character
than Latin — a Latin slide budget would over-constrain Persian slides.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from core.rtl import fits as _fits
from core.rtl import wrap_text

from .limits import CAROUSEL_FRAME, SLIDE_MIN_COUNT, SLIDE_READ_SECONDS, SLIDE_SWEET_SPOT


@dataclass
class Slide:
    index: int            # 1-based
    role: str             # hook | value | payoff | cta
    title_fa: str
    body_fa: str
    warnings: list[str] = field(default_factory=list)

    @property
    def text(self) -> str:
        return f"{self.title_fa}\n{self.body_fa}".strip()


# Slide text budgets (em units at the deck's headline/body sizes).
# 1080×1350 frame with 120px side margins ≈ 840px usable width.
# At 64px headline font that is ~13.1em wide; at 32px body ~26.2em.
HEADLINE_WIDTH_EM = 13.0
HEADLINE_MAX_LINES = 3
BODY_WIDTH_EM = 26.0
BODY_MAX_LINES = 8


def check_slide(slide: Slide) -> Slide:
    """Attach width-budget warnings using the RTL width model."""
    slide.warnings = []
    if not _fits(slide.title_fa, HEADLINE_WIDTH_EM, HEADLINE_MAX_LINES):
        lines = len(wrap_text(slide.title_fa, HEADLINE_WIDTH_EM))
        slide.warnings.append(
            f"عنوان در {HEADLINE_MAX_LINES} خطِ {HEADLINE_WIDTH_EM}em جا نمی‌شود (اکنون ~{lines} خط) — کوتاهش کن."
        )
    if not _fits(slide.body_fa, BODY_WIDTH_EM, BODY_MAX_LINES):
        lines = len(wrap_text(slide.body_fa, BODY_WIDTH_EM))
        slide.warnings.append(
            f"بدنه در {BODY_MAX_LINES} خط جا نمی‌شود (~{lines} خط) — یا متن را ببر یا اسلاید را دو ایده‌ی مستقل کن."
        )
    return slide


def plan_carousel(
    topic: str,
    points: list[str],
    cta_fa: str = "برای همین‌ها فالو کن",
) -> list[Slide]:
    """Build the universal spine from a topic + user-provided points.

    Never pads: a 5-point idea becomes a 7-slide carousel
    (hook + 5 value slides + payoff), not 10. Raises ValueError when
    fewer than {SLIDE_MIN_COUNT} real points arrive — padding is the tell.
    """
    points = [p for p in points if p and p.strip()]
    if len(points) < 1:
        raise ValueError("حداقل یک نکته‌ی واقعی لازم است؛ اسلاید پُرکنی نکن.")

    hook = Slide(1, "hook", topic, "لوپ باز بماند؛ وعده بده، عنوان خشک نده.")
    slides = [hook]
    strong = points[:2]
    rest = points[2:]
    for i, p in enumerate(strong, start=2):
        slides.append(Slide(i, "value", p[:80], "قوی‌ترین نکته‌ها اول — سوایپ با عمق می‌پوسد."))
    idx = len(slides) + 1
    for p in rest:
        slides.append(Slide(idx, "value", p[:80], ""))
        idx += 1
    payoff = Slide(idx, "payoff", "خلاصه‌ی سیو-شدنی", "؛ ".join(p[:40] for p in points[:3]))
    idx += 1
    slides.append(payoff)
    slides.append(Slide(idx, "cta", cta_fa, ""))
    for i, s in enumerate(slides, 1):
        s.index = i
    return slides


def audit_deck(slides: list[Slide]) -> dict[str, object]:
    """Spine audit: one-idea-per-slide, count in sweet spot, budget fits."""
    problems: list[str] = []
    if len(slides) < SLIDE_MIN_COUNT:
        problems.append(f"کمتر از {SLIDE_MIN_COUNT} اسلاید بی‌معناست.")
    lo, hi = SLIDE_SWEET_SPOT
    if not (lo <= len(slides) <= hi + 2):
        problems.append(f"{len(slides)} اسلاید — نقطه‌ی شیرین {lo}–{hi} است؛ پُرکنی را ببر.")
    hook = slides[0]
    if hook.role != "hook":
        problems.append("اسلاید اول هوک است، نه عنوان.")
    cta_slides = [s for s in slides if s.role == "cta"]
    if len(cta_slides) != 1:
        problems.append("دقیقاً یک اسلاید CTA لازم است؛ دو درخواست یعنی هیچ.")
    for s in slides:
        check_slide(s)
        problems.extend(s.warnings)
    return {"slides": len(slides), "problems": problems, "read_seconds": len(slides) * SLIDE_READ_SECONDS}


__all__ = ["Slide", "plan_carousel", "check_slide", "audit_deck"]
