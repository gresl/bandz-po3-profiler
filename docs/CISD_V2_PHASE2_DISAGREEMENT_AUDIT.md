# CISD V2 Phase 2 — mechanical disagreement audit

**Status:** research-only implementation; Pine v6 compilation and TradingView Replay acceptance **pending**.  
**Branch:** `experiment/cisd-v2-disagreement-audit-20261117` (based on `experiment/cisd-v2-pivot-lifecycle-20261115`).

## Why

Phase 1 produced positive closed-bar matches for the GBPUSD 15m bearish event at **2026-11-11 05:45 UTC, 1.33454** and bullish event at **2026-11-12 07:30 UTC, 1.32606**. The question now is **where and why the engines disagree**. More or fewer drawings do not establish model quality.

The Bandz legacy event recorder (`poCisdEvents`) and experimental V2 pivot event recorder (`v2rEvents`) coexist in the same Pine script. This phase adds a **read-only, opt-in comparison table**, without modifying either detector, original Bandz Po3 links, or alerts.

## Inputs (4C · CISD V2 pivot research)

- `V2: enable pivot research detector`: **ON**.
- `V2 audit: compare legacy vs V2`: **ON** to show comparison table at top right. Defaults **OFF** in source.
- `V2 audit: maximum comparison bars`: 96 (about one day of uninterrupted 15m bars; data gaps affect elapsed duration).
- `V2 audit: same-level tolerance (ticks)`: 3 (0.3 pip for a 5-decimal non-JPY forex feed with 0.00001 tick size).
- `V2 audit: near-time tolerance (ticks)`: 20 (2 pips for that feed); applies only when confirmations occur **exactly one bar apart**.
- Preserve V2's previously saved `MinRun=1, ATR stretch gate=ON, ATR threshold=0.5, pivot=1, bridge=2, scan=12, expiry=10` for the first disagreement pass.
- Leave legacy CISD inputs unchanged from baseline. The legacy event-history recorder does not require its line drawings or audit panel to be visible, but ensure it is not disabled by changing code.

**Do not overwrite the RAW, MINRUN2, ATR05 templates or chart layouts.** Use a separate "DISAGREEMENT" research copy.

## Algorithm: exactly what classification means

Event eligibility: V2 `CONFIRMED` and previously confirmed but now `INVALIDATED` both count as confirmed. Rejected, expired, superseded and pending candidates never count as confirmations. All legacy history entries are confirmed.

Both collections are bounded. The comparable window begins at the **latest** of (a) the selected last N chart bars, (b) the oldest retained V2 candidate's first-known bar, and (c) the oldest retained legacy event's confirmation bar. Therefore **the panel does not claim to cover more history than the recorders actually retain**.

The comparison greedily matches pairs of the **same direction**, with each confirmation usable at most once:

1. **Exact confirmation bar first**: if reference levels are within 3 ticks, label `EXACT`; otherwise `LEVEL_DIFF`.
2. **Only unpaired events**, confirmed **one chart bar apart**, with reference levels within 20 ticks: `TIME_DIFF`.
3. Remaining unmatched V2 confirmations: `V2_ONLY`.
4. Remaining unmatched legacy confirmations: `LEGACY_ONLY`. Search for a nearby same-direction V2 **unconfirmed** candidate at a similar price. A `Related V2 REJECTED/EXPIRED/SUPERSEDED/PENDING` note is diagnostic correlation only, **not proof of why** the legacy event was missing.

The top-right panel displays counts over that intersection and the **8 most recent non-EXACT events**. Summary counts are not signals of profitability; no accuracy can be measured without human-approved cases and proper OHLC evidence.

## Limitations

- **Cephxs reference signals are NOT inside the table.** Pine scripts cannot read another closed-source indicator's internal candidate collections. A screenshot comparison with Cephxs or manually obtained log remains necessary after a useful Bandz mismatch is identified.
- Same-time mismatched price levels are not automatically incorrect; there can be more than one plausible structural reference.
- The one-bar nearby pairing is a heuristic: it can pair related-but-distinct events during choppy price action. Review both origins and price levels before asserting timing differences.
- A missing event might result from source-engine differences, ATR/MinRun filters, lifecycle/expiry, bounded-history truncation or feed/session differences. The panel cannot assign causality.
- The V2 event registry stores at most 80 **all-state candidates**, whereas legacy stores up to 100 **confirmed** events. This is why the intersection cutoff is essential.
- Realtime provisional signals / repainting are outside this closed-event audit. Do not infer 05:30:01 firing from a historical 05:30 line anchor.
- The indicator may render both the legacy audit (bottom-right) and V2 registry (top-left). Only turn on the extra top-right difference table when needed, to reduce clutter.
- The `same-level` and `near-time` tolerance values are classification thresholds, **not new detector thresholds**.

## First TradingView acceptance fixture

Feed: `FOREXCOM:GBPUSD`, timeframe `15m`, UTC chart timezone, replay to **2026-11-12 07:45 UTC** (after the bullish 07:30 confirmation). Use the saved ATR05 detector configuration, but add the Phase 2 comparison panel.

