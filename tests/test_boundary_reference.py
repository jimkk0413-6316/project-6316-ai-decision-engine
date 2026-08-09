import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from project6316.boundary_reference import (
    AlignmentStatus,
    Direction,
    DONCHIAN_SETTINGS,
    OverlayObservation,
    PIVOT_SETTINGS,
    Timeframe,
    audit_boundary_reference,
)


class BoundaryReferenceTests(unittest.TestCase):
    def test_settings(self):
        self.assertEqual((PIVOT_SETTINGS[Timeframe.M5].high_left, PIVOT_SETTINGS[Timeframe.M5].high_right), (2, 2))
        self.assertEqual(DONCHIAN_SETTINGS[Timeframe.M5].length, 12)
        self.assertEqual(DONCHIAN_SETTINGS[Timeframe.M15].length, 8)

    def test_missing_overlay_is_structure_only(self):
        result = audit_boundary_reference(
            timeframe=Timeframe.M5,
            direction=Direction.BUY,
            atr=5.0,
            structural_boundary=100.0,
            structure_readable=True,
            observation=None,
        )
        self.assertEqual(result.status, AlignmentStatus.STRUCTURE_ONLY)
        self.assertFalse(result.future_wait_required)
        self.assertFalse(result.hard_veto_created)

    def test_overlays_cannot_create_structure(self):
        obs = OverlayObservation(
            timeframe=Timeframe.M5,
            pivot_high=100.0,
            donchian_upper=100.0,
            pivot_high_confirmed=True,
            pivot_high_same_event=True,
        )
        result = audit_boundary_reference(
            timeframe=Timeframe.M5,
            direction=Direction.BUY,
            atr=5.0,
            structural_boundary=None,
            structure_readable=False,
            observation=obs,
        )
        self.assertEqual(result.status, AlignmentStatus.N_A)
        self.assertFalse(result.candidate_legality_changed)

    def test_pivot_and_donchian_alignment(self):
        obs = OverlayObservation(
            timeframe=Timeframe.M5,
            pivot_high=100.2,
            donchian_upper=100.3,
            pivot_high_confirmed=True,
            pivot_high_same_event=True,
        )
        result = audit_boundary_reference(
            timeframe=Timeframe.M5,
            direction=Direction.BUY,
            atr=5.0,
            structural_boundary=100.0,
            structure_readable=True,
            observation=obs,
        )
        self.assertEqual(result.status, AlignmentStatus.PIVOT_DC_ALIGNED)

    def test_stale_pivot_ignored(self):
        obs = OverlayObservation(
            timeframe=Timeframe.M15,
            pivot_low=90.0,
            donchian_lower=90.2,
            pivot_low_confirmed=True,
            pivot_low_same_event=False,
        )
        result = audit_boundary_reference(
            timeframe=Timeframe.M15,
            direction=Direction.SELL,
            atr=10.0,
            structural_boundary=90.0,
            structure_readable=True,
            observation=obs,
        )
        self.assertEqual(result.status, AlignmentStatus.DC_ALIGNED)
        self.assertIsNone(result.pivot_reference)

    def test_disagreement_requests_one_correction_not_wait(self):
        obs = OverlayObservation(
            timeframe=Timeframe.M15,
            pivot_low=87.0,
            donchian_lower=86.0,
            pivot_low_confirmed=True,
            pivot_low_same_event=True,
        )
        result = audit_boundary_reference(
            timeframe=Timeframe.M15,
            direction=Direction.SELL,
            atr=10.0,
            structural_boundary=90.0,
            structure_readable=True,
            observation=obs,
        )
        self.assertEqual(result.status, AlignmentStatus.DISAGREEMENT)
        self.assertTrue(result.one_correction_required)
        self.assertFalse(result.future_wait_required)


if __name__ == "__main__":
    unittest.main()
