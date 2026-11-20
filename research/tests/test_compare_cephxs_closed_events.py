import csv
import io
import unittest
from datetime import datetime,timezone
from research.compare_cephxs_closed_events import parse_reference, analyze

def epoch(day,hour,minute):
    return str(int(datetime(2026,11,day,hour,minute,tzinfo=timezone.utc).timestamp()*1000))

def emit(tag,engine,day,hour,minute,level,side="BEAR",symbol="FOREXCOM:GBPUSD"):
    return (f"{tag}|kind=CONFIRM|engine={engine}|symbol={symbol}"
            f"|tf=15|side={side}|close_ms={epoch(day,hour,minute)}"
            f"|level={level}|pivot_bar=11748|origin_bar=11745")

class ReferenceComparatorTests(unittest.TestCase):
    def test_timing_from_real_case_synthetic_reference(self):
        v=emit("CISDEVT1","V2",18,7,30,"1.31889")
        l=emit("CISDEVT1","LEGACY",18,7,15,"1.31889")
        c=emit("CEPHXSEVT1","CEPHXS",18,7,15,"1.31889")
        start=datetime(2026,11,18,0,tzinfo=timezone.utc)
        end=datetime(2026,11,19,0,tzinfo=timezone.utc)
        result=analyze(v+"\n"+l,c,start,end)
        self.assertEqual(result["V2"][0]["category"],"TIME_DIFF")
        self.assertEqual(result["V2"][0]["delta_minutes"],15)
        self.assertEqual(result["LEGACY"][0]["category"],"EXACT")

    def test_level_and_orphans_not_marked_accuracy(self):
        b=emit("CISDEVT1","V2",17,7,45,"1.31911")
        c=emit("CEPHXSEVT1","CEPHXS",17,7,45,"1.31926")
        c2=emit("CEPHXSEVT1","CEPHXS",17,8,15,"1.31870")
        start=datetime(2026,11,17,0,tzinfo=timezone.utc)
        end=datetime(2026,11,18,0,tzinfo=timezone.utc)
        result=analyze(b,c+"\n"+c2,start,end)
        self.assertEqual({x["category"] for x in result["V2"]},{"LEVEL_DIFF","CEPHXS_ONLY"})
        self.assertEqual(len(result["LEGACY"]),2)
        self.assertTrue(all(x["category"]=="CEPHXS_ONLY" for x in result["LEGACY"]))

    def test_native_date_message_and_replay_envelope(self):
        line=emit("CEPHXSEVT1","CEPHXS",17,7,45,"1.31926",
                  symbol='={"replay":"opaque-private-id","symbol":"FOREXCOM:GBPUSD"}')
        buffer=io.StringIO()
        w=csv.DictWriter(buffer,fieldnames=["Date","Message"])
        w.writeheader()
        w.writerow({"Date":"2026-11-17T07:30:00+00:00","Message":line})
        rows=parse_reference(buffer.getvalue())
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]["symbol"],"FOREXCOM:GBPUSD")

    def test_mismatched_feeds_rejected(self):
        b=emit("CISDEVT1","V2",17,7,45,"1.31911")
        c=emit("CEPHXSEVT1","CEPHXS",17,7,45,"1.31911",symbol="OANDA:GBPUSD")
        start=datetime(2026,11,17,0,tzinfo=timezone.utc)
        end=datetime(2026,11,18,0,tzinfo=timezone.utc)
        with self.assertRaisesRegex(ValueError,"Mismatched feeds"):
            analyze(b,c,start,end)

    def test_no_cephxs_records_rejected(self):
        with self.assertRaisesRegex(ValueError,"No CEPHXSEVT1"):
            parse_reference("empty logs")

if __name__ == "__main__":
    unittest.main()
