import csv
import io
import unittest
from datetime import datetime, timezone

from research.parse_cisd_cause_logs import diagnose, parse_cause_text

def stamp(hour,minute):
    return str(int(datetime(2026,11,18,hour,minute,tzinfo=timezone.utc).timestamp()*1000))

def record(kind, at, side="BEAR", extra=""):
    return (f"CISDCAUSE1|kind={kind}|symbol=FOREXCOM:GBPUSD|tf=15"
            f"|close_ms={at}|side={side}" + extra)

class CauseLogTests(unittest.TestCase):
    def test_pivot_latency_from_prior_known_break(self):
        row = record("V2_CONFIRM", stamp(7,30), extra=(
            "|v2_level=1.31889|v2_known_ms="+stamp(7,30)
            +"|pivot_known_this_close=true|previous_close_beyond_v2=true"
            +"|same_side_legacy_confirm=false|legacy_direction_pass=false"
            +"|legacy_level_pass=true|legacy_min_run_pass=true"
            +"|legacy_close_through_pass=true|legacy_age_pass=true|legacy_duplicate_pass=true"))
        rs, problems = parse_cause_text(row)
        self.assertFalse(problems)
        self.assertEqual(rs[0]["diagnostic"], "LEGACY_DIRECTION_FAILED")
        self.assertEqual(rs[0]["prior_break_before_pivot_known"], "true")

    def test_current_legacy_run_diagnostic_after_no_fire(self):
        row = record("V2_CONFIRM", stamp(7,30), extra=(
            "|same_side_legacy_confirm=false|legacy_direction_pass=true"
            "|legacy_level_pass=true|legacy_min_run_pass=false"
            "|legacy_close_through_pass=true|legacy_age_pass=true|legacy_duplicate_pass=true"))
        rs, _ = parse_cause_text(row)
        self.assertEqual(rs[0]["diagnostic"], "LEGACY_MIN_RUN_FAILED")

    def test_bearish_pivot_breach_must_match_side_and_level(self):
        a = record("LEGACY_CONFIRM", stamp(3,0), extra=(
            "|legacy_level=1.32042|nearest_v2_level=1.31998"
            "|nearest_v2_state=4|nearest_v2_reason=PIVOT_BREACH"
            "|nearest_v2_gap_ticks=44|nearest_v2_within_tol=false"))
        rs, _ = parse_cause_text(a)
        self.assertEqual(rs[0]["diagnostic"], "NO_NEAR_LEVEL_V2_CANDIDATE")
        b = a.replace("nearest_v2_gap_ticks=44|nearest_v2_within_tol=false",
                      "nearest_v2_gap_ticks=5|nearest_v2_within_tol=true")
        rs, _ = parse_cause_text(b)
        self.assertEqual(rs[0]["diagnostic"], "NEAR_TERMINAL_V2_CANDIDATE_NOT_PROOF")

    def test_native_date_message_escaping_replay_feed_and_dedup(self):
        record1=record("LEGACY_CONFIRM", stamp(7,15),
                       extra="|legacy_level=1.31889|nearest_v2_reason=NO_KNOWN_SAME_SIDE_CANDIDATE")
        record1=record1.replace(
            "symbol=FOREXCOM:GBPUSD",
            'symbol={"replay":"private-id","symbol":"FOREXCOM:GBPUSD"}'.replace("symbol={","symbol=={")
        )
        buffer=io.StringIO()
        wr=csv.DictWriter(buffer, fieldnames=["Date","Message"])
        wr.writeheader()
        wr.writerow({"Date":"2026-11-18T07:00:00+00:00","Message":record1})
        wr.writerow({"Date":"2026-11-18T07:00:00+00:00","Message":record1})
        rs, issues=parse_cause_text(buffer.getvalue())
        self.assertEqual(rs[0]["symbol"],"FOREXCOM:GBPUSD")
        self.assertEqual(rs[0]["diagnostic"],"NO_KNOWN_SAME_SIDE_V2_CANDIDATE")
        self.assertEqual(len(rs),1)
        self.assertEqual(len(issues),1)

    def test_missing_tag_rejected(self):
        with self.assertRaisesRegex(ValueError, "No valid"):
            parse_cause_text("Date,Message\n2026-11-18T07:00:00Z,hello")

    def test_same_side_confirm_reset_not_misclassified(self):
        row=record("V2_CONFIRM",stamp(7,45), extra=(
            "|v2_level=1.31911|same_side_legacy_confirm=true|legacy_run_state_reset=true"
            "|legacy_direction_pass=true|legacy_level_pass=false|legacy_min_run_pass=false"
        ))
        rs,_=parse_cause_text(row)
        self.assertEqual(rs[0]["diagnostic"],"SAME_SIDE_LEGACY_CONFIRM")

if __name__=="__main__":
    unittest.main()