1. Compile the new branch as a **new Pine Editor script/copy**, never overwrite the previously validated V2.
2. Confirm no compiler/runtime errors.
3. Check whether known **BEAR 2026-11-11 05:45 UTC @1.33454** and **BULL 2026-11-12 07:30 UTC @1.32606** are included in `EXACT` when inside the comparable retained-history window. If outside the intersection, they are **out-of-sample** for that snapshot, not discrepancies.
4. Capture the entire top-right disagreement table and event context. Choose the **newest actionable `LEGACY_ONLY` or `V2_ONLY`**, prefer a same-direction related rejected candidate if displayed. Record direction, UTC confirmation close, reference level and V2 rejection reason for the next audit.
5. Freeze this case; then inspect raw candle OHLC and drawing/confirmation timing before proposing algorithm changes.

## Offline regression tests

`python3 -m unittest discover -s research/tests -v`

The new `research/tests/test_v2_disagreement_oracle.py` contains ten synthetic classification tests. They verify one-to-one matching and classification boundaries, **not** the Pine compiler, historical broker feeds or Cephxs parity.

## Acceptance / merge gate

Keep this branch and its draft PR **unmerged** until native Pine compile, repeatable Replay output and one verified disagreement classification pass. Do not merge purely because synthetic tests pass.

## Replay consistency investigation — November 17, 2026

Three GBPUSD 15m Replay screenshots compared:

- After enabling Phase 2 comparison, the legacy fixed NY `2026-11-12 02:30` event was initially visible in the Settings-open chart.
- After closing Settings, the *fixed legacy audit panel* said `NOT FOUND in retained history`, and its chart-side research line disappeared.
- Returning Replay to before 07:00 UTC and stepping forward to 07:45 restored the exact BULL event at **2026-11-12 07:30 UTC, level 1.32606**.
- The V2 vs legacy table remained `EXACT 7 / LEVEL 0 / TIME 0 / V2_ONLY 6 / LEGACY_ONLY 0` in both latter screenshots. Its first difference row was `BEAR V2_ONLY` at **2026-11-12 02:30 UTC**, level around 1.32765.

Important methodological finding: prior Phase 2 `EXACT` used only confirmation **bar index**, direction and level, whereas the fixed legacy audit searches the event's recorded **confirmation timestamp** formatted as NY civil time. This can conceal a timestamp discrepancy, and the panel itself may also be stale at certain Replay endpoints. We have NOT established which scenario caused the observed difference.

Audit-only fix committed after the screenshots:
1. `EXACT` and `LEVEL_DIFF` now additionally require equal stored **close timestamps**.
2. Same bar index but mismatched stored close timestamps (with nearby level) becomes `STAMP_DIFF` and increments `STAMP N` on the top-right panel.
3. Top-right header reports whether Replay's last chart bar is currently `END OPEN` or `END CLOSED`, alongside its UTC close time.
4. Neither legacy nor V2 detector, candidate state, alert, plotting geometry or Po3 qualification is altered.

The update needs fresh Pine compilation and one paired screenshot (top-right comparison + bottom-right fixed audit), ideally first **after an F5 reload at the existing Replay endpoint**, then one more after stepping Replay forward from before the 07:30 close. Do not infer an actual missed close from a single historical drawing disappearance.

The **next research disagreement fixture**, after timestamp consistency is proven, is `V2_ONLY` bearish event on Nov 12 **02:30 UTC** near **1.32765**. Its mechanical classification is not evidence of signal quality; compare independent Cephxs and original legacy history at that exact time before changing candidate rules.

## Replay UI clarification — November 17 18:01–18:03 UTC

After replacing the Pine code and using F5 / Replay bar stepping, user supplied two screenshots showing the **legacy BULL November 12, 2026 07:30 UTC, level 1.32606** alongside the V2 event registry. V2 table explicitly contains `BULL | 1.32606 | known 11-12 07:30 | confirm 11-12 07:30 | CONFIRMED`. The legacy fixed NY close selector `2026-11-12 02:30` shows the same direction, time and level. The top-right discrepancy panel reports `EXACT 8 / LEVEL 0 / TIME 0 / V2only 6 / Lonly 0 / STAMP 0`, with `END OPEN` and endpoint close `11-12 07:45`.

**Interpretation of missing V2 horizontal line:** This is NOT a missing confirmation. Phase 1 code plots only pending reference levels (`v2rPendingBull`, `v2rPendingBear`) and **confirmation plotshape triangles** (`v2rNewBull`, `v2rNewBear`), plus the event registry. V2 pending lines disappear on confirmation; unlike legacy Bandz, no persistent confirmed-V2 line is drawn. A cyan V2 upward marker appears beneath the corresponding confirmation candle. Audit result is consistent with code.

The current "END OPEN" status means the 07:45 endpoint candle is not itself confirmed; the earlier 07:30 event is stored and is stable within this screenshot. Exact matching and STAMP0 are evidence limited to the bounded overlapping history, not global detector accuracy or proof of replay deterministic equivalence.

**Phase 2 recommendation:** Before changing detection thresholds, optionally add an **independent, OFF-by-default confirmed-V2 line visualization** anchored at actual confirmation candle (not originating pivot) with a bounded number of lines and explicit UTC close marker. This is a display feature only. Next investigate the earliest nontrivial `V2_ONLY` BEAR (2026-11-12 02:30 UTC, roughly 1.32765) with unmodified filters and compare Cephxs reference, not merely the presence/absence of horizontal lines.
