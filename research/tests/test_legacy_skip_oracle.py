import unittest
from dataclasses import replace
from research.cisd_legacy_skip_oracle import LegacyCisdSnapshot, audit

DEFAULT = LegacyCisdSnapshot("Bearish", 1.32770, 1.32730,
                             1.32745, 1.32755, 2, 4)

class TestLegacySkipGates(unittest.TestCase):
    def test_full_bearish_confirmation(self):
        r = audit(DEFAULT)
        self.assertTrue(r.confirmed)
        self.assertEqual(r.level, 1.32745)

    def test_no_run(self):
        r = audit(replace(DEFAULT, run_first_open=None, run_last_open=None, run_len=0, run_age=None))
        self.assertFalse(r.confirmed)
        self.assertEqual(r.first_failure, "NO_REFERENCE_LEVEL")

    def test_minrun_one_fails_legacy_two(self):
        r = audit(replace(DEFAULT, run_len=1))
        self.assertFalse(r.confirmed)
        self.assertTrue(r.crossed)
        self.assertEqual(r.first_failure, "MIN_RUN")

    def test_candle_color_failure(self):
        r = audit(replace(DEFAULT, opening=1.32720, closing=1.32730))
        self.assertEqual(r.first_failure, "CANDLE_COLOR")

    def test_no_close_break(self):
        r = audit(replace(DEFAULT, closing=1.32750))
        self.assertEqual(r.first_failure, "NO_CLOSE_THROUGH")

    def test_run_age_failure(self):
        r = audit(replace(DEFAULT, run_age=61))
        self.assertEqual(r.first_failure, "RUN_TOO_OLD")

    def test_duplicate_bar_failure(self):
        r = audit(replace(DEFAULT, already_on_bar=True))
        self.assertEqual(r.first_failure, "ALREADY_ON_BAR")

    def test_sensitive_level_uses_last_open(self):
        r = audit(replace(DEFAULT, sensitivity="Sensitive"))
        self.assertEqual(r.level, 1.32755)

    def test_bullish_case(self):
        bull = replace(DEFAULT, side="Bullish", opening=1.32600,
                       closing=1.32640, run_first_open=1.32620, run_last_open=1.32630)
        self.assertTrue(audit(bull).confirmed)

    def test_failed_gates_are_all_reported_separately(self):
        r = audit(replace(DEFAULT, run_len=1, closing=1.32755, run_age=62))
        self.assertFalse(r.min_run_ok)
        self.assertFalse(r.crossed)
        self.assertFalse(r.age_ok)
        self.assertEqual(r.first_failure, "MIN_RUN")

    def test_invalid_configuration_rejected(self):
        with self.assertRaises(ValueError):
            audit(replace(DEFAULT, side="X"))
        with self.assertRaises(ValueError):
            audit(replace(DEFAULT, sensitivity="High"))

if __name__ == "__main__":
    unittest.main()
