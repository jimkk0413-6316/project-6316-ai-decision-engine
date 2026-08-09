"""Selected R2 safety guardrails represented as pure research functions.

These functions separate account/execution safety from structural trade legality.
They are intentionally broker-agnostic and do not place orders.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import isfinite

COMPLETE_CLUSTER_MAX_RISK_ATR = 1.50
PROVISIONAL_MAX_RISK_ATR = 1.80
DAILY_LOSS_CIRCUIT_EQUITY = 0.015
MANUAL_OCO_COMBINED_RISK_EQUITY = 0.005
MICRO_DEFAULT_EXPIRY_MIN = 8
MICRO_LOW_ATR_EXPIRY_MIN = 12
MICRO_LOW_ATR_THRESHOLD = 3.0
PSY_NEAR_ATR = 0.15
PSY_SCORE_MULTIPLIER = 0.95


class SetupType(str, Enum):
    COMPLETE = "COMPLETE"
    PROVISIONAL = "PROVISIONAL"


@dataclass(frozen=True)
class RiskCeilingResult:
    allowed: bool
    ceiling_atr: float
    elevated_risk_flag: bool


def risk_ceiling(*, risk_atr: float, setup_type: SetupType) -> RiskCeilingResult:
    _non_negative(risk_atr, "risk_atr")
    ceiling = (
        PROVISIONAL_MAX_RISK_ATR
        if setup_type is SetupType.PROVISIONAL
        else COMPLETE_CLUSTER_MAX_RISK_ATR
    )
    return RiskCeilingResult(
        allowed=risk_atr <= ceiling,
        ceiling_atr=ceiling,
        elevated_risk_flag=(
            setup_type is SetupType.PROVISIONAL
            and COMPLETE_CLUSTER_MAX_RISK_ATR < risk_atr <= PROVISIONAL_MAX_RISK_ATR
        ),
    )


def provisional_direction_blocked(consecutive_same_direction_provisional_sls: int) -> bool:
    if consecutive_same_direction_provisional_sls < 0:
        raise ValueError("SL count cannot be negative")
    return consecutive_same_direction_provisional_sls >= 2


def daily_loss_circuit_hit(*, equity: float, realised_plus_floating_loss: float) -> bool:
    """Loss is passed as a positive money amount."""
    _positive(equity, "equity")
    _non_negative(realised_plus_floating_loss, "realised_plus_floating_loss")
    return realised_plus_floating_loss >= DAILY_LOSS_CIRCUIT_EQUITY * equity


def manual_oco_combined_risk_allowed(*, equity: float, buy_risk: float, sell_risk: float) -> bool:
    _positive(equity, "equity")
    _non_negative(buy_risk, "buy_risk")
    _non_negative(sell_risk, "sell_risk")
    return (buy_risk + sell_risk) <= MANUAL_OCO_COMBINED_RISK_EQUITY * equity


def micro_expiry_minutes(*, m5_atr: float) -> int:
    _positive(m5_atr, "m5_atr")
    return MICRO_LOW_ATR_EXPIRY_MIN if m5_atr < MICRO_LOW_ATR_THRESHOLD else MICRO_DEFAULT_EXPIRY_MIN


def nearest_psychological_level(price: float) -> float:
    """Return nearest XX00 / XX50 level for a price quoted in ordinary decimal points."""
    if not isfinite(price):
        raise ValueError("price must be finite")
    base = round(price / 50.0) * 50.0
    return float(base)


def psychological_level_adjustment(*, entry: float, m15_atr: float, score: float) -> tuple[bool, float, float]:
    """Return (near_psy_level, adjusted_score, nearest_level)."""
    _positive(m15_atr, "m15_atr")
    if not isfinite(entry) or not isfinite(score):
        raise ValueError("entry and score must be finite")
    level = nearest_psychological_level(entry)
    near = abs(entry - level) < PSY_NEAR_ATR * m15_atr
    return near, score * PSY_SCORE_MULTIPLIER if near else score, level


def _positive(value: float, name: str) -> None:
    if not isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be finite and positive")


def _non_negative(value: float, name: str) -> None:
    if not isfinite(value) or value < 0:
        raise ValueError(f"{name} must be finite and non-negative")
