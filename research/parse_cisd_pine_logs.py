#!/usr/bin/env python3
"""Parse raw TradingView Pine Logs CISDEVT1 lines into event and comparison CSVs.

Historical time labels added by TradingView identify the opening bar; this
parser explicitly trusts ONLY our embedded close_ms (UTC UNIX milliseconds).
It never applies FTMO OHLC to FOREXCOM levels, and never treats Cephxs as a
source of these events.
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
    from .analyze_cisd_batch import Event, compare, save_report
else:
    from analyze_cisd_batch import Event, compare, save_report

TAG = "CISDEVT1|"
LINE = re.compile(r"CISDEVT1\|[^\r\n]+")
OHLC = ("o", "h", "l", "c")
HEADERS = [
    "kind", "engine", "symbol", "tf", "side", "close_ms", "close_utc", "level",
    "bar", "o", "h", "l", "c", "opposing_first", "known_ms", "pivot_bar",
    "stretch_atr", "state", "reason", "raw_line",
]

def _parse_line(text: str) -> dict[str, str]:
    parts = text.split("|")
    if parts[0] != "CISDEVT1":
        raise ValueError("Not CISDEVT1")
    data = {}
    for item in parts[1:]:
        if "=" not in item:
            continue
        k, v = item.split("=", 1)
        data[k] = v.strip()
    for name in ("kind", "engine", "symbol", "tf", "side", "close_ms", "level"):
        if not data.get(name):
            raise ValueError(f"Missing {name}")
    if data["engine"] not in ("LEGACY", "V2"):
        raise ValueError("Unknown engine")
    if data["kind"] not in ("CONFIRM", "LIFECYCLE"):
        raise ValueError("Unknown kind")
    if data["side"] not in ("BULL", "BEAR"):
        raise ValueError("Unknown side")
    # In TradingView Bar Replay, syminfo.tickerid can be serialized as an
    # internal replay envelope rather than the underlying exchange ticker.
    # Canonicalize for feed matching; do not publish internal replay IDs.
    if data["symbol"].startswith("={"):
        try:
            replay = json.loads(data["symbol"][1:])
        except json.JSONDecodeError as exc:
            raise ValueError("Unrecognized replay symbol envelope") from exc
        ticker = replay.get("symbol") if isinstance(replay, dict) else None
        if not isinstance(ticker, str) or not ticker:
            raise ValueError("Replay envelope missing underlying symbol")
        data["symbol"] = ticker
    close_utc = datetime.fromtimestamp(int(data["close_ms"]) / 1000, timezone.utc)
    data["close_utc"] = close_utc.isoformat()
    data["raw_line"] = text
    return data

def parse_logs(text: str) -> tuple[list[dict[str, str]], list[str]]:
    # TradingView's Pine Logs panel exports a two-column Date,Message CSV.
    # Parse that format as CSV first so quoted replay-symbol JSON survives
    # double-quote escaping. Pasted plain logs remain supported.
    first = text.lstrip("\\ufeff\\r\\n ").splitlines()[0] if text.strip() else ""
    if first.replace(" ", "").lower() == "date,message":
        reader = csv.DictReader(io.StringIO(text.lstrip("\\ufeff")))
        if not {"Date", "Message"}.issubset(reader.fieldnames or []):
            raise ValueError("Pine Logs CSV needs Date and Message columns")
        text = "\\n".join((row.get("Message") or "") for row in reader)
    rows: list[dict[str, str]] = []
    notes: list[str] = []
    seen: set[tuple[str, ...]] = set()
    for idx, match in enumerate(LINE.finditer(text), 1):
        raw = match.group(0).strip()
        try:
            data = _parse_line(raw)
            # Different V2 candidates may have identical close/price. Retain
            # distinct pivot and birth records, suppress pasted duplicate lines.
            key = (data["kind"], data["engine"], data["symbol"], data["tf"],
                   data["side"], data["close_ms"], data["level"],
                   data.get("pivot_bar", ""), data.get("known_ms", ""),
                   data.get("reason", ""))
            if key not in seen:
                rows.append(data)
                seen.add(key)
            else:
                notes.append(f"Duplicate event line {idx} suppressed")
        except (ValueError, OverflowError) as err:
            notes.append(f"Malformed tagged record {idx}: {err}")
    if not rows:
        raise ValueError("No valid CISDEVT1 lines found. In Pine Logs, filter for CISDEVT1.")
    feeds = {(r["symbol"], r["tf"]) for r in rows}
    if len(feeds) > 1:
        raise ValueError(f"Mixed symbols/timeframes cannot be compared in one batch: {sorted(feeds)}")
    return rows, notes


def as_events(rows: list[dict[str, str]]) -> list[Event]:
    out: list[Event] = []
    for r in rows:
        if r["kind"] != "CONFIRM":
            continue
        at = datetime.fromtimestamp(int(r["close_ms"])/1000, tz=timezone.utc)
        stretch = r.get("stretch_atr", "")
        pivot = r.get("pivot_bar", "")
        out.append(Event(at, r["engine"], r["side"], float(r["level"]),
                         float(stretch) if stretch and stretch != "NaN" else None,
                         int(pivot) if pivot and pivot != "NaN" else None))
    return out


def save_events(path: str | Path, rows: list[dict[str, str]]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as out:
        writer = csv.DictWriter(out, fieldnames=HEADERS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("logs_text", type=Path, help="Pine Logs Date,Message CSV or pasted log text; only CISDEVT1 records parsed")
    ap.add_argument("--output-prefix", type=Path, help="Default same path without suffix")
    ap.add_argument("--timeframe-minutes", type=int, default=15)
    ap.add_argument("--tick-size", type=float, default=0.00001)
    ap.add_argument("--same-level-ticks", type=int, default=3)
    ap.add_argument("--near-level-ticks", type=int, default=20)
    args = ap.parse_args()
    rows, notes = parse_logs(args.logs_text.read_text(encoding="utf-8-sig"))
    out = args.output_prefix or args.logs_text.with_suffix("")
    event_path = Path(str(out) + ".events.csv")
    cmp_path = Path(str(out) + ".compared.csv")
    save_events(event_path, rows)
    classified = compare(as_events(rows), timeframe_minutes=args.timeframe_minutes,
                         tick_size=args.tick_size,
                         same_level_ticks=args.same_level_ticks,
                         near_level_ticks=args.near_level_ticks)
    save_report(cmp_path, classified)
    print(f"Captured {len(rows)} event/lifecycle records and {len(classified)} comparisons")
    print(f"Events: {event_path}\nComparisons: {cmp_path}")
    for kind in ("EXACT", "TIME_DIFF", "LEVEL_DIFF", "V2_ONLY", "LEGACY_ONLY"):
        print(f"{kind}: {sum(c.category == kind for c in classified)}")
    print(f"Lifecycle rows (not confirmations): {sum(r['kind'] == 'LIFECYCLE' for r in rows)}")
    for note in notes:
        print("NOTICE:", note)
    print("WARNING: This is Bandz V2 vs Bandz legacy, NOT Cephxs or FTMO feed parity.")

if __name__ == "__main__":
    main()
