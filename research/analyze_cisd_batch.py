#!/usr/bin/env python3
"""Parse TradingView 4E CISD Data Window CSV into per-close events and comparisons.

This is a mechanical comparison of Bandz LEGACY and V2, NOT Cephxs signals or
trade performance. One V2 confirmation per direction per bar is exported.
Any same-bar multiple-event count > 1 is flagged as ambiguous.
"""
from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo


FIELDS = {
    "v2_bull": "CISDEXP_V2_BULL_LEVEL",
    "v2_bear": "CISDEXP_V2_BEAR_LEVEL",
    "legacy_bull": "CISDEXP_LEGACY_BULL_LEVEL",
    "legacy_bear": "CISDEXP_LEGACY_BEAR_LEVEL",
    "v2_bull_atr": "CISDEXP_V2_BULL_STRETCH_ATR",
    "v2_bear_atr": "CISDEXP_V2_BEAR_STRETCH_ATR",
    "v2_bull_pivot": "CISDEXP_V2_BULL_PIVOT_BAR",
    "v2_bear_pivot": "CISDEXP_V2_BEAR_PIVOT_BAR",
    "v2_bull_count": "CISDEXP_V2_BULL_COUNT",
    "v2_bear_count": "CISDEXP_V2_BEAR_COUNT",
}


@dataclass(frozen=True)
class Event:
    confirm_utc: datetime
    source: str
    direction: str
    level: float
    stretch_atr: float | None = None
    pivot_bar: int | None = None
    candidate_count: int = 1


@dataclass(frozen=True)
class Comparison:
    category: str
    v2: Event | None
    legacy: Event | None


def _number(value: str | None) -> float | None:
    if value is None or not value.strip() or value.strip().lower() in ("na", "nan", "null"):
        return None
    return float(value.strip())


def _timestamp(value: str, default_timezone: str) -> datetime:
    val = value.strip()
    try:
        number = float(val)
    except ValueError:
        d = datetime.fromisoformat(val.replace("Z", "+00:00"))
    else:
        d = datetime.fromtimestamp(number / 1000 if abs(number) > 1e11 else number, tz=timezone.utc)
    if d.tzinfo is None:
        d = d.replace(tzinfo=ZoneInfo(default_timezone))
    return d.astimezone(timezone.utc)


