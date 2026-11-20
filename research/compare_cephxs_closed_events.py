#!/usr/bin/env python3
"""Compare independent, private Cephxs reference CLOSED events with Bandz logs.

This is event parity, NOT ground-truth trading accuracy. Same symbol, 15m
timeframe, same feed and identical historical range required. No automatic
mapping between FTMO and FOREXCOM levels.
"""
from __future__ import annotations
import argparse
import csv
import io
import json
import re
from datetime import datetime, timezone
from pathlib import Path

if __package__:
    from .parse_cisd_pine_logs import parse_logs as parse_bandz, as_events as bandz_events
else:
    from parse_cisd_pine_logs import parse_logs as parse_bandz, as_events as bandz_events

REF_PATTERN = re.compile(r"CEPHXSEVT1\|[^\r\n]+")
HEADERS = ["engine", "side", "category", "bandz_confirm_utc", "bandz_level",
           "cephxs_confirm_utc", "cephxs_level", "delta_minutes",
           "delta_ticks", "reference_pivot_bar", "reference_origin_bar"]


def parse_reference(text: str) -> list[dict[str, str]]:
    if not text.strip():
        raise ValueError("Empty Cephxs log export")
    first = text.lstrip("\ufeff\r\n ").splitlines()[0].replace(" ", "").lower()
    if first == "date,message":
        rdr = csv.DictReader(io.StringIO(text.lstrip("\ufeff")))
        if not {"Date", "Message"}.issubset(rdr.fieldnames or []):
            raise ValueError("Expected native Date,Message CSV")
        text = "\n".join(r.get("Message") or "" for r in rdr)
    out = []
    seen = set()
    for found in REF_PATTERN.finditer(text):
        row = {}
        for part in found.group(0).strip().split("|")[1:]:
            if "=" in part:
                key, value = part.split("=", 1)
                row[key] = value.strip()
        for key in ("kind","engine","symbol","tf","side","close_ms","level"):
            if not row.get(key):
                raise ValueError(f"Malformed CEPHXSEVT1 missing {key}")
        if row["kind"] != "CONFIRM" or row["engine"] != "CEPHXS" or row["side"] not in ("BULL","BEAR"):
            raise ValueError("Not a reference confirmation")
        symbol = row["symbol"]
        if symbol.startswith("={"):
            val = json.loads(symbol[1:])
            if not isinstance(val, dict) or not val.get("symbol"):
                raise ValueError("Unrecognized replay reference symbol")
            symbol = val["symbol"]
        row["symbol"] = symbol
        row["epoch"] = datetime.fromtimestamp(int(row["close_ms"])/1000, tz=timezone.utc)
        row["level_num"] = float(row["level"])
        token = (symbol,row["tf"],row["side"],row["close_ms"],row["level"],
                 row.get("pivot_bar",""),row.get("origin_bar",""))
        if token not in seen:
            out.append(row)
            seen.add(token)
    if not out:
        raise ValueError("No CEPHXSEVT1 confirmed rows found. Enable private reference logging.")
    if len({(r["symbol"], r["tf"]) for r in out}) > 1:
        raise ValueError("Mixed symbol/timeframe in Cephxs reference logs")
    return out


