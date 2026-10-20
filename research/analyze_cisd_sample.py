#!/usr/bin/env python3
"""Descriptive Phase C CISD cohort report. No signal tuning, backtest, or trade P&L."""

import argparse
import json
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path

from validate_cisd_sample import check

# Frozen Phase B hypotheses. These are NOT calibrated by this script.
BODY_RANGE_MIN = 55.0
BODY_ATR_MIN = 0.60
DIRECTIONAL_CLOSE_MIN = 70.0

COHORT_KEYS = (
    "source_tickerid", "chart_tf", "po3_anchor_tf",
    "timezone", "source_commit_sha", "settings_profile",
)
GROUPS = (
    "raw",
    "c2_linked",
    "c1_swept",
    "c2_closed_then",
    "displacement",
    "aligned_fvg",
    "c2_displacement_fvg",
    "audit_eligible",
)
TRUE_VALUES = {"yes", "true", "pass", "1"}
FALSE_VALUES = {"no", "false", "fail", "0"}
HITS = {
    "f first": "favorable_first",
    "f only": "favorable_first",
    "a first": "adverse_first",
    "a only": "adverse_first",
    "ambiguous same bar": "ambiguous_same_bar",
    "none": "no_hit",
}


def flag(value):
    value = (value or "").strip().lower()
    if value in TRUE_VALUES:
        return True
    if value in FALSE_VALUES:
        return False
    return None


def number(value):
    value = (value or "").strip()
    if not value or value.lower() in {"unknown", "n/a", "na", "not_evaluable"}:
        return None
    try:
        result = float(value)
    except ValueError:
        return None
    return result if math.isfinite(result) else None


def all_three(a, b, c):
    """Unknown stays unknown unless an already-known requirement fails."""
    flags = (a, b, c)
    if any(x is False for x in flags):
        return False
    if all(x is True for x in flags):
        return True
    return None


def displacement(row):
    comparisons = (
        ("body_range_pct_then", BODY_RANGE_MIN),
        ("body_atr14_then", BODY_ATR_MIN),
        ("directional_close_pct_then", DIRECTIONAL_CLOSE_MIN),
    )
    values = []
    for field, minimum in comparisons:
        observed = number(row.get(field))
        values.append(None if observed is None else observed >= minimum)
    return all_three(*values)


def memberships(row):
    c2 = flag(row.get("c2_linked_then"))
    fvg = flag(row.get("aligned_fvg_known_then"))
    # A claimed known FVG without its formation timestamp is unverified evidence.
    if fvg is True and not (row.get("aligned_fvg_born_time_then") or "").strip():
        fvg = None
    disp = displacement(row)
    return {
        "raw": True,
        "c2_linked": c2,
        "c1_swept": flag(row.get("c1_swept_then")),
        "c2_closed_then": flag(row.get("c2_closed_then")),
        "displacement": disp,
        "aligned_fvg": fvg,
        "c2_displacement_fvg": all_three(c2, disp, fvg),
        "audit_eligible": flag(row.get("audit_eligible_at_close")),
    }


def percentiles(values):
    """Descriptive linear-interpolation quartiles; no confidence intervals."""
    if not values:
        return {"n": 0, "p25": None, "median": None, "p75": None}
    ordered = sorted(values)

    def pct(fraction):
        i = (len(ordered) - 1) * fraction
        lo = math.floor(i)
        hi = math.ceil(i)
        return round(ordered[lo] + (ordered[hi] - ordered[lo]) * (i - lo), 4)

    return {
        "n": len(values),
        "p25": pct(0.25),
        "median": round(statistics.median(ordered), 4),
        "p75": pct(0.75),
    }


def outcomes(rows, horizon):
    status_field = "outcome_%s_status" % horizon
    prefix = ("mfe_atr_", "mae_atr_", "terminal_atr_")
    statuses = Counter((r.get(status_field) or "MISSING").upper() for r in rows)
    final = [r for r in rows if (r.get(status_field) or "").upper() == "FINAL"]
    metrics = {
        p[:-1]: percentiles([v for r in final if (v := number(r.get(p + str(horizon)))) is not None])
        for p in prefix
    }
    hit_counts = Counter()
    for row in final:
        hit = (row.get("first_hit_1atr_%s" % horizon) or "").strip().lower()
        hit_counts[HITS.get(hit, "unknown")] += 1
    return {
        "status": dict(sorted(statuses.items())),
        "final_n": len(final),
        "metrics": metrics,
        "first_hit": dict(sorted(hit_counts.items())),
        "first_hit_denominator": len(final),
        "note": "OHLC threshold hits are not fills; same-bar ordering remains ambiguous.",
    }


