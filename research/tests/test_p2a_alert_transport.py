"""Static transport safety and independent contract oracle; not Pine execution."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "indicators/Bandz_Po3_P1_C2_State_Audit.pine"
P2 = ROOT / "indicators/Bandz_Po3_P2A_Alerts.pine"
MARK = "// P1 — OBSERVATIONAL Po3/C2 STATE AUDIT"


def event(kind, t, *, side=-1, c2=100, cisd=115, origin=90, level="1.31231"):
    return dict(kind=kind, observed=t, side=side, c2=c2, cisd=cisd,
                origin=origin, level=level)


class Dispatcher:
    """Independent acceptance oracle for event selection and batched IDs."""
    def __init__(self, mode="Preview", raw=False, early=True, direction="Both",
                 structural=False, reclaim=True, reject=True, link_end=True, seq_end=False):
        self.mode, self.raw, self.early = mode, raw, early
        self.direction, self.structural = direction, structural
        self.reclaim, self.reject, self.link_end, self.seq_end = reclaim, reject, link_end, seq_end
        self.sent, self.links, self.c2s = set(), set(), set()

    def bar(self, events, *, confirmed=True, realtime=False, supported=True, in_window=True):
        if not confirmed or not supported or self.mode == "Off":
            return None
        if self.mode == "Live" and not realtime or self.mode == "Preview" and not in_window:
            return None
        out, omitted, invalid = [], 0, 0
        for e in events:
            k = e["kind"]
            sig = None if any(e[x] is None for x in ("cisd", "origin", "level")) else (
                f'FOREXCOM:GBPUSD|15|V2|{e["side"]}|{e["cisd"]}|{e["origin"]}|{e["level"]}')
            c2 = None if e["c2"] is None else f'FOREXCOM:GBPUSD|15|V2|240|{e["side"]}|{e["c2"]}'
            link = f"{c2}|{sig}" if c2 and sig else None
            raw = k == "CISD_CONFIRMED"
            early = k == "C2_CISD_LINKED_EARLY"
            linked = k in ("C2_CISD_RECLAIMED", "C2_CISD_LINK_ENDED")
            selected = (
                raw and self.raw or early and self.early or
                k == "C2_CONFIRMED" and self.structural or
                k == "C2_CISD_RECLAIMED" and self.reclaim and link in self.links or
                k == "C2_CISD_LINK_ENDED" and self.link_end and link in self.links or
                k == "C2_REJECTED" and self.reject and c2 in self.c2s or
                k in ("C2_SEQUENCE_ENDED", "C2_SEQUENCE_UNTRACKED") and self.seq_end and c2 in self.c2s)
            if not selected or self.direction != "Both" and (
                    e["side"] != (1 if self.direction == "Bullish" else -1)):
                continue
            key = sig if raw else link if early or linked else c2
            if key is None:
                invalid += 1
                continue
            eid = f'p2a1|{k}|{key}|{e["observed"]}'
            if eid in self.sent:
                continue
            if len(out) >= 32:
                omitted += 1
                continue
            out.append(dict(event_id=eid, kind=k, signal_id=sig, c2_id=c2,
                            link_id=link, observed_ms=e["observed"]))
            self.sent.add(eid)
            if early:
                self.links.add(link)
                self.c2s.add(c2)
        if not out and not omitted and not invalid:
            return None
        return json.loads(json.dumps(dict(schema="bandz.po3.p2a.v1", events=out,
                                         event_count=len(out), omitted_count=omitted,
                                         invalid_identity_count=invalid)))


class StaticChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = BASE.read_text(encoding="utf8")
        cls.p2 = P2.read_text(encoding="utf8")
        cls.audit = cls.p2.split(MARK, 1)[1]
        cls.transport = cls.audit.split("// P2A — CLOSED-BAR NOTIFICATION TRANSPORT", 1)[1]

    def test_frozen_engine_prefix(self):
        expected = self.base.split(MARK, 1)[0].replace(
            'indicator("Bandz Po3 P1 — C2 State Audit", shorttitle="Bandz P1 C2",',
            'indicator("Bandz Po3 P2A — Alerts", shorttitle="Bandz P2A",')
        self.assertEqual(self.p2.split(MARK, 1)[0], expected)

    def test_one_alert_live_confirmed_only(self):
        self.assertEqual(len(re.findall(r"\balert\s*\(", self.p2)), 1)
        self.assertNotRegex(self.p2, r"\balertcondition\s*\(")
        self.assertIn('input.string("Off", "Alerts mode"', self.audit)
        self.assertIn('if p2Mode == "Live" and barstate.isrealtime and barstate.isconfirmed\n            alert(payload, alert.freq_once_per_bar_close)', self.transport)
        self.assertIn('if p2Mode == "Preview"', self.transport)
        self.assertIn('log.info("P2A_PREVIEW|" + payload)', self.transport)

    def test_queue_and_stable_identity(self):
        for s in ("p2Queue.clear()", "p2Queue.push(PoP2Event.new",
                  "e.cisdOriginAt := sg.originAt", "p2OriginTime(origin)",
                  "off < 5000 ? time[off] : na", "ticker.standard(syminfo.tickerid)",
                  'p2Stream + "|" + str.tostring(ev.side)', "str.tostring(ev.originAt)",
                  'string eid = "p2a1|"', "p2Sent.includes(eid)"):
            self.assertIn(s, self.audit)
        self.assertNotIn("bar_index", self.transport.replace(
            "// IDs are based on timestamps, not dataset-dependent bar_index.", ""))

    def test_no_qualified_dispatch_and_bounded_batch(self):
        self.assertNotIn('"C2_CISD_QUALIFIED"', self.transport)
        for s in ("count < 32", "28000", "omitted += 1", "invalid += 1",
                  "cache.size() > 512", "p2NotifiedLinks.includes(link)",
                  "p2NotifiedC2.includes(c2)", "p2Supported and barstate.isconfirmed",
                  "timeframe.multiplier == 15", "timeframe.in_seconds(poSrcLane.tf) == 14400"):
            self.assertIn(s, self.audit)


class ContractChecks(unittest.TestCase):
    def test_off_and_live_history_and_open_bar(self):
        e = event("C2_CISD_LINKED_EARLY", 115)
        self.assertIsNone(Dispatcher("Off").bar([e], realtime=True))
        d = Dispatcher("Live")
        self.assertIsNone(d.bar([e]))
        self.assertIsNone(d.bar([e], realtime=True, confirmed=False))
        self.assertIsNotNone(d.bar([e], realtime=True))

    def test_preview_window_and_scope(self):
        d = Dispatcher()
        e = event("C2_CISD_LINKED_EARLY", 115)
        self.assertIsNone(d.bar([e], in_window=False))
        self.assertIsNone(d.bar([e], supported=False))
        self.assertIsNone(d.bar([event("C2_CISD_RECLAIMED", 130)]))
        self.assertIsNotNone(d.bar([e]))

    def test_raw_and_early_same_bar_both_retained(self):
        d = Dispatcher(raw=True)
        p = d.bar([event("CISD_CONFIRMED", 115, c2=None),
                   event("C2_CISD_LINKED_EARLY", 115)])
        self.assertEqual(p["event_count"], 2)
        self.assertEqual(p["events"][0]["signal_id"], p["events"][1]["signal_id"])
        self.assertNotEqual(p["events"][0]["event_id"], p["events"][1]["event_id"])

    def test_same_level_distinct_origin_or_confirmation(self):
        d = Dispatcher(raw=True)
        p = d.bar([event("CISD_CONFIRMED", 115, c2=None),
                   event("CISD_CONFIRMED", 115, c2=None, origin=95)])
        self.assertEqual(p["event_count"], 2)
        q = d.bar([event("CISD_CONFIRMED", 130, c2=None, cisd=130)])
        self.assertNotEqual(p["events"][0]["signal_id"], q["events"][0]["signal_id"])

    def test_duplicate_event_id_stable_across_instances(self):
        e = event("C2_CISD_LINKED_EARLY", 115)
        d = Dispatcher()
        a = d.bar([e, e])
        self.assertEqual(a["event_count"], 1)
        self.assertIsNone(d.bar([e]))
        self.assertEqual(a, Dispatcher().bar([e]))

    def test_followups_only_for_notified_link_and_c2(self):
        d = Dispatcher()
        self.assertIsNone(d.bar([event("C2_CISD_RECLAIMED", 130)]))
        d.bar([event("C2_CISD_LINKED_EARLY", 115)])
        self.assertIsNone(d.bar([event("C2_CISD_RECLAIMED", 130, cisd=120)]))
        p = d.bar([event("C2_CISD_RECLAIMED", 130), event("C2_CISD_LINK_ENDED", 130)])
        self.assertEqual(p["event_count"], 2)
        self.assertIsNotNone(d.bar([event("C2_REJECTED", 160, cisd=None, origin=None, level=None)]))
        self.assertIsNone(d.bar([event("C2_REJECTED", 160, c2=200)]))

    def test_qualified_never_emitted(self):
        d = Dispatcher(raw=True, structural=True, seq_end=True)
        d.bar([event("C2_CISD_LINKED_EARLY", 115)])
        self.assertIsNone(d.bar([event("C2_CISD_QUALIFIED", 160),
                                 event("C2_CISD_LINKED_AT_CLOSE", 160)]))

    def test_raw_off_early_on_and_direction(self):
        d = Dispatcher(direction="Bullish")
        self.assertIsNone(d.bar([event("C2_CISD_LINKED_EARLY", 115),
                                 event("CISD_CONFIRMED", 115, side=1)]))
        self.assertIsNotNone(d.bar([event("C2_CISD_LINKED_EARLY", 115, side=1)]))

    def test_missing_origin_and_overflow_reported(self):
        d = Dispatcher(raw=True)
        p = d.bar([event("CISD_CONFIRMED", 115, origin=None)])
        self.assertEqual(p["invalid_identity_count"], 1)
        q = d.bar([event("CISD_CONFIRMED", 130, origin=i) for i in range(40)])
        self.assertEqual(q["event_count"], 32)
        self.assertEqual(q["omitted_count"], 8)


if __name__ == "__main__":
    unittest.main()
