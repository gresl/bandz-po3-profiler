# CISD V2C engineering investigation — 2026-11-20

**Status (updated 2026-11-20):** source/frozen-log diagnosis complete; private Cephxs reference event logger compiled and produced historical closed-event CSV. Bandz V2C/4G native Pine compilation remains optional and unverified. This is NOT evidence of trade profitability or of Cephxs parity.

## Versions and feeds

- Frozen Bandz reference: experiment/cisd-v2-pine-logs-20261120, PR #18. Do not adjust its detection inputs.
- New research diagnostics: experiment/cisd-v2c-causal-diagnostics-20261120. Parent is PR #18; default-OFF new logging only.
- Cephxs archive: private gresl/cephxs-cisd-reference/source/cephxs-cisd-base.pine. Keep the preserved file unmodified; copyright, redistribution and upstream provenance are described in its docs/SOURCE.md.
- Data: FOREXCOM:GBPUSD 15m historical UTC-close event logs. FTMO/MT5 is a different price feed. The 20 classified records are preserved in research/fixtures/GBPUSD_FOREXCOM_20261117_18_PINE_LOGS_FULL_COMPARISON.csv.

## Case 1: late bearish confirmation, Nov 18

| Fact | Evidence |
|---|---|
| Level | 1.31889 both Bandz engines |
| Legacy confirmed close | 07:15 UTC, candle O=1.31931, C=1.31777 |
| V2 confirmed close | 07:30 UTC, candle O=1.31777, C=1.31793 |
| V2 candidate first known | **07:30 UTC**; confirmed the same close |
| V2 pivot source | Pivot high length 1 right bar |

**Established explanation:** pivot qualification latency. The legacy opposing-run break was confirmed one candle before V2 first *knew* the candidate. There was no extra one-bar confirmation wait *after candidate creation*. V2 allows a bearish confirmation on a bullish-bodied candle when that candle closes below its reference. This is consistent with the archived Cephxs *source-level* close-through predicate, but does NOT prove Cephxs actually produced a 07:15 or 07:30 closed event.

**Decision:** never backdate the V2 pivot to an earlier close. If an earlier delivery-break preview is considered, classify it separately as PRE-PIVOT/PROVISIONAL; do not equate it to a confirmed pivot CISD.

## Case 2: distinct bearish levels, Nov 17 at 07:45 UTC

Legacy 1.31926 versus V2 1.31911 = 15 ticks = 0.00015 (1.5 GBPUSD pips). Both confirmed at the same close, C=1.31896 below both levels.

**Established explanation:** reference-origin algorithm difference. Legacy Standard uses the first candle's opening price in the tracked bullish run. V2 reconstructs a bullish opposing stretch around a confirmed high pivot using bridge=2, additional scan=12. The archived Cephxs reference computes the initial stretch around the confirmed pivot, skips to the first opposite-body candle and scans backward through contiguous candles up to a 300-bar limit, and uses the oldest candle's open. These algorithms are not equivalent. Without full *matching FOREXCOM OHLC*, the event logs alone cannot identify which origin candle is correct.

**Decision:** do not simply replace the V2 level with the legacy level. Use independent Cephxs closed-event logs (which include origin/pivot bars) to choose which disagreement is valid, then perform out-of-sample checks.

## Case 3: seven V2-only and three legacy-only events

Across 30 actual confirmations, the 20 one-to-one comparisons are: 8 EXACT, 7 V2_ONLY, 3 LEGACY_ONLY, 1 TIME_DIFF, 1 LEVEL_DIFF.

- All seven V2_ONLY confirmations had their candle body in the same direction as the CISD. Thus none is explained *solely* by legacy's candle-body direction gate. Legacy min-run, run level, close-through, age and duplicate gates were not captured in the initial 4F export; assigning a particular cause now would be speculation.
- All three LEGACY_ONLY confirmations are bearish. None has a demonstrated *same-side, same-reference within 20 ticks* V2 pivot-breach terminal event at the precise confirmed close. Nov 17 20:00 BEAR 1.32184 is NOT explained by the V2 BULL PIVOT_BREACH at 1.32262. Other nearby V2 BEAR candidates differ by 33–77 ticks and must not be called causal.
- Corrected lifecycle interpretation: do not pair an event with an opposite-side rejection merely because its time matches.

## Engineering deliverables

### 4G — optional causal telemetry added to Bandz (OFF by default)

