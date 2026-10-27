# M0-02 — 2026-10-08 EURUSD bullish CISD → thin PB candidate

**Status:** `VISUAL_MATCH / ONE_RECALCULATION_STABLE / PB_POSITIVE_CANDIDATE / EXACT_CLOSE_UNVERIFIED`. This is a **visual positive candidate**, not final parity acceptance or a no-repaint claim. Study screenshots captured 2026-10-26 15:26–15:30 UTC-4, in forward replay of 2026-10-08 (New York, EURUSD 15m).

## Supplied captures

| File (screenshots only; not stored in repository) | Indicator | Evidence |
|---|---|---|
| image(20261026-192609).png | cephxs / Po3 [Ultimate+] | Early bullish thicker cyan CISD reference near ~1.1183–1.1184 appears |
| image(20261026-192617).png | cephxs / CISD [base] | Same early bullish cyan reference on standalone |
| image(20261026-192729).png | cephxs / CISD [base] | Price advances; earlier cyan line persists; later upper cyan pending/faint mark becomes visible |
| image(20261026-193016).png | cephxs / Po3 [Ultimate+] | Earlier thick cyan line plus possible upper pending/faint mark; before the later solid cyan mark |
| image(20261026-193023).png | cephxs / Po3 [Ultimate+] | Later visibly thinner cyan line appears around ~1.1198–1.1200, above original thick ~1.1183 line |
| image(20261026-193033).png | cephxs / CISD [base] | Later visually thin cyan line in same price area, and lower thick cyan line remains |

## What is observed

1. Both indicators agree directionally on first thick cyan bullish CISD, and subsequently show a *second, thinner* cyan level above it. Close crops/pixel rows suggest the upper line has one saturated blue raster row while the earlier cyan line has two; pixel line-width can vary with render resolution and should be cross-checked by indicator setting/source semantics.
2. The upper level is in the neighborhood of **1.1198–1.1200** (estimated from right-hand price scale, NOT read to 5 decimals). The earlier lower level is ~**1.1183–1.1184**. They cannot be marked exact level equality from these screenshots alone.
3. The later cyan line is a **candidate PB** in both published Cephxs implementations. Standalone source's PB rule is a same-direction subsequent CISD with an opposing-run extreme within an earlier same-direction CISD zone, rendered thin (1px). This does **not** prove the parent-zone predicate fired: no per-event debug labels or data-window exact prices/timestamps were supplied.
4. Neither confirmed close NY nor first knowable appearance was isolated rigorously. Replay captures span more than one closed 15m bar and may show back-drawn anchors. Do not confuse **line origin timestamp** with **confirmation close timestamp**.
5. **Critical comparability caveat:** Early Po3 screenshot header shows `15m → 4H`, but the later zoomed Po3 screenshots (`193016`, `193023`) appear to show `15m → 1W`. Keep consistent `15m → 4H` on next confirmation capture, although raw standalone CISD marks may not depend on the Po3 selected profile.
6. Settings panels and exact feed details are not displayed in these screenshots. Assume nothing beyond source-name and chart title visible.
7. On the initial evidence set, same-endpoint indicator recalculation had not been checked. The subsequent 15:45 UTC-4 screenshots below now support **one visually stable toggle-off/on check**; this is not a proof of global non-repainting.

## Interpretation / next test

This is **our strongest candidate of a PB-positive match to date**. It is not final validation. Next capture one tight matched pair at exactly the same Replay endpoint with `15m → 4H` on Ultimate+, both indicators' sensitivity/size/purge controls noted, focused on the upper thin cyan line around 1.1198–1.1200. Note the replay-endpoint timestamp and exact level by crosshair/Data Window, and if possible prior parent CISD origin. Then reload each indicator without advancing replay and compare confirmed lines. Record a clear PB-negative control before M0 acceptance. Leave Bandz code/thresholds unchanged.

## M0-02b — Same-endpoint toggle / recalculation check (2026-10-26 15:45 UTC-4)

The user reports toggling **both indicators off/on**, without advancing the replay candles, and supplied four screenshots:
- `image(20261026-194527).png`, `image(20261026-194534).png`: two plain-price candles-only views with indicators hidden.
- `image(20261026-194548).png`: `cephxs / Po3 [Ultimate+]` re-enabled, shows visible lower thick cyan bullish CISD (~1.1184) and higher thin cyan bullish candidate PB (~1.1198).
- `image(20261026-194555).png`: `cephxs / CISD [base]` re-enabled, reproduces two bullish cyan levels at visually matching prices; short red bearish historical CISD levels are also shown on both.

**Result:** `SAME_REPLAY_ENDPOINT_RECALCULATION_VISUALLY_STABLE` for this single observed toggle test. The underlying price candles, rightmost chart position (~10:00 NY 15m candle, from screenshots), and two highlighted bullish line levels are consistent. No material change in those lines after toggle/recalculation is visible. The test does *not* show the exact market-time close when the upper line first qualified, the exact five-decimal level, or parent-zone validation; absence of global repaint is **not established**.

**Next gate:** one clearly bearish PB-positive example from `2026-10-22 00:00–08:00 NY` if found, plus a regular-CISD without PB control. Capture earliest confirmation at bar-by-bar Replay if achievable. Save full Settings and note NY candle label is bar *opening* time, not the bar-close timestamp. Maintain `15m → 4H` on Ultimate+; do not modify Bandz code at this stage.
