"""R2 adaptive entry-buffer calculation for the public Project 6316 portfolio."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

BASE_ATR_FRACTION = 0.10
CEILING_ATR_FRACTION = 0.18
ELEVATED_SPREAD_EXTRA_ATR = 0.05
ELEVATED_SPREAD_MIN_RATIO = 1.80
BLOCK_SPREAD_RATIO = 2.50


@dataclass(frozen=True)
class AdaptiveBufferResult:
    buffer_points: float
    base_buffer_points: float
    buffer_atr: float
    rvol_used: float | None
    spread_ratio: float | None
    spread_extra_points: float
    orders_allowed: bool
    note: str


def calculate_adaptive_buffer(
    *,
    m15_atr: float,
    rvol_m15: float | None,
    spread_ratio: float | None = None,
) -> AdaptiveBufferResult:
    """Calculate the current R2 adaptive buffer and spread adjustment.

    Formula from the R2 specification:
        0.10 * ATR * (1 + RVOL / 2), clamped to [0.10, 0.18] ATR.

    If RVOL is missing, the floor is used and explicitly flagged.
    If a documented spread ratio is 1.8-2.5, +0.05 ATR is added.
    At >=2.5, new pending orders are blocked by the safety layer.
    """

    _positive(m15_atr, "m15_atr")
    if rvol_m15 is not None and (not isfinite(rvol_m15) or rvol_m15 < 0):
        raise ValueError("rvol_m15 must be finite and non-negative when supplied")
    if spread_ratio is not None and (not isfinite(spread_ratio) or spread_ratio < 0):
        raise ValueError("spread_ratio must be finite and non-negative when supplied")

    floor_points = BASE_ATR_FRACTION * m15_atr
    ceiling_points = CEILING_ATR_FRACTION * m15_atr

    if rvol_m15 is None:
        raw = floor_points
        note_parts = ["RVOL N/A - floor buffer applied"]
    else:
        raw = BASE_ATR_FRACTION * m15_atr * (1 + rvol_m15 / 2)
        note_parts = []

    base = min(max(raw, floor_points), ceiling_points)
    extra = 0.0
    allowed = True

    if spread_ratio is None:
        note_parts.append("spread ratio N/A - actual usability must be assessed separately")
    elif spread_ratio >= BLOCK_SPREAD_RATIO:
        allowed = False
        note_parts.append("spread safety block")
    elif spread_ratio >= ELEVATED_SPREAD_MIN_RATIO:
        extra = ELEVATED_SPREAD_EXTRA_ATR * m15_atr
        note_parts.append("elevated spread - extra ATR buffer added")

    total = base + extra
    return AdaptiveBufferResult(
        buffer_points=total,
        base_buffer_points=base,
        buffer_atr=total / m15_atr,
        rvol_used=rvol_m15,
        spread_ratio=spread_ratio,
        spread_extra_points=extra,
        orders_allowed=allowed,
        note="; ".join(note_parts) if note_parts else "adaptive buffer applied",
    )


def _positive(value: float, name: str) -> None:
    if not isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be finite and positive")
