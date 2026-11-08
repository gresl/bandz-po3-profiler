# CISD v2 research — Bandz versus observable reference (2026-11-08)

**Status:** observation/specification only; **no Pine code changes**.  
**Branch:** `experiment/cisd-pivot-audit-nov2026`, based on `experiment/cephxs-base-parity-v0.1`.  
**Aim:** user-specific 15m -> 4H Po3/CRT model, with more structurally useful CISD decisions. Target review window: November 2026.

## Why this research exists

Bandz already produces valid raw candle-delivery reversal signals, but the user has observed raw CISD marks that do not correspond to the desired swing/HTF context. One visual match on GBPUSD 2026-10-29 does not establish general parity. The objective is **not** to reproduce proprietary Cephxs internals: distinguish (a) a raw delivery-open close-through, (b) a swing/pivot-qualified candidate, and (c) a trade-eligible HTF/DR/session setup.

Public TTrades educational descriptions:
- https://ttrades.com/understanding-the-change-in-state-of-delivery-cisd/
- https://ttrades.com/how-change-in-the-state-of-delivery-cisd-confirms-swing-points/

Their raw definition focuses on a candle **closing** beyond the opening price of a run of opposing candles (the first open for a run). Their trading interpretation separately requires contextual HTF closure. A pivot requirement is a **candidate quality rule**, not necessarily part of the raw CISD definition.

## Code review: present Bandz behavior

`Bandz_Po3_Profiler.pine` around lines 1461–1544 on the base research branch:
- Tracks most recent run of down-close/up-close candles and the first or last opening price.
- Default `poCisdMinRun=2` (single opposing candle is not sufficient).
- On a qualifying reversal close, requires the tracked level to be crossed, with a permissive age check (up to 60 chart bars).
- Option `poCisdFilterInv` removes a confirmed line after a **close** back across its level, rather than modeling the origin swing extreme as a separate invalidation reference.
- Confirmation research history, source timestamps, C2 qualifiers and outcome diagnostics already exist; **preserve them**.

Reference **hypothesis**, based on private user-supplied CISD [base] inspection and webhook observations: a pivot-seeded candidate with its own age, ATR significance and origin invalidation can account for some visual discrepancies. **Private source is not to be copied to this public repository.** Standalone [base] is not proven to share all Ultimate+ internals.

## Testable hypotheses (not asserted facts)

| ID | Hypothesis | A/B isolation |
|---|---|---|
| H1 | Restricting CISD candidates to price pivots reduces spurious Bandz markings | raw Bandz vs opt-in pivot-qualified overlay |
| H2 | Permitting 1 opposing candle recovers valid CISDs the `min run = 2` default misses | fixed baseline vs 1-bar sensitivity |
| H3 | Shorter, candidate-specific expiry removes stale false confirmations | bounded 10/20-like research window vs legacy 60 bars |
| H4 | ATR-scaled opposing-delivery displacement reduces small/noisy candidates | filter off vs threshold bands, no hidden default |
| H5 | Invalidation by candidate pivot extreme better tracks the intended market structure | close-through-level vs pivot-price crossing |
| H6 | HTF C2/C3 and later DR/session checks improve *trade eligibility* without redefining raw CISD | retain full raw log, compare qualified subset |

## Validation fixtures and controls

- GBPUSD 2026-10-29 14:30 UTC: bullish Cephxs raw CISD and matching Bandz visual example; manually verify Bandz exact confirmation candle **close and level**.
- GBPUSD 2026-10-28 13:15–13:45 UTC: bearish waiting context terminated without bearish final.
- GBPUSD 2026-10-22 07:15 / 08:30 UTC: two bullish qualified events in one 4H context; compare raw CISDs separately.
- EURUSD 2026-09-21 09:30/09:45 NY: previously identified possible **bar-open vs confirm-close** labeling discrepancy, not automatically detector lag.
- Add 3+ bullish, 3+ bearish, and 3+ no-entry controls. Prefer cases where Bandz and Cephxs actually **disagree**, not just matching examples.

**Timing/feed:** reference event `t` is the webhook event-fire Unix ms. Pair with 15m candle CLOSE; don't mistake candle-open chart labels for delayed signaling. Check using the **same TradingView symbol/feed, exact settings and chart timezone**. FTMO M1 OHLC is useful for price reconstruction but is a different provider and does not prove tick-exact chart parity.

## Planned implementation (new commits only after user review)

1. Add an **opt-in, separate candidate lifecycle** to Bandz: candidate created / eligible / confirmed / expired / invalidated, for both directions. Keep original detector and C6 audit unchanged.
2. Add a compare panel or bounded event registry with immutable **confirmation close**, direction, line level, candidate pivot/extreme, age, ATR significance, raw vs qualified status and rejection reason. No lookahead or backdated signals.
3. Test live and historical TradingView Pine v6 compilation, stable close-only confirmations and unchanged legacy rendering when opt-in mode is off.
4. Decide whether the candidate rules should become one selectable Bandz detector mode. Keep separate C2/C3, DR, sessions and trade-eligibility filters.
5. Only then add independently authenticated Bandz event alerts into the Po3 Journal receiver. No live orders.

## Acceptance gate

- Repeatable on the same feed/configuration with exact confirmation-close comparisons, not visual similarity alone.
- Positive and negative fixtures, mismatch table (`MATCH`, `BANDZ_ONLY`, `REFERENCE_ONLY`, `LEVEL_DIFF`, `CLOSE_DIFF`, `UNVERIFIED`).
- At least one test in each direction where the original Bandz model fails but an alternative improves correctly **without introducing more false matches**.
- Preserve license attribution and **no user-provided proprietary source copied to the repository**.
- No changes to production or the baseline research branch; no claim about profitability.

## Separate research lanes

- Broker-executed positions belong in a **trade journal**. Po3 reference alerts are signals, not executed trades.
- Mado C3 dealing-range and London/NY session concepts can be studied as a separate, source-labeled qualification layer **after raw CISD rules are reproducible**. Do not presume content of unpublished transcripts.

**Scope principle:** Build a personal, testable model, not a proprietary clone.