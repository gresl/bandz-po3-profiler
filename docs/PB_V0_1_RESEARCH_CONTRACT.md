# Phase PB-A — Propulsion Block independent research contract

**Status:** research/design only — no indicator logic or chart output changed by this document. 
**Baseline:** fork branch `feature/cisd-v1.4-phase-c-c6-parity-audit` at `e51113d1fcbe8dbdd7cbc55e9e8a223fb53e5e1d`.
**Goal:** implement an original, strictly causal *research* detector for ICT/TTrades-style Propulsion Blocks (PB), observe whether it coincides with Cephxs' visually marked PB, and test it independently of the existing Bandz Po3/CISD engine.

## Evidence and definition

1. TTrades (2025-07-08), *Understanding Propulsion Blocks in Trading*, https://ttrades.com/understanding-propulsion-blocks-in-trading/ : parent OB -> revisit -> new opposing candle in/at that OB -> confirming displacement; opening price is important and the PB mean threshold should hold.
2. Independent interpretation of ICT Month 04 source: https://www.ictkillzone.com/ict-propulsion-block — a **later** opposing candle revisits an **earlier** OB, then price displaces away in the original direction; midpoint is the PB **body** mean threshold, not a 3-candle FVG midpoint.
3. Existing Bandz C6 source has *no validated OB or PB registry*: `PoCisdEvent.lastOpposingOpen/High/Low` is explicitly an **OB reference only** (around line 1639). The original CISD break-close, C2 association, and research FVG are not PB confirmation.
4. A Cephxs PB-style narrow blue/red mark is observable in prior user screenshots, but we cannot inspect its private code. *Similarity of markings is not proof of matching underlying rules.*

**Never define PB = any CISD, PB = CISD-origin candle, or PB = FVG displacement/middle candle.**

## State machine (chart TF; use closed candles only)

All records carry `bar_index`, `time` (bar OPEN), and `time_close` (bar CLOSE, with explicit fallback for unsupported charts). Timestamps in the audit view use `America/New_York`.

