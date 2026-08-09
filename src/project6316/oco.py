"""Small OCO helpers for Project 6316 research simulations."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Side(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


@dataclass(frozen=True)
class Candidate:
    side: Side
    legal: bool
    score: float
    provisional: bool = False


@dataclass(frozen=True)
class BoardSelection:
    mode: str
    selected_sides: tuple[Side, ...]
    reason: str


def choose_board(buy: Candidate | None, sell: Candidate | None) -> BoardSelection:
    """Represent the R2 preference: two-sided OCO when both paths are available.

    This is deliberately a small public abstraction. The private project contains
    the full candidate-construction and ranking process.
    """

    buy_ok = buy is not None and buy.legal
    sell_ok = sell is not None and sell.legal

    if buy_ok and sell_ok:
        return BoardSelection(
            mode="TWO_SIDED_OCO",
            selected_sides=(Side.BUY, Side.SELL),
            reason="Both independently legal paths exist; price is allowed to choose direction.",
        )
    if buy_ok:
        return BoardSelection(
            mode="ONE_SIDED_FALLBACK",
            selected_sides=(Side.BUY,),
            reason="Sell path unavailable after full search.",
        )
    if sell_ok:
        return BoardSelection(
            mode="ONE_SIDED_FALLBACK",
            selected_sides=(Side.SELL,),
            reason="Buy path unavailable after full search.",
        )
    return BoardSelection(mode="NO_BOARD", selected_sides=(), reason="No legal public-demo candidate path.")
