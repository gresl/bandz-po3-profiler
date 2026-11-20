import unittest
import csv
import io
from datetime import datetime, timezone
from tempfile import TemporaryDirectory
from pathlib import Path

from research.parse_cisd_pine_logs import parse_logs, as_events, save_events
from research.analyze_cisd_batch import compare

def line(engine, close, level, side="BEAR", kind="CONFIRM", extra=""):
    return (
        f"CISDEVT1|kind={kind}|engine={engine}|symbol=FOREXCOM:GBPUSD|tf=15"
        f"|side={side}|close_ms={close}|level={level}|bar=11800"
        f"|o=1.32000|h=1.32100|l=1.31700|c=1.31800"
        + extra
    )

class TestPineLogsParse(unittest.TestCase):
    def test_realtime_and_historical_prefix_ignored(self):
        ms = 1794987000000
        text = f"2026-11-18 07:15\t{line('V2', ms, '1.31889', extra='|pivot_bar=11720|stretch_atr=0.95|known_ms=1794986100000')}\n"
        rows, warnings = parse_logs(text)
        self.assertFalse(warnings)
        self.assertEqual(rows[0]["close_ms"], str(ms))
        self.assertEqual(rows[0]["symbol"], "FOREXCOM:GBPUSD")
        event = as_events(rows)[0]
        self.assertEqual(event.confirm_utc, datetime.fromtimestamp(ms/1000, tz=timezone.utc))
        self.assertEqual(event.pivot_bar, 11720)
        self.assertEqual(event.stretch_atr, 0.95)

    def test_one_bar_time_disagreement_detected(self):
        v_ms = int(datetime(2026, 11, 18, 7, 30, tzinfo=timezone.utc).timestamp() * 1000)
        l_ms = int(datetime(2026, 11, 18, 7, 15, tzinfo=timezone.utc).timestamp() * 1000)
        text = "\n".join([line("V2", v_ms, "1.31889", extra="|pivot_bar=30|stretch_atr=1.2"),
                           line("LEGACY", l_ms, "1.31889")])
        rows, warnings = parse_logs(text)
        self.assertEqual(len(rows), 2)
        self.assertEqual(compare(as_events(rows))[0].category, "TIME_DIFF")
        self.assertEqual(warnings, [])

    def test_lifecycle_retained_but_not_compared(self):
        ms = int(datetime(2026, 11, 17, 20, 0, tzinfo=timezone.utc).timestamp()*1000)
        text = "\n".join([
            line("V2", ms, "1.32184", kind="LIFECYCLE",
                 extra="|reason=PIVOT_BREACH|pivot_bar=111|state=4"),
            line("LEGACY", ms, "1.32184")])
        rows, _ = parse_logs(text)
        self.assertEqual(len(rows), 2)
        self.assertEqual(len(as_events(rows)), 1)
        self.assertEqual(compare(as_events(rows))[0].category, "LEGACY_ONLY")
        with TemporaryDirectory() as d:
            dest = Path(d)/"out.csv"
            save_events(dest, rows)
            self.assertIn("PIVOT_BREACH", dest.read_text())

    def test_suppresses_identical_pasted_lines_not_real_different_candidates(self):
        ts = 1794987000000
        r1 = line("V2", ts, "1.31889", extra="|pivot_bar=30|known_ms=20")
        r2 = line("V2", ts, "1.31889", extra="|pivot_bar=31|known_ms=23")
        rows, notes = parse_logs("\n".join([r1, r1, r2]))
        self.assertEqual(len(rows), 2)
        self.assertEqual(len(notes), 1)

    def test_mixed_feeds_rejected(self):
        ts = 1794987000000
        a = line("V2", ts, "1.31889")
        b = line("LEGACY", ts, "1.31889").replace("FOREXCOM:GBPUSD", "FX:GBPUSD")
        with self.assertRaisesRegex(ValueError, "Mixed"):
            parse_logs(a+"\n"+b)

    def test_native_tradingview_date_message_csv_replay_feed(self):
        ms = int(datetime(2026, 11, 18, 7, 30, tzinfo=timezone.utc).timestamp() * 1000)
        replay = '={"replay":"internal-opaque-id","symbol":"FOREXCOM:GBPUSD"}'
        v = line("V2", ms, "1.31889", extra="|pivot_bar=11749|stretch_atr=0.73")
        v = v.replace("symbol=FOREXCOM:GBPUSD", "symbol=" + replay)
        writer_buf = io.StringIO()
        writer = csv.DictWriter(writer_buf, fieldnames=["Date", "Message"])
        writer.writeheader()
        writer.writerow({"Date": "2026-11-18T07:15:00.000-00:00",
                         "Message": v})
        rows, notes = parse_logs(writer_buf.getvalue())
        self.assertEqual(notes, [])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["symbol"], "FOREXCOM:GBPUSD")
        self.assertEqual(as_events(rows)[0].confirm_utc,
                         datetime(2026, 11, 18, 7, 30, tzinfo=timezone.utc))

    def test_missing_or_malformed_no_false_positive(self):
        with self.assertRaisesRegex(ValueError, "No valid"):
            parse_logs("Only current candle no exporter logs here")
        with self.assertRaisesRegex(ValueError, "No valid"):
            parse_logs("CISDEVT1|engine=V2|side=BULL")

    def test_historical_open_prefix_does_not_replace_close(self):
        ts=int(datetime(2026,11,18,7,30,tzinfo=timezone.utc).timestamp()*1000)
        data, _ = parse_logs("[2026-11-18 07:15] "+line("V2",ts,"1.31889"))
        self.assertEqual(data[0]["close_utc"], "2026-11-18T07:30:00+00:00")

if __name__ == "__main__":
    unittest.main()
