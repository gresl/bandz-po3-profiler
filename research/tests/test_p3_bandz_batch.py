"""Synthetic contract fixtures based on observed Nov 23 event identities."""
import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "p3"))
from bandz_batch import decode, Source, InvalidBatch

SRC = Source("FOREXCOM:GBPUSD")
START, ORIGIN, CONFIRM, QUALIFY = 1795413600000, 1795420800000, 1795427100000, 1795428000000
STREAM = "FOREXCOM:GBPUSD|15|V2"
SIG = f"{STREAM}|-1|{CONFIRM}|{ORIGIN}|1.31231"
C2 = f"{STREAM}|240|-1|{START}"
LINK = f"{C2}|{SIG}"


def event(kind, observed, *, raw=False, structural=False):
    key = SIG if raw else C2 if structural else LINK
    return dict(event_id=f"p2a1|{kind}|{key}|{observed}", kind=kind, side="BEAR",
                observed_ms=observed, c2_start_ms=None if raw else START,
                cisd_close_ms=None if structural else CONFIRM,
                origin_open_ms=None if structural else ORIGIN,
                level=None if structural else 1.31231,
                signal_id=None if structural else SIG, c2_id=None if raw else C2,
                link_id=None if raw or structural else LINK, reason="V2")


def batch(*events, close=CONFIRM):
    return dict(schema="bandz.po3.p2a.v1", symbol=SRC.symbol, chart_tf="15",
                anchor_tf="240", engine="V2", bar_close_ms=close,
                bar_close_price=1.31212, event_count=len(events), omitted_count=0,
                invalid_identity_count=0, events=list(events))


def wire(b):
    return json.dumps(b).encode()


class TestBandzBatch(unittest.TestCase):
    def test_raw_and_link_same_bar(self):
        b = decode(wire(batch(event("CISD_CONFIRMED", CONFIRM, raw=True),
                              event("C2_CISD_LINKED_EARLY", CONFIRM))), SRC)
        self.assertEqual(b["event_count"], 2)
        self.assertEqual(b["events"][0]["signal_id"], b["events"][1]["signal_id"])

    def test_qualification_and_followups(self):
        for kind in ("C2_CISD_QUALIFIED", "C2_CISD_RECLAIMED", "C2_CISD_LINK_ENDED"):
            b = decode(wire(batch(event(kind, QUALIFY), close=QUALIFY)), SRC)
            self.assertEqual(b["events"][0]["link_id"], LINK)

    def test_structural(self):
        for kind in ("C2_CONFIRMED", "C2_REJECTED", "C2_SEQUENCE_ENDED", "C2_SEQUENCE_UNTRACKED"):
            b = decode(wire(batch(event(kind, QUALIFY, structural=True), close=QUALIFY)), SRC)
            self.assertIsNone(b["events"][0]["signal_id"])

    def test_bad_source_and_engine(self):
        raw = wire(batch(event("CISD_CONFIRMED", CONFIRM, raw=True)))
        for source in (Source("FOREXCOM:EURUSD"), Source(SRC.symbol, engine="Legacy")):
            with self.assertRaises(InvalidBatch):
                decode(raw, source)

    def test_invalid_event_mutations(self):
        original = batch(event("C2_CISD_LINKED_EARLY", CONFIRM))
        for key, value in (("event_id", "wrong"), ("signal_id", None),
                           ("link_id", None), ("observed_ms", CONFIRM+1),
                           ("origin_open_ms", CONFIRM+1), ("level", "1.31231"),
                           ("kind", []), ("side", "BOTH"), ("c2_start_ms", True)):
            b = copy.deepcopy(original)
            b["events"][0][key] = value
            with self.subTest(key=key), self.assertRaises(InvalidBatch):
                decode(wire(b), SRC)

    def test_counts_duplicates_and_limits(self):
        e = event("C2_CISD_LINKED_EARLY", CONFIRM)
        for b in (batch(e, e), batch(), dict(batch(e), event_count=2),
                  dict(batch(e), invalid_identity_count=True), batch(*[e]*33)):
            with self.assertRaises(InvalidBatch):
                decode(wire(b), SRC)
        self.assertEqual(decode(wire(dict(batch(), omitted_count=1)), SRC)["omitted_count"], 1)

    def test_invalid_json(self):
        for raw in (b"", b"{}", b'{"x":1,"x":2}', b'{"x":NaN}', b"\xff", b" "*40961):
            with self.assertRaises(InvalidBatch):
                decode(raw, SRC)

    def test_price_tick_padding(self):
        e = event("CISD_CONFIRMED", CONFIRM, raw=True)
        e["level"] = 1.3123
        e["signal_id"] = SIG.replace("1.31231", "1.31230")
        e["event_id"] = e["event_id"].replace("1.31231", "1.31230")
        self.assertEqual(decode(wire(batch(e)), SRC)["events"][0]["signal_id"], e["signal_id"])


if __name__ == "__main__":
    unittest.main()
