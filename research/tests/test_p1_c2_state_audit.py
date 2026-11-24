"""P1B contract and static preservation checks; NOT a Pine interpreter."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "indicators/Bandz_Po3_V2_Visual_Test.pine"
P1 = ROOT / "indicators/Bandz_Po3_P1_C2_State_Audit.pine"
MARKER = "// P1 — OBSERVATIONAL Po3/C2 STATE AUDIT"


class C2ReferenceModel:
    """Independent acceptance oracle with immutable event snapshots."""
    def __init__(self):
        self.state = "ABSENT"
        self.c2_at = None
        self.early_at = None
        self.link = None
        self.ended = False
        self.events = []

    def emit(self, kind, t, link_id=None):
        self.events.append((kind, t, link_id))

    def close(self, t, *, sweep=False, c2_final=None, raw=None,
              attach=None, reclaim=False, clear=False, visible=True,
              end=False, gap=False):
        if raw is not None:
            self.emit("CISD_CONFIRMED", t, raw)
        if sweep and self.state == "ABSENT":
            self.state = "LIVE"
            self.emit("C2_CANDIDATE", t)
        if self.state == "LIVE" and c2_final is not None:
            self.state = "PASS" if c2_final else "REJECT"
            self.c2_at = t
            self.emit("C2_CONFIRMED" if c2_final else "C2_REJECTED", t)
        if self.state == "LIVE" and gap:
            self.state = "UNVERIFIED"
            self.emit("C2_UNVERIFIED", t)
        if reclaim and self.link and self.link["active"] and not self.link["reclaimed"]:
            self.link["reclaimed"] = True
            self.emit("C2_CISD_RECLAIMED", t, self.link["id"])
        replace = attach is not None and self.link and attach != self.link["id"]
        if (clear or replace or end) and self.link and self.link["active"]:
            self.link["active"] = False
            self.emit("C2_CISD_LINK_ENDED", t, self.link["id"])
        if attach is not None and not self.ended and not end and self.state != "UNVERIFIED":
            if self.link is None or attach != self.link["id"]:
                self.link = dict(id=attach, active=True, reclaimed=False, qualified=None)
                if self.state == "LIVE":
                    if self.early_at is None:
                        self.early_at = t
                    kind = "C2_CISD_LINKED_EARLY"
                else:
                    kind = "C2_CISD_LINKED_AT_CLOSE" if self.c2_at == t else "C2_CISD_LINKED_AFTER_CLOSE"
                self.emit(kind, t, attach)
        if (self.state == "PASS" and self.link and self.link["active"]
                and not self.link["reclaimed"] and not self.ended and not end and visible
                and self.link["qualified"] is None):
            self.link["qualified"] = t
            self.emit("C2_CISD_QUALIFIED", t, self.link["id"])
        if end or self.state in ("REJECT", "UNVERIFIED"):
            if self.link and self.link["active"]:
                self.link["active"] = False
                self.emit("C2_CISD_LINK_ENDED", t, self.link["id"])
            if not self.ended:
                self.ended = True
                self.emit("C2_SEQUENCE_ENDED", t)


class TestP1StaticSafety(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = BASE.read_text(encoding="utf8")
        cls.p1 = P1.read_text(encoding="utf8")
        cls.audit = cls.p1.split(MARKER, 1)[1]

    def test_frozen_visual_indicator_unchanged(self):
        before = self.base.replace('indicator("Bandz Po3 V2 — Visual Test", shorttitle="Bandz V2 Test",',
                                   'indicator("Bandz Po3 P1 — C2 State Audit", shorttitle="Bandz P1 C2",')
        self.assertEqual(self.p1.split(MARKER)[0].rstrip().removesuffix('// =============================================================================').rstrip(), before.rstrip())

    def test_read_only_opt_in_no_alerts(self):
        self.assertFalse(re.search(r"\balert(?:condition)?\s*\(", self.audit))
        self.assertFalse(re.search(r"\brc\.\w+\s*:=", self.audit))
        for s in ("poRecs.push(", "poRecs.set(", "poCisds.push(", "v2rEvents.push(",
                  "poLinkCisd(", "poSyncRecs("):
            self.assertNotIn(s, self.audit)
        self.assertIn('bool p1On = input.bool(false', self.audit)

    def test_closed_bar_identity_and_qualification_guards(self):
        for s in ("barstate.isconfirmed and not na(time_close)", "time_close == sourceEnd",
                  "c2.startTime == sourceStart", "if sq.closedIn", "e.c2ClosedAt := time_close",
                  "sg.originBar == origin and sg.level == level", "poSeqSlot == 0",
                  "e.cisdConfirmedAt <= time_close", "poRecVisible(rc)", "na(rc.cisdBrokeT)",
                  "na(e.sequenceEndedAt)", "na(e.reclaimedAt)", "e.qualifiedAt := time_close",
                  "e.reclaimedAt := time_close", "p1SameLink(e, rc)"):
            with self.subTest(contract=s):
                self.assertIn(s, self.audit)
        self.assertNotIn("e.cisdBar := na", self.audit)
        self.assertNotIn("e.cisdConfirmedAt := na", self.audit)

    def test_immutable_event_records_bounded_and_visible(self):
        for s in ("p1Ledger.push(PoP1Event.new(kind, time_close, side, c2Start, cisdAt, level, reason))",
                  "while p1Ledger.size() > 192", "while p1Events.size() > 40",
                  "while p1Signals.size() > 256", "if p1On and barstate.islast and not na(p1Table)",
                  '"C2 summary"', '"Event history"', '"CISD_CONFIRMED"',
                  '"C2_CISD_LINKED_EARLY"', '"C2_CISD_LINKED_AT_CLOSE"', '"C2_CISD_LINKED_AFTER_CLOSE"',
                  '"C2_CISD_RECLAIMED"', '"C2_CISD_LINK_ENDED"', '"C2_CISD_QUALIFIED"',
                  '"C2_UNVERIFIED"', '"C2_SEQUENCE_UNTRACKED"'):
            with self.subTest(contract=s):
                self.assertIn(s, self.audit)
        self.assertNotRegex(self.audit, r"e\.state\s*:=\s*3\b")

    def test_reclamation_checked_before_link_end(self):
        section = self.audit.split("bool sameLink = p1SameLink(e, rc)", 1)[1]
        self.assertLess(section.index('p1EmitLink("C2_CISD_RECLAIMED"'), section.index("p1EndLink(e, endedWhy)"))


class TestC2ReferenceAcceptance(unittest.TestCase):
    def test_raw_without_c2(self):
        m = C2ReferenceModel()
        m.close(15, raw="A")
        self.assertEqual(m.events, [("CISD_CONFIRMED", 15, "A")])

    def test_early_link_then_qualification_once(self):
        m = C2ReferenceModel()
        m.close(15, sweep=True, raw="A", attach="A")
        self.assertIsNone(m.link["qualified"])
        m.close(60, c2_final=True)
        m.close(75)
        self.assertEqual(m.early_at, 15)
        self.assertEqual(m.link["qualified"], 60)
        self.assertEqual(m.events.count(("C2_CISD_QUALIFIED", 60, "A")), 1)

    def test_early_reclaim_before_c2_close_preserves_history(self):
        m = C2ReferenceModel()
        m.close(15, sweep=True, raw="A", attach="A")
        m.close(30, reclaim=True)
        m.close(60, c2_final=True)
        self.assertEqual(m.state, "PASS")
        self.assertIsNone(m.link["qualified"])
        self.assertIn(("C2_CISD_LINKED_EARLY", 15, "A"), m.events)
        self.assertIn(("C2_CISD_RECLAIMED", 30, "A"), m.events)

    def test_same_bar_link_is_not_early(self):
        m = C2ReferenceModel()
        m.close(15, sweep=True)
        m.close(60, c2_final=True, raw="A", attach="A")
        self.assertIsNone(m.early_at)
        self.assertIn(("C2_CISD_LINKED_AT_CLOSE", 60, "A"), m.events)
        self.assertEqual(m.link["qualified"], 60)

    def test_post_close_link_and_later_reclaim(self):
        m = C2ReferenceModel()
        m.close(15, sweep=True)
        m.close(60, c2_final=True)
        m.close(75, raw="A", attach="A")
        m.close(90, reclaim=True)
        m.close(105, reclaim=True)
        self.assertEqual(m.link["qualified"], 75)
        self.assertEqual(m.events.count(("C2_CISD_RECLAIMED", 90, "A")), 1)

    def test_reject_keeps_early_evidence(self):
        m = C2ReferenceModel()
        m.close(15, sweep=True, raw="A", attach="A")
        m.close(60, c2_final=False)
        self.assertEqual(m.state, "REJECT")
        self.assertIsNone(m.link["qualified"])
        self.assertFalse(m.link["active"])
        self.assertIn(("C2_CISD_LINKED_EARLY", 15, "A"), m.events)

    def test_clear_and_replacement_keeps_old_record(self):
        m = C2ReferenceModel()
        m.close(15, sweep=True, raw="A", attach="A")
        m.close(30, clear=True)
        m.close(45, raw="B", attach="B")
        m.close(60, c2_final=True)
        self.assertIn(("C2_CISD_LINK_ENDED", 30, "A"), m.events)
        self.assertIn(("C2_CISD_QUALIFIED", 60, "B"), m.events)
        self.assertEqual(m.early_at, 15)

    def test_same_bar_reclaim_and_sequence_end(self):
        m = C2ReferenceModel()
        m.close(15, sweep=True, raw="A", attach="A")
        m.close(60, c2_final=True)
        m.close(75, reclaim=True, end=True)
        self.assertEqual(m.state, "PASS")
        self.assertIn(("C2_CISD_RECLAIMED", 75, "A"), m.events)
        self.assertIn(("C2_CISD_LINK_ENDED", 75, "A"), m.events)

    def test_visibility_gate_then_reclaim_never_qualifies(self):
        m = C2ReferenceModel()
        m.close(15, sweep=True, raw="A", attach="A")
        m.close(60, c2_final=True, visible=False)
        m.close(75, reclaim=True, visible=False)
        m.close(90, visible=True)
        self.assertIsNone(m.link["qualified"])

    def test_gap_not_retroactively_confirmed(self):
        m = C2ReferenceModel()
        m.close(15, sweep=True, raw="A", attach="A")
        m.close(90, gap=True)
        m.close(105, c2_final=True)
        self.assertEqual(m.state, "UNVERIFIED")
        self.assertIsNone(m.link["qualified"])

    def test_ended_sequence_cannot_resurrect(self):
        m = C2ReferenceModel()
        m.close(15, sweep=True, raw="A", attach="A")
        m.close(60, c2_final=True, visible=False)
        m.close(75, end=True)
        m.close(90, raw="B", attach="B")
        self.assertEqual(m.link["id"], "A")
        self.assertIsNone(m.link["qualified"])


if __name__ == "__main__":
    unittest.main()