def compare_engines(bandz: list[dict], reference: list[dict], engine: str,
                    tick_size: float=.00001, exact_ticks: int=3,
                    near_ticks: int=20, minutes: int=15) -> list[dict]:
    b = [r for r in bandz if r["kind"]=="CONFIRM" and r["engine"]==engine]
    c = reference
    used_b,used_c = set(), set()
    result = []
    for phase in (0,1):
        for i,be in enumerate(b):
            if i in used_b:
                continue
            t = datetime.fromtimestamp(int(be["close_ms"])/1000,timezone.utc)
            choices=[]
            for j,ce in enumerate(c):
                if j in used_c or be["side"]!=ce["side"]:
                    continue
                mins = abs((ce["epoch"]-t).total_seconds())/60
                ticks = abs(float(be["level"])-ce["level_num"])/tick_size
                if (phase == 0 and mins < 1e-6) or (
                    phase == 1 and abs(mins-minutes) < 1e-6 and ticks <= near_ticks+1e-6):
                    choices.append((ticks,j))
            if not choices:
                continue
            ticks,j = min(choices)
            ce = c[j]
            category = "TIME_DIFF" if phase else ("EXACT" if ticks<=exact_ticks+1e-6 else "LEVEL_DIFF")
            result.append({
                "engine":engine,"side":be["side"],"category":category,
                "bandz_confirm_utc":t.isoformat(),"bandz_level":be["level"],
                "cephxs_confirm_utc":ce["epoch"].isoformat(),"cephxs_level":ce["level"],
                "delta_minutes":round((t-ce["epoch"]).total_seconds()/60,3),
                "delta_ticks":round(ticks,3),
                "reference_pivot_bar":ce.get("pivot_bar",""),
                "reference_origin_bar":ce.get("origin_bar","")
            })
            used_b.add(i);used_c.add(j)
    for i,be in enumerate(b):
        if i not in used_b:
            result.append({"engine":engine,"side":be["side"],"category":"BANDZ_ONLY",
                           "bandz_confirm_utc":datetime.fromtimestamp(int(be["close_ms"])/1000,timezone.utc).isoformat(),
                           "bandz_level":be["level"]})
    for j,ce in enumerate(c):
        if j not in used_c:
            result.append({"engine":engine,"side":ce["side"],"category":"CEPHXS_ONLY",
                           "cephxs_confirm_utc":ce["epoch"].isoformat(),"cephxs_level":ce["level"],
                           "reference_pivot_bar":ce.get("pivot_bar",""),
                           "reference_origin_bar":ce.get("origin_bar","")})
    return sorted(result,key=lambda r:(r.get("bandz_confirm_utc") or r.get("cephxs_confirm_utc"),r["engine"]))


def analyze(bandz_text: str, cephxs_text: str, start_utc: datetime, end_utc: datetime,
            tick_size: float=.00001) -> dict[str,list[dict]]:
    if start_utc.tzinfo is None or end_utc.tzinfo is None or start_utc >= end_utc:
        raise ValueError("An explicit valid UTC comparison window is required")
    bandz_rows,issues = parse_bandz(bandz_text)
    cephxs_rows = parse_reference(cephxs_text)
    feeds_a={(r["symbol"],r["tf"]) for r in bandz_rows}
    feeds_b={(r["symbol"],r["tf"]) for r in cephxs_rows}
    if feeds_a != feeds_b or len(feeds_a)!=1:
        raise ValueError(f"Mismatched feeds/timeframes: Bandz {feeds_a}; Cephxs {feeds_b}")
    if issues and any("Malformed" in msg for msg in issues):
        raise ValueError("Malformed Bandz log records: "+repr(issues))
    b=[r for r in bandz_rows if start_utc <=
       datetime.fromtimestamp(int(r["close_ms"])/1000,timezone.utc) < end_utc]
    c=[r for r in cephxs_rows if start_utc <= r["epoch"] < end_utc]
    if not b or not c:
        raise ValueError("Both engines need nonempty logs inside the common UTC window")
    return {engine:compare_engines(b,c,engine,tick_size=tick_size)
            for engine in ("V2","LEGACY")}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("bandz_pine_logs",type=Path)
    ap.add_argument("cephxs_pine_logs",type=Path)
    ap.add_argument("--from-utc",default="2026-11-17T00:00:00Z")
    ap.add_argument("--to-utc",default="2026-11-19T00:00:00Z")
    ap.add_argument("--tick-size",type=float,default=.00001)
    ap.add_argument("--output",type=Path,default=Path("CISD_Bandz_vs_Cephxs.csv"))
    args=ap.parse_args()
    beg=datetime.fromisoformat(args.from_utc.replace("Z","+00:00"))
    end=datetime.fromisoformat(args.to_utc.replace("Z","+00:00"))
    groups=analyze(args.bandz_pine_logs.read_text(encoding="utf-8-sig"),
                   args.cephxs_pine_logs.read_text(encoding="utf-8-sig"),
                   beg,end,tick_size=args.tick_size)
    with args.output.open("w",newline="",encoding="utf-8") as f:
        wr=csv.DictWriter(f,fieldnames=HEADERS,extrasaction="ignore")
        wr.writeheader()
        for engine,rows in groups.items():
            wr.writerows(rows)
            counts={kind:sum(r["category"]==kind for r in rows)
                    for kind in ("EXACT","TIME_DIFF","LEVEL_DIFF","BANDZ_ONLY","CEPHXS_ONLY")}
            print(engine,counts)
    print(f"Saved {args.output}; Cephxs parity is not ground-truth trading accuracy.")

if __name__=="__main__":
    main()
