"""P1 closed-HTF C2 audit: static safety and event-spec regression.

These tests do not pretend to compile Pine; the reference state transition
tests below define expected behavior for manual TradingView Replay acceptance.
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "indicators/Bandz_Po3_V2_Visual_Test.pine"
P1 = ROOT / "indicators/Bandz_Po3_P1_C2_State_Audit.pine"
P1_MARKER = "// P1 — OBSERVATIONAL Po3/C2 STATE AUDIT"

class C2ReferenceModel:
    """Small independent acceptance oracle (not Pine execution)."""

    def __init__(self):
        self.seen_at = None
        self.c2_at = None
        self.cisd_at = None
        self.linked = False
        self.visible = False
        self.state = "ABSENT"
        self.qualified_at = None
        self.broken_at = None

    def on_close(self, t, *, swept=False, c2_final=False, inside=False,
                 cisd_confirm=False, linked=False, visible=False,
                 reclaim=False, link_cleared=False):
        if swept and self.state == "ABSENT":
            self.seen_at = t
            self.state = "C2_LIVE"
        if cisd_confirm:
            self.cisd_at = t
        if linked:
            self.linked = True
        if link_cleared:
            self.linked = False
        if c2_final and self.state == "C2_LIVE":
            self.state = "C2_CONFIRMED" if inside else "C2_REJECTED"
            if inside:
                self.c2_at = t
        self.visible = visible
        if (self.state == "C2_CONFIRMED" and self.cisd_at is not None
                and self.linked and self.visible
                and self.qualified_at is None):
            self.qualified_at = t
        if reclaim and self.qualified_at is not None and self.broken_at is None:
            self.broken_at = t

class TestP1StaticSafety(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = BASE.read_text(encoding="utf8")
        cls.p1 = P1.read_text(encoding="utf8")

    def test_frozen_visual_indicator_unchanged(self):
        before = self.base.replace('indicator("Bandz Po3 V2 — Visual Test", shorttitle="Bandz V2 Test",',
                                   'indicator("Bandz Po3 P1 — C2 State Audit", shorttitle="Bandz P1 C2",')
        self.assertIn(P1_MARKER, self.p1)
        self.assertEqual(self.p1.split(P1_MARKER)[0].rstrip().removesuffix('// =============================================================================').rstrip(), before.rstrip())

    def test_p1_has_no_alerts_or_writes_to_original_engine(self):
        appendix = self.p1.split(P1_MARKER, 1)[1]
        self.assertFalse(re.search(r"\balert(?:condition)?\s*\(", appendix))
        for statement in ("poRecs.push(", "poRecs.set(", "poCisds.push(",
                          "v2rEvents.push(", "rc.cisdBar :=", "rc.alive :=",
                          "poLinkCisd(", "poSyncRecs("):
            self.assertNotIn(statement, appendix)
        self.assertIn('bool p1On = input.bool(false', appendix)

    def test_only_closed_confirmations_and_real_htf_boundary(self):
        appendix = self.p1.split(P1_MARKER, 1)[1]
        for contract in (
            "barstate.isconfirmed and not na(time_close)",
            "time_close == sourceEnd",
            "c2.startTime == sourceStart",
            "if sourceClosing",
            "if sq.closedIn",
            "e.c2ClosedAt := time_close",
            "e.lastReason := \"C2_CLOSED_OUTSIDE_C1\"",
            "e.lastReason := \"HTF_CLOSE_NOT_OBSERVED\"",
            "sg.confirmedAt <= time_close",
            "poRecVisible(rc)",
            "e.qualifiedAt := time_close",
            "e.brokenAt := time_close",
            "p1FindSignal(e.side, rc.cisdBar, rc.cisdLevel)",
            "poSeqSlot == 0",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, appendix)

    def test_bounded_memory_and_table_only_on_last_bar(self):
        appendix = self.p1.split(P1_MARKER, 1)[1]
        self.assertIn("while p1Events.size() > 40", appendix)
        self.assertIn("while p1Signals.size() > 256", appendix)
        self.assertIn("if p1On and barstate.islast and not na(p1Table)", appendix)

class TestC2ReferenceAcceptance(unittest.TestCase):
    def test_live_c2_with_raw_cisd_never_qualifies(self):
        x = C2ReferenceModel()
        x.on_close(100, swept=True, cisd_confirm=True, linked=True, visible=True)
        self.assertEqual(x.state, "C2_LIVE")
        self.assertIsNone(x.qualified_at)

    def test_earlier_cisd_qualifies_only_at_later_c2_close(self):
        x = C2ReferenceModel()
        x.on_close(100, swept=True)
        x.on_close(115, cisd_confirm=True, linked=True, visible=True)
        self.assertIsNone(x.qualified_at)
        x.on_close(160, c2_final=True, inside=True, visible=True)
        self.assertEqual(x.cisd_at, 115)
        self.assertEqual(x.c2_at, 160)
        self.assertEqual(x.qualified_at, 160)

    def test_rejection_never_promotes_a_raw_cisd(self):
        x = C2ReferenceModel()
        x.on_close(100, swept=True, cisd_confirm=True, linked=True)
        x.on_close(160, c2_final=True, inside=False, visible=True)
        self.assertEqual(x.state, "C2_REJECTED")
        self.assertIsNone(x.qualified_at)

    def test_original_visibility_gate_prevents_premature_xc2_qualification(self):
        x = C2ReferenceModel()
        x.on_close(100, swept=True, cisd_confirm=True, linked=True)
        x.on_close(160, c2_final=True, inside=True, visible=False)
        self.assertIsNone(x.qualified_at)
        x.on_close(175, visible=True)
        self.assertEqual(x.qualified_at, 175)

    def test_cleared_provisional_link_is_not_carried_forward(self):
        x = C2ReferenceModel()
        x.on_close(100, swept=True, cisd_confirm=True, linked=True)
        x.on_close(115, link_cleared=True)
        x.on_close(160, c2_final=True, inside=True, visible=True)
        self.assertIsNone(x.qualified_at)

    def test_post_close_cisd_and_first_reclamation(self):
        x = C2ReferenceModel()
        x.on_close(100, swept=True)
        x.on_close(160, c2_final=True, inside=True)
        x.on_close(175, cisd_confirm=True, linked=True, visible=True)
        self.assertEqual(x.qualified_at, 175)
        x.on_close(190, reclaim=True)
        x.on_close(205, reclaim=True)
        self.assertEqual(x.broken_at, 190)

if __name__ == "__main__":
    unittest.main()
