"""Synthetic example only - no broker or market connection."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from project6316.adaptive_buffer import calculate_adaptive_buffer
from project6316.boundary_reference import Direction, OverlayObservation, Timeframe, audit_boundary_reference
from project6316.oco import Candidate, Side, choose_board


def main() -> None:
    observation = OverlayObservation(
        timeframe=Timeframe.M5,
        pivot_high=2400.20,
        donchian_upper=2400.30,
        pivot_high_confirmed=True,
        pivot_high_same_event=True,
        observed_at="synthetic-demo",
    )

    audit = audit_boundary_reference(
        timeframe=Timeframe.M5,
        direction=Direction.BUY,
        atr=5.0,
        structural_boundary=2400.0,
        structure_readable=True,
        observation=observation,
    )

    buffer = calculate_adaptive_buffer(m15_atr=8.0, rvol_m15=1.2, spread_ratio=2.0)
    board = choose_board(
        Candidate(side=Side.BUY, legal=True, score=0.55),
        Candidate(side=Side.SELL, legal=True, score=0.52),
    )

    print("Boundary audit:", audit.to_dict())
    print("Adaptive buffer:", buffer)
    print("Board selection:", board)


if __name__ == "__main__":
    main()
