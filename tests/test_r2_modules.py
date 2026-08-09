import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from project6316.adaptive_buffer import calculate_adaptive_buffer
from project6316.guardrails import (
    SetupType,
    daily_loss_circuit_hit,
    manual_oco_combined_risk_allowed,
    micro_expiry_minutes,
    provisional_direction_blocked,
    psychological_level_adjustment,
    risk_ceiling,
)
from project6316.oco import Candidate, Side, choose_board


class R2Tests(unittest.TestCase):
    def test_adaptive_buffer_floor_when_rvol_missing(self):
        r = calculate_adaptive_buffer(m15_atr=10.0, rvol_m15=None)
        self.assertAlmostEqual(r.base_buffer_points, 1.0)
        self.assertIn("floor buffer", r.note)

    def test_adaptive_buffer_clamped_to_ceiling(self):
        r = calculate_adaptive_buffer(m15_atr=10.0, rvol_m15=10.0)
        self.assertAlmostEqual(r.base_buffer_points, 1.8)

    def test_elevated_spread_adds_buffer(self):
        r = calculate_adaptive_buffer(m15_atr=10.0, rvol_m15=1.0, spread_ratio=2.0)
        self.assertAlmostEqual(r.base_buffer_points, 1.5)
        self.assertAlmostEqual(r.spread_extra_points, 0.5)
        self.assertTrue(r.orders_allowed)

    def test_extreme_spread_blocks(self):
        r = calculate_adaptive_buffer(m15_atr=10.0, rvol_m15=1.0, spread_ratio=2.5)
        self.assertFalse(r.orders_allowed)

    def test_provisional_risk_softening(self):
        self.assertFalse(risk_ceiling(risk_atr=1.7, setup_type=SetupType.COMPLETE).allowed)
        p = risk_ceiling(risk_atr=1.7, setup_type=SetupType.PROVISIONAL)
        self.assertTrue(p.allowed)
        self.assertTrue(p.elevated_risk_flag)

    def test_provisional_circuit_breaker(self):
        self.assertFalse(provisional_direction_blocked(1))
        self.assertTrue(provisional_direction_blocked(2))

    def test_daily_loss_circuit(self):
        self.assertTrue(daily_loss_circuit_hit(equity=10_000, realised_plus_floating_loss=150))
        self.assertFalse(daily_loss_circuit_hit(equity=10_000, realised_plus_floating_loss=149.99))

    def test_manual_oco_combined_risk(self):
        self.assertTrue(manual_oco_combined_risk_allowed(equity=10_000, buy_risk=20, sell_risk=30))
        self.assertFalse(manual_oco_combined_risk_allowed(equity=10_000, buy_risk=30, sell_risk=30))

    def test_micro_expiry(self):
        self.assertEqual(micro_expiry_minutes(m5_atr=2.5), 12)
        self.assertEqual(micro_expiry_minutes(m5_atr=3.0), 8)

    def test_psychological_level_penalty(self):
        near, adjusted, level = psychological_level_adjustment(entry=4050.5, m15_atr=10.0, score=100.0)
        self.assertTrue(near)
        self.assertEqual(adjusted, 95.0)
        self.assertEqual(level, 4050.0)

    def test_oco_preference(self):
        board = choose_board(
            Candidate(side=Side.BUY, legal=True, score=0.6),
            Candidate(side=Side.SELL, legal=True, score=0.4),
        )
        self.assertEqual(board.mode, "TWO_SIDED_OCO")
        self.assertEqual(set(board.selected_sides), {Side.BUY, Side.SELL})


if __name__ == "__main__":
    unittest.main()
