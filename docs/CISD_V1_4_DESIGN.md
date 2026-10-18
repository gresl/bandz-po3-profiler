# CISD v1.4 — Structural qualification contract (research design)

**State:** design only; no Pine detection or rendering change in this branch yet. The current stable code is on `main` (v1.1–v1.3 merged). This specification is deliberately independent of the private Cephxs implementation.

## Goal

Classify *when a mechanically detected CISD has additional contemporaneous structural context*, rather than deleting every raw/engulfing-like CISD or treating C2 association/killzone membership as proof of trading quality.

Use separate **as-known-then** and **eventual outcome** fields. A later closed C2 or FVG may be associated retrospectively for analysis, but **must not upgrade the original signal as of its earlier confirmation candle**.

## Exact baseline in merged source

- `poCisdNewBull / poCisdNewBear` detect a chart-TF close beyond the first/last opposing delivery-run open (Standard/Sensitive), currently controlled by `Min run`.
- `poEvalSide` identifies C2 candidates: C2 opens within C1, sweeps C1 extreme, and for a completed C2 closes back inside the C1 high–low range; the currently forming C2 is provisional.
- `poLinkCisd` attaches the first CISD to a *live* same-direction sequence only after the C2 extreme (not necessarily after confirmed C2 close).
- v1.3 `c2ClosedAt` records a later valid C2 close if the same CISD remains linked.
- v1.3 aligned/opposing FVG bars are time-linked, but the nearest gap is **not** proof of displacement quality, FVG relevance, or directional confirmation.

Therefore **do not label** `c2Linked` alone as `C2 confirmed`.

## Proposed independent qualification fields

| Field | Definition at original CISD confirmation | Later updates? |
|---|---|---|
| `rawConfirmed` | Existing closed-candle Bandz CISD formula | No |
| `associatedLiveC2` | Existing first CISD link to an alive C2 after C2 extreme | Stored at confirmation |
| `c2ConfirmedNow` | C2 *already* closed back inside C1 by CISD confirmation and still linked | No |
| `c2ConfirmedLaterAt` | Same C2 closes and still links original CISD | Yes, separate timestamp |
| `c2SweepSide` | Bull: C2 low below C1 low; bear: C2 high above C1 high | Snapshot from C2, when linked |
| `levelReclaimedAt` | Separate later close back across CISD level (v1.1 field) | Yes |
| `bodyToRange` | abs(C-O)/(H-L), with zero-range guard | No |
| `bodyToAtr` | abs(C-O)/confirmed ATR(14), with na/zero guard | No |
| `closeLocation` | Direction-adjusted close position within candle range | No |
| `alignedFvgAtConfirm` | Already-confirmed, uninvalidated same-direction chart-TF FVG within preceding window | No |
| `alignedFvgLaterAt` | New same-direction FVG confirmed **after** CISD, within forward window | Yes, not backdated |
| `inKillzone` | Session tag from v1.2 with explicitly defined chart-bar opening time | No |

For v1.4, do not add weighted proprietary-looking scores. Use transparent boolean flags and numeric measurements so we can later compare false positives and true negatives instead of selecting attractive historical outcomes.

## Initial display hypotheses (all opt-in)

- **Raw (reference)** — all confirmed historical CISDs (the current v1.3 `All + C2 highlighted` view).
- **Sweep-associated** — first chart-CISD linked to an HTF C2 that demonstrably swept C1. A *live* C2 sweep is provisional.
- **C2 confirmed as-of now** — only those where C2 had actually closed and passed its closure conditions **by the CISD confirmation time**. This must NOT include any retroactive promotion.
- **C2 eventually confirmed** — retrospective diagnostic view only, clearly labeled **not available at CISD time**.
- **Displacement candidate** — recorded body/range, ATR-normalized body and close-location filters; user-selectable thresholds; default off. Do not infer that high ATR alone proves CISD relevance.
- **FVG context at confirmation** — use already known and still active FVGs only. Subsequent FVG formation is a separately labeled annotation, never contemporaneous confirmation.

Killzones are a separate timing overlay, **not a definition of valid CISD**; PB is an independent future detection module (not synonymous with FVG).

## Definitions needing care

1. **Sweep:** For this first phase, use Bandz's own C1/C2 sweep evidence, not a generic nearby swing/high-low or alleged stop-run; adding daily/session/HTF liquidity sweeps should be a separately specified detector.
2. **ATR:** Compute consistently on the chart timeframe and only from closed data. Compare normalized metrics across EURUSD, GBPUSD, and later gold; avoid fixed-pip rules.
3. **Closed C2:** Use `rc.c3StartTime` as the exact C2 close boundary only when qualified; require `c2ClosedAt <= event.confirmTime` for *as-of-now* qualification (and distinguish equality explicitly).
4. **Direction:** Check bull/bear association against `rc.side`. A bearish three-candle FVG does not qualify a bullish CISD merely due to overlapping prices.
5. **Replay and non-repainting:** A historical label may display retrospective outcome, but historical *eligible-to-trade at time T* must be calculated using only information available at T.

## Implementation phases

**Phase A (next code PR):** Add closed-candle displacement metadata (body/range, body/ATR, close-location), explicit C2 temporal tags, clear debug labels/tables; preserve legacy and existing v1.3 modes unchanged. No automatic alerts or entries.

**Phase B:** Add research-only *drawing* filters combining independently testable sweep, C2-at-confirmation, and displacement, all off by default. Record counts of each category and allow unfiltered fallback.

**Phase C:** Collect event-to-outcome research on known fixed periods. Evaluate whether exclusions are useful. Only after this, consider strict latest-run detection as **a separate alternate algorithm** and a new Propulsion Block detector.

## Acceptance checks

1. Original `Sequence only` and `All` modes unchanged versus merged main baseline.
2. October 8 EURUSD: C2-associated bullish CISD first says live/unconfirmed; a later C2 close is recorded only at actual closure. As-of-confirmation qualification stays unchanged.
3. October 14 EURUSD: bear CISD reclaim and bearish FVG tracked independently; no use of a later FVG to qualify an earlier signal.
4. October 8 GBPUSD: live C2 and xC2 cases preserve distinct qualifications, including failed/superseded candidates.
5. Changing filters or numeric thresholds never alters original Po3 phase, raw CISD confirmation times/levels or saved FVG event origins.
6. Bar Replay on two FX symbols, first before and after each confirmation, then longer history under max configured registry sizes. No Pine timeout or drawing-limit errors.
7. **No claim of Cephxs parity** without paired identical feed, exact time and marker categories verified against observable Cephxs outputs.

## Trade decision

These classifications are tools for discretionary research, not a validated strategy or indication of profitability. No automatic executions, webhook order actions or new alerts are in scope.