1. **PARENT_OB_CANDIDATE** — a previous opposing candle/short run exists. Bull case = latest down-close candle before bullish move; bear case = latest up-close before bearish move. Capture *both* full OHLC and body bounds, the candidate's origin index/time, run length, and first/last opens. Do not label a parent as valid yet.
2. **PARENT_OB_CONFIRMED** — after one or more subsequent candles, a closed bar moves in the proposed direction and breaks the chosen origin threshold (bull: above the opposing candle's high; bear: below its low) with separately measured displacement. Record confirmation bar/close time and metrics. Research variants below distinguish a structural close break and normalized displacement; no optimization.
3. **PARENT_ACTIVE / INVALIDATED** — only after confirmation may a parent be revisited. Maintain simultaneous *diagnostic* invalidation criteria: (a) close beyond full candle extreme, (b) close beyond the parent's body midpoint. Record earliest timestamp for each; do not rewrite prior state or erase records silently.
4. **PB_REVISIT_CANDIDATE** — after the parent is confirmed, a later, same-direction *opposing* candle trades into its price zone: bullish PB candidate = down-close candle interacting with a bullish parent; bearish = up-close candle interacting with a bearish parent. Save a parent ID and candidate OHLC, open/close, own body midpoint, parent interaction mode, and whether either parent invalidation rule was breached. The existence of a revisit candle alone is **not confirmation**.
5. **PB_CONFIRMED** — only after the candidate, a separately closed impulse in the parent direction satisfies the declared move-away/displacement test within the forward confirmation window. Snapshot first knowable confirmation close, validating close price, original PB candle and parent IDs. The PB's drawing *may* extend from the older candidate candle, but the legend MUST show the actual **confirmation close NY time**; no backdated alerts.
6. **PB_LATER_TEST / PB_INVALIDATED / EXPIRED** — forward-only touch of PB zone, first PB mean-threshold wick/close breach, first far-edge close, favorable/adverse excursions, and +16/+32 chart-close observations. Never change `PB_CONFIRMED_AT` after creation. Keep a distinct reason if the PB never confirms or its parent invalidates during confirmation.

### Initial measurable variants — explicitly hypotheses, not canonical settings

| Choice | Strict vs permissive research measurements |
|---|---|
| Parent zone | Full candle high/low AND body high/low; store both, select display variant |
| Parent formation | Single most recent opposing candle vs 1–3 opposing-candle origin run |
| Parent validation | Close beyond origin high/low; separately tag body/ATR14 ≥0.6 and ≥1.0, directional-close fraction |
| Revisit | Wick overlaps parent full range, vs candle body intersects parent body; record both simultaneously |
| Parent hold | Close beyond parent full extreme vs beyond parent body 50%; record earliest breaches separately |
| PB departure | Close beyond PB candle high (bull) / low (bear); measure ATR14-normalized body; max 1–3 closed bars as initial variants |
| PB invalidation | Closing beyond PB body midpoint vs full opposite wick extreme — **separate outcomes** |
| FVG | Contemporaneously existing / subsequently confirmed FVG **tags**, not part of baseline PB identity |
| CISD & C2 | Optional contemporaneous same-direction association; not parent OB or PB by fiat |
| Trading time | London/NY killzones as tags, not conditions defining PB |

*ATR ratios, lookbacks and limits above are seed hypotheses chosen for comparison; do not present as TTrades/ICT hard rules or assume they produce profitable trades.*

## Proposed implementation split

**PB-A1: foundation, research-only** (first code PR):
- `PoResearchOb` bounded registry, deterministic parent origin/confirmation/invalidations and one fixed-event audit selector; no PB drawing yet.
- Enable only on confirmed regular time-based chart candles; require sufficient warm-up.
- Default parent/displacement switches off for live drawing; research sampling does not alter raw CISD or Po3.

**PB-A2: stacked revisit + PB confirmation**:
- `PoResearchPb` bounded registry with unique parent reference, frozen revisit candle and separate later departure confirmation.
- Prototype visuals: small PB-level open line, distinct PB midpoint, parent box, candidate dotted vs confirmed solid, expiry/invalidation style, max configurable recent PB drawings (default PB research UI Off).
- Draw only once the confirmation candle closes; no lookahead, no backfilled trigger metadata, no PB trading alerts.

**PB-A3: parity and outcomes**:
- Compare same symbol/feed/timezone/chart interval/replay endpoint against Cephxs; record **anchor bar, PB candle open, PB level, parent OB, earliest known confirmation**, not just similar colored rectangles.
- Maintain a 16/32-bar fixed-event outcome audit, including failures and misses; screenshots are qualitative samples, not a success-rate estimate.
- Document false positives and false negatives before tuning any filter.

## Code integration and invariants

- The current `PoCisdEvent` registry and `poCisdNewBull/poCisdNewBear` trigger are **read-only context**. C6 event parity (EURUSD 15m, 2026-09-21 bearish, 09:30 candle OPEN NY/09:45 confirmation CLOSE NY, level around 1.14804) is a regression invariant.
- Never use the mutable current `poCisds` array as the PB source of truth; its historical invalidation/eviction is not an immutable OB registry.
- Do not mark a candidate as confirmed on the candidate candle when a future candle is required. A user-visible origin anchor may be historical, but the event-time audit must identify information first known later.
- Record complete first-known timestamps. A later C2/FVG/pullback may only update a **LATER** field.
- Bounded arrays, bounded draw objects, no duplicate same-bar entries on replay/ticks, clear recycling/expiry policies, no backward time travel.
- No modifications to legacy Po3, C1/C2/C3/C4, T-Spot, CISD, FVG/VI, alerts, receiver payloads, trade execution or default settings.

## Test protocol and objective pass criteria

1. **Synthetic bullish**: prior down-close parent -> confirmed departure -> later down-close revisit -> *later* up-close departure. Verify PB does not exist as confirmed before the departure closes, and parent/CISD are distinct records.
2. **Synthetic bearish mirror**: prior up-close parent -> departure down -> later up-close revisit -> later bearish displacement.
3. **No parent**: large FVG middle candle or isolated displacement **must not** produce a PB.
4. **Parent invalidated first**: revisit after invalidation is rejected; record why.
5. **Failed revisit / no departure**: expired candidate is retained as a failed observation, not retroactively hidden.
6. **Mean threshold**: wick breach and body close breach have distinct timestamps, and the PB midpoint is its own body 50%, not its FVG 50%.
7. **Replay invariance**: stepping one closed 15m bar changes only facts that can then be known; disabling/re-enabling yields the same fixed-event history given the same data window. Source display must not depend on the mutable newest-event index alone.
8. **Regression**: unchanged Sep 21 EURUSD 09:30/09:45 raw CISD identity; Oct 8 and Oct 16 EURUSD bullish C6 fixed-event audits, C2 and FVG behavior, and all default profiles.
9. **Cephxs comparison**: choose paired 2026-09-21, 2026-10-08 and 2026-10-16 EURUSD 15m cases, plus one non-EURUSD cross-check; classify `exact PB match`, `level mismatch`, `timing mismatch`, `Cephxs only`, `Bandz only`, `uncertain`. This is **visual validation only**: we do not possess Cephxs source.
10. **No performance claims** until a predeclared outcome rule, spread/slippage conventions, sample size, and out-of-sample period are tested.

## Research decisions

- The essential distinction: **PB is a stacked, subsequently confirmed OB**, not a CISD alias or FVG.
- Baseline detector should be *direction-neutral, instrument-normalized, and close-confirmed*. Strong displacement and aligned FVG remain measured **experimental gates**, not required default truths.
- We will first build `PB-A1`, not change the C6 file, and let the user verify Pine compilation/replay before we layer `PB-A2` on top.