def review_comparison(rows, flags):
    """Only records labeled *before* seeing outcomes enter review agreement."""
    result = Counter()
    for row, status in zip(rows, flags):
        label = (row.get("technical_review_label") or "").strip().lower()
        blinded = (row.get("technical_review_blinded") or "").strip().lower() == "yes"
        if not blinded:
            result["excluded_not_blinded"] += 1
            continue
        if label not in {"valid", "invalid"}:
            result["excluded_uncertain_or_missing"] += 1
            continue
        if status is None:
            result["unknown_gate_%s" % label] += 1
        else:
            result[("passed_" if status else "rejected_") + label] += 1
    return dict(sorted(result.items()))


def group_summary(rows, field):
    flags = [memberships(r)[field] for r in rows]
    positive = [r for r, value in zip(rows, flags) if value is True]
    totals = {
        "pass": sum(value is True for value in flags),
        "fail": sum(value is False for value in flags),
        "unknown": sum(value is None for value in flags),
    }
    return {
        "membership": totals,
        "manual_review_blinded_only": review_comparison(rows, flags),
        "outcome_16": outcomes(positive, 16),
        "outcome_32": outcomes(positive, 32),
    }


def analyze(rows):
    cohorts = defaultdict(list)
    for row in rows:
        cohorts[tuple(row[k].strip() for k in COHORT_KEYS)].append(row)
    result = []
    for identity, records in sorted(cohorts.items()):
        result.append({
            "identity": dict(zip(COHORT_KEYS, identity)),
            "raw_n": len(records),
            "directions": dict(sorted(Counter(r["direction"].strip().lower() for r in records).items())),
            "technical_review": dict(sorted(Counter((r.get("technical_review_label") or "missing").lower() for r in records).items())),
            "blinded_review": dict(sorted(Counter((r.get("technical_review_blinded") or "missing").lower() for r in records).items())),
            "groups": {group: group_summary(records, group) for group in GROUPS},
        })
    return {
        "method": "descriptive fixed-horizon, separate cohorts; no model optimization",
        "total_rows": len(rows),
        "cohorts": result,
        "experimental_thresholds": {
            "body_range_pct_min": BODY_RANGE_MIN,
            "body_atr14_min": BODY_ATR_MIN,
            "directional_close_pct_min": DIRECTIONAL_CLOSE_MIN,
            "note": "Research hypotheses, NOT recommended production filters.",
        },
        "limitations": [
            "Cohorts may overlap; do not sum memberships as independent observations.",
            "Unblinded/uncertain labels excluded from validity agreement.",
            "Unknown evidence is not classified as a pass or a failure.",
            "Partial/censored horizons excluded from finalized outcome distributions.",
            "Consecutive event sampling and chart/feed parity require external review.",
            "Overlapping events and common-day effects invalidate naive independence assumptions.",
            "ATR excursions and OHLC hits are not executable profitability.",
        ],
    }


def print_summary(report):
    print("Phase C: %d recorded raw events across %d fixed cohorts" %
          (report["total_rows"], len(report["cohorts"])))
    if not report["cohorts"]:
        print("No observations. Capture consecutive raw events before interpreting filters.")
        return
    for cohort in report["cohorts"]:
        ident = cohort["identity"]
        print("\n%s %sm->%sm | %s | SHA %s | profile %s | N=%d" %
              (ident["source_tickerid"], ident["chart_tf"],
               ident["po3_anchor_tf"], ident["timezone"],
               ident["source_commit_sha"][:12], ident["settings_profile"],
               cohort["raw_n"]))
        print("%-23s %5s %5s %7s %8s %8s" %
              ("Hypothesis", "PASS", "FAIL", "UNKNOWN", "FINAL16", "FINAL32"))
        for name, data in cohort["groups"].items():
            m = data["membership"]
            print("%-23s %5d %5d %7d %8d %8d" %
                  (name, m["pass"], m["fail"], m["unknown"],
                   data["outcome_16"]["final_n"], data["outcome_32"]["final_n"]))
        print("Cohorts overlap. See --json for blinded-review disagreements,")
        print("outcome quartiles and first-hit ambiguity denominators.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csvfile", nargs="?",
                        default=str(Path(__file__).with_name("cisd_phase_c_sample.csv")))
    parser.add_argument("--json", dest="jsonpath", type=Path,
                        help="Optional JSON report output path (no file by default)")
    args = parser.parse_args()
    records, errors, warnings = check(Path(args.csvfile))
    for message in errors:
        print("ERROR:", message)
    if errors:
        print("Refusing analysis: %d validation errors" % len(errors))
        return 1
    for message in warnings:
        print("WARN:", message)
    report = analyze(records)
    report["validation_warnings"] = len(warnings)
    print_summary(report)
    if args.jsonpath:
        args.jsonpath.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n",
                                 encoding="utf-8")
        print("JSON report:", args.jsonpath)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
