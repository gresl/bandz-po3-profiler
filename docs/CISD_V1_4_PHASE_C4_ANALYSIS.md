# Phase C4 — descriptive comparison, no threshold optimization

Branch: feature/cisd-v1.4-phase-c-c4-analysis
Base: Phase C3 draft PR #7, stacked on draft PR #6. No Pine source edits.

## Why

Phase C outcomes and the consecutive-event sample already exist. This layer compares the **entire raw CISD cohort** against independent hypotheses, without converting displacement, C2 or FVG into a new detector or selecting thresholds after seeing results.

## Frozen hypotheses (NOT trading rules)

- Raw: all consecutive confirmed CISDs, including ignored/no-trade and invalidated events.
- C2-linked at confirmation; C1 swept at confirmation; C2 already confirmed at confirmation.
- Displacement: body/range >=55% AND body/ATR14 >=0.6 AND directional close >=70%, evaluated solely at confirmation.
- Same-direction FVG known at confirmation, **with a recorded formation timestamp**. A gap appearing later never qualifies the earlier event.
- Exploratory intersection of C2-linked + displacement + known aligned FVG.
- Actual event-time audit eligibility as reported, not recomputed from later outcomes.

Every hypothesis has PASS, FAIL, UNKNOWN. Missing evidence is not a positive pass. Cohorts overlap and must not be summed as independent events.

## Run (from repo root, Python 3.8+)

    python3 research/validate_cisd_sample.py
    python3 research/analyze_cisd_sample.py
    python3 research/analyze_cisd_sample.py --json phase-c4-results.json
    python3 -m unittest discover -s research/tests -v

The validator checks the unchanged canonical CSV. The reporter prints sample totals, experimental-filter pass/fail/unknown counts and finalized horizon counts. Optional JSON contains per-horizon terminal ATR return, MFE, MAE p25/median/p75 and distinct first favorable, adverse, ambiguous same-bar and no-hit classifications; each metric has its own denominator.

**The canonical CSV intentionally has zero observations.** With zero rows, the reporter should emit a no-data message, not manufactured results.

## Interpretation safeguards

1. Manual technical-validity agreement uses only records marked technical_review_blinded=yes and labeled valid/invalid. Unblinded/uncertain labels are disclosed and excluded from the blinded-agreement calculation.
2. At each 16/32-bar horizon, only FINAL outcomes enter the distributions. PARTIAL, CENSORED, NOT_EVALUABLE and missing rows stay visible as status counts. Favorable first hits do not equal realized winning trades.
3. Same-bar favorable/adverse 1-ATR touches are ambiguous, not wins/losses. Raw events may correlate strongly by day and Po3 sequence. A 30–50-event sample is descriptive, not an independent backtest.
4. Separate cohorts by symbol/feed, chart TF, anchor, time zone, Pine SHA and input profile. Do not aggregate EURUSD with GBPUSD replication or two versions of the indicator.
5. The 55/0.6/70 displacement thresholds are experimental, not optimized. Any proposed changes require a new prespecified hypothesis and an independent holdout cohort.
6. The analysis cannot prove all CISDs were captured consecutively or validate manually entered timestamps. The C3 procedure and independent TradingView audit remain mandatory.

## Before drawing C4 conclusions

- Verify an uninterrupted +31 to +32 Replay transition without reloading the indicator; frozen event fields must stay MATCH.
- Run GBPUSD/xC2 and legacy drawing regression checks; leave stacked PRs draft until accepted.
- Collect 30–50 consecutive raw EURUSD 15m-to-4h CISDs with confirmation-time manual labels before seeing later candles, or disclose non-blinded assessment.
- Check horizon maturity, compare raw CSV denominators against output, and discuss both valid setups filtered out and invalid setups permitted by each hypothesis.

No new alerts, execution, Cephxs parity claim, significance or strategy profitability claim.
