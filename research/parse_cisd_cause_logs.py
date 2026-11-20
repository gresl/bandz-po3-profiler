#!/usr/bin/env python3
"""Parse opt-in CISDCAUSE1 evidence from TradingView Essential Pine Logs exports.

Only confirmed-close predicate snapshots. Never treat nearest lifecycle
events as proof that they caused a missed CISD. No Cephxs or trade label.
"""
from __future__ import annotations
import argparse
import csv
import io
import json
import re
from datetime import datetime, timezone
from pathlib import Path

TAG = "CISDCAUSE1|"
P = re.compile(r"CISDCAUSE1\|[^\r\n]+")
BOOL = {"true": True, "false": False}
BASE = ["kind", "symbol", "tf", "close_ms", "close_utc", "side"]
V2 = ["v2_level", "v2_known_ms", "v2_pivot_bar", "pivot_known_this_close",
      "previous_close_beyond_v2", "same_side_legacy_confirm", "legacy_run_state_reset",
      "legacy_run_len", "legacy_min_run", "legacy_run_start_bar", "legacy_selected_level",
      "legacy_direction_pass", "legacy_level_pass", "legacy_min_run_pass",
      "legacy_close_through_pass", "legacy_age_pass", "legacy_duplicate_pass"]
LEG = ["legacy_level", "legacy_start_bar", "nearest_v2_level", "nearest_v2_state",
       "nearest_v2_reason", "nearest_v2_known_ms", "nearest_v2_gap_ticks",
       "nearest_v2_within_tol"]
FIELDS = BASE + V2 + LEG + ["diagnostic", "prior_break_before_pivot_known", "raw_line"]


def canonical_symbol(symbol: str) -> str:
    if symbol.startswith("={"):
        data = json.loads(symbol[1:])
        if not isinstance(data, dict) or not isinstance(data.get("symbol"), str):
            raise ValueError("Replay envelope lacks an underlying symbol")
        return data["symbol"]
    return symbol


def parse_cause_text(text: str) -> tuple[list[dict[str, str]], list[str]]:
    if not text.strip():
        raise ValueError("Empty Pine Logs export")
    first = text.lstrip("\ufeff\r\n ").splitlines()[0].replace(" ", "").lower()
    if first == "date,message":
        lines = csv.DictReader(io.StringIO(text.lstrip("\ufeff")))
        if not {"Date", "Message"}.issubset(lines.fieldnames or []):
            raise ValueError("Unexpected Pine Logs headers")
        text = "\n".join((r.get("Message") or "") for r in lines)
    output: list[dict[str, str]] = []
    seen: set[tuple[str, ...]] = set()
    issues: list[str] = []
    for i, match in enumerate(P.finditer(text), 1):
        raw = match.group(0).strip()
        try:
            row = {}
            for part in raw.split("|")[1:]:
                if "=" in part:
                    key, value = part.split("=", 1)
                    row[key] = value.strip()
            for field in BASE[:4] + ["side"]:
                if not row.get(field):
                    raise ValueError(f"missing {field}")
            if row["kind"] not in ("V2_CONFIRM", "LEGACY_CONFIRM"):
                raise ValueError("unknown kind")
            if row["side"] not in ("BULL", "BEAR"):
                raise ValueError("unknown side")
            row["symbol"] = canonical_symbol(row["symbol"])
            row["close_utc"] = datetime.fromtimestamp(
                int(row["close_ms"]) / 1000, timezone.utc).isoformat()
            key = (row["symbol"], row["tf"], row["close_ms"], row["kind"],
                   row["side"], row.get("v2_level", ""), row.get("legacy_level", ""))
            if key in seen:
                issues.append(f"Duplicate cause row {i} ignored")
                continue
            seen.add(key)
            row["prior_break_before_pivot_known"] = (
                "true" if row["kind"] == "V2_CONFIRM"
                and row.get("pivot_known_this_close") == "true"
                and row.get("previous_close_beyond_v2") == "true"
                else "false"
            )
            row["diagnostic"] = diagnose(row)
            row["raw_line"] = raw
            output.append(row)
        except (ValueError, OverflowError, json.JSONDecodeError) as exc:
            issues.append(f"Malformed cause row {i}: {exc}")
    if not output:
        raise ValueError("No valid CISDCAUSE1 records found. Enable both 4F and 4G.")
    feed_set = {(r["symbol"], r["tf"]) for r in output}
    if len(feed_set) > 1:
        raise ValueError(f"Mixed feed/timeframe in one export: {feed_set}")
    return output, issues


def diagnose(row: dict[str, str]) -> str:
    if row["kind"] == "LEGACY_CONFIRM":
        reason = row.get("nearest_v2_reason", "")
        if reason == "NO_KNOWN_SAME_SIDE_CANDIDATE":
            return "NO_KNOWN_SAME_SIDE_V2_CANDIDATE"
        if row.get("nearest_v2_within_tol") != "true":
            return "NO_NEAR_LEVEL_V2_CANDIDATE"
        if reason in ("PIVOT_BREACH", "EXPIRED", "SUPERSEDED"):
            # Proximity alone does not prove that this was the causative V2 event.
            return "NEAR_TERMINAL_V2_CANDIDATE_NOT_PROOF"
        if reason == "PENDING":
            return "NEAR_V2_PENDING"
        if reason in ("CONFIRMED", "INVALID_AFTER_CONFIRM"):
            return "NEAR_V2_CONFIRMED_OR_INVALIDATED"
        return "NEAR_V2_UNCLASSIFIED"
    if row.get("same_side_legacy_confirm") == "true":
        return "SAME_SIDE_LEGACY_CONFIRM"
    gates = [
        ("legacy_direction_pass", "LEGACY_DIRECTION_FAILED"),
        ("legacy_level_pass", "LEGACY_LEVEL_UNAVAILABLE"),
        ("legacy_min_run_pass", "LEGACY_MIN_RUN_FAILED"),
        ("legacy_close_through_pass", "LEGACY_CLOSE_THROUGH_FAILED"),
        ("legacy_age_pass", "LEGACY_RUN_EXPIRED"),
        ("legacy_duplicate_pass", "LEGACY_DUPLICATE_GUARD"),
    ]
    for field, name in gates:
        if row.get(field) == "false":
            return name
    return "NO_FAILED_GATE_IN_SNAPSHOT_REQUIRES_SOURCE_AUDIT"


def save(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as file:
        wr = csv.DictWriter(file, fieldnames=FIELDS, extrasaction="ignore")
        wr.writeheader()
        wr.writerows(rows)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("log_csv_or_text", type=Path)
    ap.add_argument("--output", type=Path, default=None)
    args = ap.parse_args()
    rows, issues = parse_cause_text(args.log_csv_or_text.read_text(encoding="utf-8-sig"))
    out = args.output or args.log_csv_or_text.with_suffix(".cause.csv")
    save(out, rows)
    print(f"{len(rows)} causal snapshots written to {out}")
    counts: dict[str, int] = {}
    for r in rows:
        counts[r["diagnostic"]] = counts.get(r["diagnostic"], 0) + 1
    for name, count in sorted(counts.items()):
        print(f"{name}: {count}")
    for note in issues:
        print("WARNING:", note)
    print("This report is observational; a nearby terminal candidate is not causal proof.")


if __name__ == "__main__":
    main()