Requires 4F Pine Logs ON and same UTC window. Emits CISDCAUSE1 records:
- On every V2 confirmation, captures the actual legacy run length, selected level, direction, minimum-run, close-through, run-age, duplicate eligibility predicates. Explicitly marks if legacy already confirmed and reset its run state.
- On every legacy confirmation, captures the *nearest known recent same-side* V2 candidate's level, state, reason, born time and price distance. It explicitly marks whether it lies within the user-specified near tolerance.
- On V2 confirmation, reports whether a candle *before* V2 candidate creation had already closed beyond that level, without claiming it was knowable then.
- These are terminally read-only; NO changes to V2 or legacy detection, alerts, drawings, C2 or Po3.
- Parser: research/parse_cisd_cause_logs.py accepts native TV Pine Logs Date,Message CSV (including replay-symbol wrappers) or pasted log text.

### Independent Cephxs closed-event adapter (kept PRIVATE)

Separate private branch experiment/private-cisd-closed-event-log-20261120 in gresl/cephxs-cisd-reference adds a private **derived research file**, leaving the archived original untouched. Its opt-in CEPHXSEVT1 records are written on confirmed closes at the source's actual confirmation block, before later drawings disappear. Fields include UTC close, direction, level, origin bar and pivot bar. **The new adapter's native Pine compilation has not yet been tested in TradingView.** It is a research-only derivative, not for publication or redistribution.

Bandz comparator: research/compare_cephxs_closed_events.py takes original Bandz 4F Pine Logs CSV plus Cephxs reference Pine Logs CSV, requires same symbol and timeframe, pairs exact close/direction before +/-one bar near-level pair, and reports EXACT/TIME_DIFF/LEVEL_DIFF/BANDZ_ONLY/CEPHXS_ONLY for Legacy and V2 independently.

This makes independent reference comparison feasible in batches rather than one screenshot per candle, but the private adapter itself still needs a one-time compile and exported CEphxs event data.

## Acceptance boundary

DONE: source-level latency and origin differences; frozen dataset classification; conservative lifecycle analysis; opt-in cause telemetry; independent reference logger implementation; Python unit and integration regressions in GitHub CI.

NOT DONE: native Pine v6 compile of optional Bandz V2C/4G; out-of-sample and realtime non-repainting demonstration of an improved detector. The Cephxs reference logger HAS compiled, with a historical event export as verified below.

**Research discipline:** There is not yet evidence to rewrite the V2 detection engine, relax the ATR gate, discard the pivot, or claim superior entry quality. Keep working baseline intact, investigate only verified disagreements, and separate early delivery breaks from pivot-confirmed entries.

## Nov 20 independent reference export — acceptance result

The user supplied 27 CEPHXSEVT1 confirmed Cephxs closed events from the private adapter on FOREXCOM:GBPUSD M15, Nov17–18. All embedded close_ms timestamps fall exactly 15m after native CSV bar-open Date. The frozen earlier Bandz log contains 17 V2 confirmations and 13 legacy confirmations through Nov18 09:45 UTC. Evaluate only the shared period Nov17 01:15–Nov18 09:45 inclusive; nine later Cephxs events lack Bandz coverage.

| Engine vs Cephxs | Exact | Level diff | Time diff | Bandz-only | Cephxs-only |
|---|---:|---:|---:|---:|---:|
| V2 | **17** | **0** | **0** | **0** | **1** |
| Legacy | **8** | **1** | **1** | **3** | **8** |

- Nov17 07:45 BEAR: Cephxs and V2 reference level 1.31911; legacy 1.31926, 15 ticks difference.
- Nov18 BEAR: Cephxs and V2 confirm 07:30 at level 1.31889; legacy confirmed 07:15 at same level, consistent with V2 pivot-qualification latency.
- All 7 formerly V2_ONLY vs legacy events are present at identical side, close and level in Cephxs.
- None of 3 legacy-only confirmations (Nov17 10:15 BEAR 1.31952, Nov17 20:00 BEAR 1.32184, Nov18 03:00 BEAR 1.32042) appears in Cephxs as a matching event.
- One extra Cephxs event at Nov18 02:15 BULL 1.32040, after the earlier 02:00 BULL 1.32040 event already matched by V2. Its new pivot bar 2750 differs from prior pivot 2746, but source origin bar 2745 and reference price are identical. Its candle opens 1.32060 and closes 1.32042, bearish-bodied but above level. Specific cause for V2 omission remains unproven.

**Decision:** freeze V2 detector for this bounded *in-sample historical reference-parity* phase. Do not tune to chase the repeated-level signal, alter legacy production, or claim live non-repainting or trade profitability. Defer optional 4G validation and retain PR #19 in draft; prioritize Po3/C2 integration and journaled trade outcomes. Raw private Cephxs log must not be committed to the public repo.