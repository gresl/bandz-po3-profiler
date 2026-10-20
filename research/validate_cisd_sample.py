#!/usr/bin/env python3
"""Validate Phase C CISD research rows; stdlib only; never fills missing evidence."""
import argparse
import csv
from collections import Counter
from pathlib import Path

EXPECTED = (
    "event_key source_tickerid chart_tf po3_anchor_tf timezone "
    "confirm_close_time_ny direction confirm_bar_local confirm_close_price "
    "atr14_at_confirm cisd_level source_commit_sha settings_profile "
    "c2_linked_then c1_swept_then c2_closed_then body_range_pct_then "
    "body_atr14_then directional_close_pct_then aligned_fvg_known_then "
    "aligned_fvg_born_time_then killzone_then audit_eligible_at_close "
    "audit_consistency technical_review_label technical_review_reason "
    "technical_review_blinded later_c2_close_time later_aligned_fvg_time "
    "later_cisd_invalidation_time outcome_16_status mfe_atr_16 mae_atr_16 "
    "terminal_atr_16 first_hit_1atr_16 outcome_32_status mfe_atr_32 "
    "mae_atr_32 terminal_atr_32 first_hit_1atr_32 notes"
).split()

KEY_FIELDS = (
    "source_tickerid", "chart_tf", "po3_anchor_tf", "timezone",
    "confirm_close_time_ny", "direction", "source_commit_sha", "settings_profile"
)
NUMBER_FIELDS = (
    "confirm_close_price", "atr14_at_confirm", "cisd_level",
    "body_range_pct_then", "body_atr14_then", "directional_close_pct_then",
    "mfe_atr_16", "mae_atr_16", "terminal_atr_16",
    "mfe_atr_32", "mae_atr_32", "terminal_atr_32",
)
FINAL_FIELDS = {
    16: ("mfe_atr_16", "mae_atr_16", "terminal_atr_16", "first_hit_1atr_16"),
    32: ("mfe_atr_32", "mae_atr_32", "terminal_atr_32", "first_hit_1atr_32"),
}


def check(path: Path):
    errors, warnings = [], []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        headers = reader.fieldnames or []
        if headers != EXPECTED:
            errors.append("CSV header differs from canonical research/cisd_phase_c_sample.csv")
            errors.append("Missing: " + ", ".join(sorted(set(EXPECTED) - set(headers))))
            errors.append("Unexpected: " + ", ".join(sorted(set(headers) - set(EXPECTED))))
            return [], errors, warnings
        rows = list(reader)

    seen, previous = set(), None
    for line, raw in enumerate(rows, start=2):
        r = {k: (v or "").strip() for k, v in raw.items() if k is not None}
        tag = f"line {line} ({r.get('event_key') or 'missing event_key'})"
        if None in raw:
            errors.append(f"{tag}: extra CSV cells")
        if not r["event_key"]:
            errors.append(f"{tag}: missing event_key")
        identity = tuple(r[k] for k in KEY_FIELDS)
        if any(not value for value in identity):
            errors.append(f"{tag}: missing immutable identity fields")
        compound = (r["event_key"], identity)
        if compound in seen:
            errors.append(f"{tag}: duplicate event key + identity")
        seen.add(compound)
        if r["direction"].lower() not in {"bull", "bear", "bullish", "bearish"}:
            errors.append(f"{tag}: unexpected direction")
        label = r["technical_review_label"].lower()
        if label not in {"valid", "invalid", "uncertain"}:
            warnings.append(f"{tag}: technical_review_label must be valid/invalid/uncertain")
        if label and not r["technical_review_reason"]:
            warnings.append(f"{tag}: manual review reason missing")
        if r["technical_review_blinded"].lower() not in {"yes", "no"}:
            warnings.append(f"{tag}: blinded review must explicitly be yes or no")
        if r["audit_consistency"].upper() != "MATCH":
            warnings.append(f"{tag}: audit_consistency is not MATCH")
        if r["aligned_fvg_known_then"].lower() in {"yes", "true", "pass"} and not r["aligned_fvg_born_time_then"]:
            warnings.append(f"{tag}: FVG known at confirmation but no born time (missing evidence)")
        for col in NUMBER_FIELDS:
            value = r[col]
            if value and value.lower() not in {"unknown", "n/a", "na", "not_evaluable"}:
                try:
                    float(value)
                except ValueError:
                    errors.append(f"{tag}: {col} is not numeric")
        for horizon, fields in FINAL_FIELDS.items():
            status = r[f"outcome_{horizon}_status"].upper()
            if status and status not in {"FINAL", "PARTIAL", "CENSORED", "NOT_EVALUABLE"}:
                warnings.append(f"{tag}: unexpected {horizon}-bar horizon status: {status}")
            if status == "FINAL" and any(not r[f] for f in fields):
                warnings.append(f"{tag}: {horizon}-bar FINAL with missing measurements/hit classification")
            if status != "FINAL" and r[f"terminal_atr_{horizon}"]:
                warnings.append(f"{tag}: {horizon}-bar terminal present without FINAL; check censoring")
        # Sequential capture is defined by Replay order, not by row sorting.
        sort_key = (r["source_tickerid"], r["confirm_close_time_ny"])
        if previous and sort_key[0] == previous[0] and sort_key[1] < previous[1]:
            warnings.append(f"{tag}: timestamp precedes earlier row of same feed; confirm consecutive Replay order")
        previous = sort_key
    return rows, errors, warnings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csvfile", nargs="?", default=str(Path(__file__).with_name("cisd_phase_c_sample.csv")))
    args = parser.parse_args()
    path = Path(args.csvfile)
    rows, errors, warnings = check(path)
    print(f"Phase C rows: {len(rows)} (target: 30-50 consecutive raw CISDs per cohort)")
    print("Technical review:", dict(Counter(r["technical_review_label"].lower() or "missing" for r in rows)))
    print("Blinded review:", dict(Counter(r["technical_review_blinded"].lower() or "missing" for r in rows)))
    for horizon in (16, 32):
        print(f"{horizon}-bar status:", dict(Counter(r[f"outcome_{horizon}_status"].upper() or "MISSING" for r in rows)))
    for line in errors:
        print("ERROR:", line)
    for line in warnings:
        print("WARN:", line)
    print(f"Errors: {len(errors)} | Warnings: {len(warnings)}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
