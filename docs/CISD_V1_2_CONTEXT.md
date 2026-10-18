# CISD v1.2 — context-filter research spike

**Status:** draft; must be compiled and validated in TradingView. Depends on unmerged CISD v1.1 branch. Does **not** replace or fix the raw CISD detector.

## Why this exists

The v1.1 `All + C2 highlighted` mode exposes many mechanical CISDs. A one-candle opposing run followed by a close through its origin opening price may satisfy the **mechanical** rule but says little about trade quality without context.

TTrades definitions:
- https://ttrades.com/understanding-the-change-in-state-of-delivery-cisd/ — consecutive directional delivery run and body close through the first candle's open.
- https://ttrades.com/market-structure-shifts-vs-change-in-the-state-of-delivery-a-clear-comparison/ — CISD (open-level delivery) versus MSS (swing-point structure break).
- https://ttrades.com/how-change-in-the-state-of-delivery-cisd-confirms-swing-points/ — C2/C3 HTF *closure* together with LTF CISD for validated swing points.
- https://ttrades.com/kill-zones-explained-best-trading-sessions-for-entries/ — New York session clock and forex killzone windows.

**Important:** This is a source-specific interpretation, not a unique consensus algorithm. A raw CISD isn't an entry signal; killzone membership does not prove a CISD is valid.

## New optional research-only display filters

In section `4 · CISD + STDV`, set `CISD = All + C2 highlighted`. Then:

| Research: draw filter | Behavior |
|---|---|
| All (default) | v1.1: draw newest retained events according to original research view settings. |
| C2-associated | Draw only CISDs originally linked to a **live** C2 by Bandz's legacy `poLinkCisd` logic. Does **not** assert C2 had a confirmed close. |
| Killzones | Draw only events confirmed on chart bars whose **opening time** falls in an enabled killzone. |
| C2-associated + Killzones | Require both conditions. |

By default, the enabled killzones are:
- London: **02:00–05:00**
- New York AM: **07:00–10:00**
- Optional London close: **10:00–12:00** (off by default)

All windows are session inputs in the **Bandz-selected timezone**, default `America/New_York` (DST-aware). These example windows are for forex, not universal across all instruments. Session classification is intentionally limited to intraday chart periods **at or below 1H**; on larger timeframes a killzone-only filter will draw no events.

The chosen killzone is snapshotted **at the CISD's confirming chart candle**, by its opening time. A 15M confirmation at 10:00 is not in the NY AM 07:00–10:00 window even though the bar closes at 10:15. Other criteria (such as the sweep occurring in the zone rather than the confirming close) require a separate option, not a hidden assumption.

All events, including events outside killzones, remain in the bounded research registry; recorded invalidation status is unaffected. The filter restricts drawings and hence labels, not event detection, history, C2/SMT/PSP calculations, STDV or the original `Sequence only` and `All` modes. `Research: draw events` limits the number of **matching** events shown. Its value is not a filter over just the latest N raw events.

## Known raw-detector limitations to investigate next

From code inspection, current Bandz CISD:
1. Tracks successive same-direction candles and chooses either the first (Standard) or last (Sensitive) run candle's opening level.
2. Confirms on an opposite-color candle whose **close** crosses that opening level, with a configurable `Min run` (user comparison used 1).
3. Does **not** demand a liquidity sweep, proximity to a POI, displacement minimum, or a confirmed C2/C3 HTF close.
4. Keeps the older opposing run's state until it triggers or is overwritten by a new run of that direction. Thus it does not intrinsically prove the selected run was the *last uninterrupted delivery sequence into the swept high/low*. We must compare representative candle-level events before rewriting it.
5. Legacy sequence linking occurs after a C2 directional extreme but can happen while C2 is *live*. The event registry's `c2Linked` field is not verified closed-C2 status.

**Deferred:** strict latest-delivery-run identification; swing/liquidity sweep requirement; C2 post-closure qualification state/time; price-displacement and body-size filters; POI context; configurable scoring. These are separate hypotheses to test, not claims of the exact private Cephxs algorithm.

## TradingView manual acceptance test

1. Install this branch as a new Pine script, compile, and compare `All + C2 highlighted / Research: draw filter = All` with validated v1.1 using identical EURUSD feed, 15M → 4H settings and the same Bar Replay end point. Original lines, labels and states should match.
2. Switch draw filter to `C2-associated`. Lines should reduce to existing thicker C2-linked events; raw events stay stored and reappear under All.
3. Switch to `Killzones`. Check an October 9 event *inside* London or NY AM and an event *outside*. Only the former should display; manually verify event chart-open time in Bandz's configured timezone.
4. Disable both London and NY AM (leave London close off): Killzones must show no research lines or labels. Re-enable one and verify lines return. Original `Sequence only` and `All` modes must remain unchanged.
5. Switch to `C2-associated + Killzones`; only overlapping events should draw, including any that were later invalidated if fading is enabled.
6. Change label filter while the drawing filter stays fixed: labels only may change; lines should not.
7. Confirm event status Active → Invalid at the original confirmation level under a filter. Flip back to All: invalidation metadata must still be retained, even if filtered out while price moved.
8. Test a second forex major and longer historical window for drawing-object/runtime issues. Do not merge until confirmed.

## Next research gate

Capture **one mechanically detected CISD without an obvious liquidity sweep** and **one first post-C2 CISD after a C2 candle has definitely closed back inside C1**. Compare those with TTrades and Cephxs. Decide strict-run, sweep, and C2-closed rules *before* changing legacy detection.

**PR base:** `feature/cisd-v1.1-history-diagnostics`. Merge v1.1 only after its remaining regression checks; review this PR separately.