def parse_export(path: str | Path, *, timeframe_minutes: int = 15,
                 source_timezone: str = "UTC", timestamp_is_close: bool = False) -> tuple[list[Event], list[str]]:
    events: list[Event] = []
    warnings: list[str] = []
    with open(path, newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        columns = reader.fieldnames or []
        actual: dict[str, str] = {}
        for name, suffix in FIELDS.items():
            hits = [col for col in columns if suffix in col.upper()]
            if len(hits) != 1:
                if name in ("v2_bull", "v2_bear", "legacy_bull", "legacy_bear"):
                    raise ValueError(f"Expected ONE {suffix} column, found {len(hits)}. Verify active 4E export plots.")
            else:
                actual[name] = hits[0]
        ts_col = next((col for col in columns if col.strip().lower() in
                       ("time", "date", "datetime", "timestamp")), None)
        if ts_col is None:
            raise ValueError("No Time column in CSV. Choose TradingView chart-data export, not trade-list export.")
        for row_idx, row in enumerate(reader, 2):
            raw = (row.get(ts_col) or "").strip()
            if not raw:
                continue
            bar_time = _timestamp(raw, source_timezone)
            closed_time = bar_time if timestamp_is_close else bar_time + timedelta(minutes=timeframe_minutes)
            for provider in ("V2", "LEGACY"):
                for side in ("BULL", "BEAR"):
                    prefix = provider.lower() + "_" + side.lower()
                    level = _number(row.get(actual[prefix]))
                    if level is None:
                        continue
                    atr = _number(row.get(actual.get(prefix + "_atr"))) if prefix + "_atr" in actual else None
                    pb = _number(row.get(actual.get(prefix + "_pivot"))) if prefix + "_pivot" in actual else None
                    count = _number(row.get(actual.get(prefix + "_count"))) if prefix + "_count" in actual else None
                    n = int(count) if count is not None else 1
                    if n > 1:
                        warnings.append(f"Row {row_idx}: {provider} {side} confirms {n} candidates on one bar;"
                                        " CSV includes only first level — classification may be incomplete.")
                    events.append(Event(closed_time, provider, side, level,
                                        atr if provider == "V2" else None,
                                        int(pb) if pb is not None and provider == "V2" else None, n))
    return sorted(events, key=lambda e: (e.confirm_utc, e.source, e.direction)), warnings


def compare(events: list[Event], *, timeframe_minutes: int = 15, tick_size: float = 0.00001,
            same_level_ticks: int = 3, near_level_ticks: int = 20) -> list[Comparison]:
    v = [e for e in events if e.source == "V2"]
    l = [e for e in events if e.source == "LEGACY"]
    used_v: set[int] = set()
    used_l: set[int] = set()
    out: list[Comparison] = []
    # Exact close before adjacent-bar matches. Same side; closest level wins.
    for phase in (0, 1):
        for i, ve in enumerate(v):
            if i in used_v:
                continue
            choices: list[tuple[float, int]] = []
            for j, le in enumerate(l):
                if j in used_l or le.direction != ve.direction:
                    continue
                bars_apart = abs((ve.confirm_utc - le.confirm_utc).total_seconds()) / (timeframe_minutes * 60)
                price_ticks = abs(ve.level - le.level) / tick_size
                if (phase == 0 and bars_apart < 1e-6 or
                    phase == 1 and abs(bars_apart - 1.0) < 1e-6 and price_ticks <= near_level_ticks + 1e-6):
                    choices.append((price_ticks, j))
            if choices:
                _, j = min(choices)
                le = l[j]
                category = ("TIME_DIFF" if phase else
                            "EXACT" if abs(ve.level - le.level) / tick_size <= same_level_ticks + 1e-6
                            else "LEVEL_DIFF")
                out.append(Comparison(category, ve, le))
                used_v.add(i)
                used_l.add(j)
    out.extend(Comparison("V2_ONLY", e, None) for i, e in enumerate(v) if i not in used_v)
    out.extend(Comparison("LEGACY_ONLY", None, e) for j, e in enumerate(l) if j not in used_l)
    return sorted(out, key=lambda x: (x.v2 or x.legacy).confirm_utc)


def _ts(ev: Event | None) -> str:
    return ev.confirm_utc.strftime("%Y-%m-%d %H:%M:%S UTC") if ev else ""


def save_report(path: str | Path, comparisons: list[Comparison]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=[
            "classification", "direction", "v2_confirm_utc", "v2_level", "v2_stretch_atr",
            "v2_pivot_bar", "legacy_confirm_utc", "legacy_level", "count_ambiguous"])
        writer.writeheader()
        for c in comparisons:
            ev = c.v2 or c.legacy
            writer.writerow({
                "classification": c.category,
                "direction": ev.direction,
                "v2_confirm_utc": _ts(c.v2),
                "v2_level": c.v2.level if c.v2 else "",
                "v2_stretch_atr": c.v2.stretch_atr if c.v2 else "",
                "v2_pivot_bar": c.v2.pivot_bar if c.v2 else "",
                "legacy_confirm_utc": _ts(c.legacy),
                "legacy_level": c.legacy.level if c.legacy else "",
                "count_ambiguous": int(any(e.candidate_count > 1 for e in (c.v2, c.legacy) if e)),
            })


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("csv_path", help="TradingView Export chart data CSV with 4E enabled")
    ap.add_argument("--timeframe-minutes", type=int, default=15)
    ap.add_argument("--source-timezone", default="UTC", help="Timezone for naive date columns, default UTC")
    ap.add_argument("--timestamp-is-close", action="store_true", help="Use when input CSV times are candle closes, not opens")
    ap.add_argument("--tick-size", type=float, default=0.00001)
    ap.add_argument("--same-level-ticks", type=int, default=3)
    ap.add_argument("--near-level-ticks", type=int, default=20)
    ap.add_argument("--output", help="Result CSV path; default <input>.cisd-comparison.csv")
    args = ap.parse_args()
    events, warnings = parse_export(args.csv_path, timeframe_minutes=args.timeframe_minutes,
                                    source_timezone=args.source_timezone,
                                    timestamp_is_close=args.timestamp_is_close)
    rows = compare(events, timeframe_minutes=args.timeframe_minutes, tick_size=args.tick_size,
                   same_level_ticks=args.same_level_ticks, near_level_ticks=args.near_level_ticks)
    dest = args.output or str(Path(args.csv_path).with_suffix("")) + ".cisd-comparison.csv"
    save_report(dest, rows)
    counts: dict[str, int] = {}
    for c in rows:
        counts[c.category] = counts.get(c.category, 0) + 1
    print(f"Events: {len(events)}; classified event-pairs: {len(rows)}; {counts}; CSV: {dest}")
    for warning in warnings:
        print("WARNING:", warning)
    if warnings:
        print("WARNING: Compare single-bar collisions independently; this CSV alone is not complete ground truth.")


if __name__ == "__main__":
    main()
