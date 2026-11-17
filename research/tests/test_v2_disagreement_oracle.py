"""Synthetic classification regressions for V2 vs legacy closed-event audit."""
import unittest
from research.cisd_v2_disagreement_oracle import Signal, compare

def e(bar, side, level, state="CONFIRMED"):
    return Signal(bar, side, level, state)

class DisagreementAuditTests(unittest.TestCase):
    def test_exact_same_close_and_level(self):
        out=compare([e(20,"BEAR",1.33454)],[e(20,"BEAR",1.33454)])
        self.assertEqual([x.category for x in out],["EXACT"])

    def test_small_tick_tolerance(self):
        out=compare([e(20,"BULL",1.32606)],[e(20,"BULL",1.32608)])
        self.assertEqual(out[0].category,"EXACT")

    def test_same_time_different_reference_level(self):
        out=compare([e(20,"BULL",1.32606)],[e(20,"BULL",1.32644)])
        self.assertEqual([x.category for x in out],["LEVEL_DIFF"])

    def test_one_bar_close_difference_is_not_exact(self):
        out=compare([e(20,"BEAR",1.33454)],[e(21,"BEAR",1.33455)])
        self.assertEqual([x.category for x in out],["TIME_DIFF"])

    def test_unrelated_near_time_levels_stay_unmatched(self):
        out=compare([e(20,"BEAR",1.33454)],[e(21,"BEAR",1.33000)])
        self.assertEqual({x.category for x in out},{"V2_ONLY","LEGACY_ONLY"})

    def test_opposite_direction_is_not_match(self):
        out=compare([e(20,"BEAR",1.33454)],[e(20,"BULL",1.33454)])
        self.assertEqual({x.category for x in out},{"V2_ONLY","LEGACY_ONLY"})

    def test_rejected_candidate_is_not_confirmed(self):
        out=compare([e(20,"BEAR",1.33454,"REJECTED")],[e(20,"BEAR",1.33454)])
        self.assertEqual([x.category for x in out],["LEGACY_ONLY"])

    def test_invalidated_after_confirmation_remains_matchable(self):
        out=compare([e(20,"BEAR",1.33454,"INVALIDATED")],[e(20,"BEAR",1.33454)])
        self.assertEqual([x.category for x in out],["EXACT"])

    def test_one_to_one_pair_prevents_reuse(self):
        out=compare([e(20,"BEAR",1.33454),e(20,"BEAR",1.33455)],[e(20,"BEAR",1.33454)])
        self.assertEqual([x.category for x in out].count("EXACT"),1)
        self.assertEqual([x.category for x in out].count("V2_ONLY"),1)

    def test_window_cutoff_excludes_old_events(self):
        out=compare([e(10,"BEAR",1.33000),e(20,"BULL",1.32606)],
                    [e(10,"BEAR",1.33000),e(20,"BULL",1.32606)],cutoff=15)
        self.assertEqual(len(out),1)
        self.assertEqual(out[0].category,"EXACT")

if __name__=="__main__":
    unittest.main()
