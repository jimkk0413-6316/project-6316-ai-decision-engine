"""Deterministic boundary-reference audit derived from Project 6316 B1.

The purpose of this module is not to generate a trade. It standardises how an
already-readable structural boundary is compared with scan-time Pivot High/Low
and Donchian references.

Core contract:
- visible price structure remains controlling;
- a confirmed, same-event, unconsumed pivot may support the boundary;
- the same-side Donchian edge may support externality / recency;
- missing or disagreeing overlays do not manufacture structure;
- no future confirmation wait is introduced by this audit.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from math import isfinite
from typing import Any

ALIGNMENT_TOLERANCE_ATR = 0.10


class Timeframe(str, Enum):
    M5 = "M5"
    M15 = "M15"


class Direction(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class AlignmentStatus(str, Enum):
    PIVOT_DC_ALIGNED = "PIVOT_DC_ALIGNED"
    PIVOT_ALIGNED = "PIVOT_ALIGNED"
    DC_ALIGNED = "DC_ALIGNED"
    STRUCTURE_ONLY = "STRUCTURE_ONLY"
    DISAGREEMENT = "DISAGREEMENT"
    N_A = "N_A"


@dataclass(frozen=True)
class PivotSettings:
    high_left: int
    high_right: int
    low_left: int
    low_right: int


@dataclass(frozen=True)
class DonchianSettings:
    length: int
    offset: int = 0
    use_upper_lower_only: bool = True
    basis_is_non_scoring: bool = True
    fill_is_non_scoring: bool = True


PIVOT_SETTINGS: dict[Timeframe, PivotSettings] = {
    Timeframe.M5: PivotSettings(2, 2, 2, 2),
    Timeframe.M15: PivotSettings(3, 3, 3, 3),
}

DONCHIAN_SETTINGS: dict[Timeframe, DonchianSettings] = {
    Timeframe.M5: DonchianSettings(length=12),
    Timeframe.M15: DonchianSettings(length=8),
}


@dataclass(frozen=True)
class OverlayObservation:
    """Values visible at scan time. Missing values remain explicit None."""

    timeframe: Timeframe
    pivot_high: float | None = None
    pivot_low: float | None = None
    donchian_upper: float | None = None
    donchian_lower: float | None = None
    pivot_high_confirmed: bool = False
    pivot_low_confirmed: bool = False
    pivot_high_same_event: bool = False
    pivot_low_same_event: bool = False
    pivot_high_consumed: bool = False
    pivot_low_consumed: bool = False
    observed_at: str | None = None


@dataclass(frozen=True)
class BoundaryReferenceAudit:
    timeframe: Timeframe
    direction: Direction
    structural_boundary: float | None
    pivot_reference: float | None
    donchian_reference: float | None
    pivot_distance_atr: float | None
    donchian_distance_atr: float | None
    status: AlignmentStatus
    one_correction_required: bool
    future_wait_required: bool
    hard_veto_created: bool
    candidate_legality_changed: bool
    note: str

    def to_dict(self) -> dict[str, Any]:
        return {k: (v.value if isinstance(v, Enum) else v) for k, v in asdict(self).items()}


def indicator_settings_contract() -> dict[str, Any]:
    """Machine-readable public contract for the boundary-reference overlays."""
    return {
        "M5": {
            "pivot_high_low": asdict(PIVOT_SETTINGS[Timeframe.M5]),
            "donchian": asdict(DONCHIAN_SETTINGS[Timeframe.M5]),
        },
        "M15": {
            "pivot_high_low": asdict(PIVOT_SETTINGS[Timeframe.M15]),
            "donchian": asdict(DONCHIAN_SETTINGS[Timeframe.M15]),
        },
        "future_confirmation_wait": False,
        "spot_or_market_orders_allowed": False,
        "overlay_can_create_hard_veto": False,
        "overlay_can_create_candidate": False,
    }


def audit_boundary_reference(
    *,
    timeframe: Timeframe,
    direction: Direction,
    atr: float,
    structural_boundary: float | None,
    structure_readable: bool,
    observation: OverlayObservation | None,
) -> BoundaryReferenceAudit:
    """Audit overlay agreement without replacing structural interpretation."""

    _require_positive(atr, "ATR")

    if not structure_readable or structural_boundary is None:
        return BoundaryReferenceAudit(
            timeframe=timeframe,
            direction=direction,
            structural_boundary=structural_boundary,
            pivot_reference=None,
            donchian_reference=None,
            pivot_distance_atr=None,
            donchian_distance_atr=None,
            status=AlignmentStatus.N_A,
            one_correction_required=False,
            future_wait_required=False,
            hard_veto_created=False,
            candidate_legality_changed=False,
            note="No readable structural boundary; overlays cannot manufacture one.",
        )

    if observation is None:
        return BoundaryReferenceAudit(
            timeframe=timeframe,
            direction=direction,
            structural_boundary=structural_boundary,
            pivot_reference=None,
            donchian_reference=None,
            pivot_distance_atr=None,
            donchian_distance_atr=None,
            status=AlignmentStatus.STRUCTURE_ONLY,
            one_correction_required=False,
            future_wait_required=False,
            hard_veto_created=False,
            candidate_legality_changed=False,
            note="Overlay values not supplied; proceed from visible structure without waiting.",
        )

    if observation.timeframe is not timeframe:
        raise ValueError("Overlay timeframe does not match audit timeframe")

    if direction is Direction.BUY:
        pivot = (
            observation.pivot_high
            if observation.pivot_high_confirmed
            and observation.pivot_high_same_event
            and not observation.pivot_high_consumed
            else None
        )
        dc = observation.donchian_upper
    else:
        pivot = (
            observation.pivot_low
            if observation.pivot_low_confirmed
            and observation.pivot_low_same_event
            and not observation.pivot_low_consumed
            else None
        )
        dc = observation.donchian_lower

    pivot_distance = _distance_atr(structural_boundary, pivot, atr)
    dc_distance = _distance_atr(structural_boundary, dc, atr)
    pivot_aligned = pivot_distance is not None and pivot_distance <= ALIGNMENT_TOLERANCE_ATR
    dc_aligned = dc_distance is not None and dc_distance <= ALIGNMENT_TOLERANCE_ATR

    if pivot_aligned and dc_aligned:
        status = AlignmentStatus.PIVOT_DC_ALIGNED
        correction = False
        note = "Structure, confirmed same-event Pivot and current Donchian edge align."
    elif pivot_aligned:
        status = AlignmentStatus.PIVOT_ALIGNED
        correction = False
        note = "Confirmed same-event Pivot aligns; Donchian is absent or not aligned."
    elif dc_aligned:
        status = AlignmentStatus.DC_ALIGNED
        correction = False
        note = "Donchian edge aligns; Pivot is absent, stale, consumed or not same-event."
    elif pivot is None and dc is None:
        status = AlignmentStatus.STRUCTURE_ONLY
        correction = False
        note = "No usable overlay reference; proceed from structure without waiting."
    else:
        status = AlignmentStatus.DISAGREEMENT
        correction = True
        note = (
            "Overlay references disagree with the structural boundary. Test one reasonable "
            "same-event correction internally; do not wait for a future reference."
        )

    return BoundaryReferenceAudit(
        timeframe=timeframe,
        direction=direction,
        structural_boundary=structural_boundary,
        pivot_reference=pivot,
        donchian_reference=dc,
        pivot_distance_atr=pivot_distance,
        donchian_distance_atr=dc_distance,
        status=status,
        one_correction_required=correction,
        future_wait_required=False,
        hard_veto_created=False,
        candidate_legality_changed=False,
        note=note,
    )


def _distance_atr(a: float, b: float | None, atr: float) -> float | None:
    if b is None:
        return None
    if not isfinite(b):
        raise ValueError("Overlay price must be finite")
    return abs(a - b) / atr


def _require_positive(value: float, name: str) -> None:
    if not isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be finite and positive")
