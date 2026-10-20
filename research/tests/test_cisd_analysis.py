#!/usr/bin/env python3
"""Synthetic-only unit tests; no generated observations enter the research CSV."""
import csv
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from analyze_cisd_sample import analyze, displacement, outcomes, percentiles
from validate_cisd_sample import EXPECTED, check


def row(**updates):
    base = {key: "" for key in EXPECTED}
    base.update({
        "event_key": "fake|test|never-a-real-trade",
        "source_tickerid": "SYNTHETIC:TEST",
        "chart_tf": "15",
        "po3_anchor_tf": "240",
        "timezone": "America/New_York",
        "source_commit_sha": "a" * 40,
        "settings_profile": "unit-test-only",
        "confirm_close_time_ny": "2026-01-01T09:15:00-05:00",
        "direction": "bull",
        "technical_review_label": "valid",
        "technical_review_blinded": "yes",
        "body_range_pct_then": "55",
        "body_atr14_then": "0.6",
        "directional_close_pct_then": "70",
        "c2_linked_then": "yes",
        "aligned_fvg_known_then": "no",
        "outcome_16_status": "FINAL",
        "mfe_atr_16": "1.5",
        "mae_atr_16": "0.3",
        "terminal_atr_16": "-0.2",
        "first_hit_1atr_16": "AMBIGUOUS same bar",
    })
    base.update(updates)
    return base


class PhaseCAnalysisTests(unittest.TestCase):
    def test_displacement_is_hypothesis_not_implicit_signal(self):
        self.assertTrue(displacement(row()))
        self.assertFalse(displacement(row(body_range_pct_then="54.9")))
        self.assertIsNone(displacement(row(body_range_pct_then="unknown")))
        self.assertFalse(displacement(row(body_range_pct_then="unknown",
                                          body_atr14_then="0.1")))

    def test_missing_fvg_remains_unknown_not_positive(self):
        case = row(aligned_fvg_known_then="")
        report = analyze([case])
        groups = report["cohorts"][0]["groups"]
        self.assertEqual(groups["raw"]["membership"]["pass"], 1)
        self.assertEqual(groups["aligned_fvg"]["membership"]["unknown"], 1)
        self.assertEqual(groups["c2_displacement_fvg"]["membership"]["unknown"], 1)
        # A checked YES without a formation timestamp is still unverified.
        missing_timestamp = analyze([row(aligned_fvg_known_then="yes")])
        self.assertEqual(missing_timestamp["cohorts"][0]["groups"]["aligned_fvg"]["membership"]["unknown"], 1)
        evidenced = analyze([row(aligned_fvg_known_then="yes",
                                 aligned_fvg_born_time_then="2026-01-01T09:00:00-05:00")])
        self.assertEqual(evidenced["cohorts"][0]["groups"]["aligned_fvg"]["membership"]["pass"], 1)

    def test_overlapping_cohorts_and_blinded_comparison(self):
        good = row(aligned_fvg_known_then="yes")
        bad = row(event_key="another", body_range_pct_then="45",
                  technical_review_label="invalid", technical_review_blinded="no",
                  outcome_16_status="PARTIAL", terminal_atr_16="")
        report = analyze([good, bad])["cohorts"][0]["groups"]
        self.assertEqual(report["displacement"]["membership"]["pass"], 1)
        self.assertEqual(report["displacement"]["membership"]["fail"], 1)
        self.assertEqual(report["raw"]["manual_review_blinded_only"]["excluded_not_blinded"], 1)
        self.assertEqual(report["raw"]["outcome_16"]["final_n"], 1)
        self.assertEqual(report["displacement"]["outcome_16"]["first_hit"]["ambiguous_same_bar"], 1)

    def test_partial_excluded_and_quartiles(self):
        metrics = outcomes([row(), row(outcome_16_status="PARTIAL",
                                       mfe_atr_16="4", terminal_atr_16="")], 16)
        self.assertEqual(metrics["final_n"], 1)
        self.assertEqual(metrics["metrics"]["mfe_atr"]["median"], 1.5)
        self.assertEqual(percentiles([1, 3, 5])["p25"], 2.0)

    def test_empty_manifest_is_valid_but_no_sample(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "empty.csv"
            with path.open("w", newline="", encoding="utf-8") as fh:
                writer = csv.writer(fh)
                writer.writerow(EXPECTED)
            rows, errors, warnings = check(path)
            self.assertEqual((rows, errors, warnings), ([], [], []))
            self.assertEqual(analyze(rows)["total_rows"], 0)


if __name__ == "__main__":
    unittest.main()
