import csv
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from research.analyze_cisd_batch import FIELDS, Event, compare, parse_export, save_report

UTC = timezone.utc

def event(hour, minute, provider, direction, level, *, day=18):
    return Event(datetime(2026, 11, day, hour, minute, tzinfo=UTC), provider, direction, level)

class TestBatchComparison(unittest.TestCase):
    def test_matches_exact_before_time_diff(self):
        cases = [
            event(7, 30, "V2", "BEAR", 1.31889),
            event(7, 15, "LEGACY", "BEAR", 1.31889),
            event(7, 30, "LEGACY", "BULL", 1.31638),
            event(7, 30, "V2", "BULL", 1.31638),
        ]
        self.assertEqual([r.category for r in compare(cases)], ["EXACT", "TIME_DIFF"])

    def test_full_synthetic_distribution(self):
        # Synthetic counts mirror a screenshot but synthetic match cases
        # are NOT market data or independent chart evidence.
        pairs = [
            event(0, 0, "V2", "BEAR", 1.32111),
            event(0, 0, "LEGACY", "BEAR", 1.32111),
            event(1, 0, "V2", "BULL", 1.32011),
            event(1, 0, "LEGACY", "BULL", 1.32011),
            event(2, 0, "V2", "BEAR", 1.31911),
            event(2, 0, "LEGACY", "BEAR", 1.31911),
            event(2, 30, "V2", "BULL", 1.31901),
            event(2, 30, "LEGACY", "BULL", 1.31901),
            event(3, 30, "V2", "BEAR", 1.31810),
            event(3, 30, "LEGACY", "BEAR", 1.31810),
            event(7, 30, "V2", "BEAR", 1.31889),
            event(7, 15, "LEGACY", "BEAR", 1.31889),
            event(9, 45, "V2", "BULL", 1.31638),
            event(7, 0, "V2", "BULL", 1.31930),
            event(6, 0, "V2", "BEAR", 1.31940),
            event(4, 15, "V2", "BEAR", 1.31970),
            event(12, 45, "V2", "BULL", 1.31945, day=17),
            event(3, 0, "LEGACY", "BEAR", 1.32042),
            event(20, 0, "LEGACY", "BEAR", 1.32184, day=17),
        ]
        rows = compare(pairs)
        self.assertEqual({k: sum(x.category == k for x in rows) for k in
                          ("EXACT", "TIME_DIFF", "V2_ONLY", "LEGACY_ONLY")},
                         {"EXACT": 5, "TIME_DIFF": 1, "V2_ONLY": 5, "LEGACY_ONLY": 2})

    def test_price_gap_at_same_time(self):
        rows = compare([event(3, 0, "V2", "BEAR", 1.32750),
                        event(3, 0, "LEGACY", "BEAR", 1.32800)])
        self.assertEqual(rows[0].category, "LEVEL_DIFF")

    def test_direction_must_agree(self):
        rows = compare([event(3, 0, "V2", "BULL", 1.32750),
                        event(3, 0, "LEGACY", "BEAR", 1.32750)])
        self.assertEqual({r.category for r in rows}, {"V2_ONLY", "LEGACY_ONLY"})

    def test_csv_roundtrip_and_utc_closing_bar(self):
        with TemporaryDirectory() as d:
            src = Path(d) / "tv.csv"
            headers = ["time", "open", "close"] + list(FIELDS.values())
            def row(bar_time, **data):
                result = {key: "" for key in headers}
                result.update({"time": bar_time, "open": "1.32", "close": "1.318"})
                for field, val in data.items():
                    result[FIELDS[field]] = str(val)
                return result
            with src.open("w", newline="") as f:
                wr = csv.DictWriter(f, fieldnames=headers)
                wr.writeheader()
                wr.writerow(row("2026-11-18T07:15:00+00:00",
                                v2_bear=1.31889, v2_bear_atr=0.75,
                                v2_bear_pivot=9876, v2_bear_count=1))
                wr.writerow(row("2026-11-18T07:00:00+00:00",
                                legacy_bear=1.31889))
            events, warnings = parse_export(src)
            self.assertFalse(warnings)
            v = next(e for e in events if e.source == "V2")
            self.assertEqual(v.confirm_utc, datetime(2026, 11, 18, 7, 30, tzinfo=UTC))
            self.assertEqual(v.pivot_bar, 9876)
            self.assertEqual(v.stretch_atr, 0.75)
            self.assertEqual(compare(events)[0].category, "TIME_DIFF")
            dest = Path(d) / "result.csv"
            save_report(dest, compare(events))
            self.assertIn("TIME_DIFF", dest.read_text())

    def test_same_bar_multiple_candidates_warns(self):
        with TemporaryDirectory() as d:
            p = Path(d) / "t.csv"
            headers = ["time"] + list(FIELDS.values())
            with p.open("w", newline="") as f:
                wr = csv.DictWriter(f, fieldnames=headers)
                wr.writeheader()
                wr.writerow({"time": "2026-11-18T07:15:00Z",
                             FIELDS["v2_bear"]: 1.31889,
                             FIELDS["v2_bear_count"]: 2})
            events, warnings = parse_export(p)
            self.assertEqual(events[0].candidate_count, 2)
            self.assertEqual(len(warnings), 1)

    def test_missing_export_raises(self):
        with TemporaryDirectory() as d:
            p = Path(d) / "t.csv"
            p.write_text("time,open,close\\n2026-11-18T07:15:00Z,1.32,1.31\\n")
            with self.assertRaisesRegex(ValueError, "CISDEXP_"):
                parse_export(p)

if __name__ == "__main__":
    unittest.main()
