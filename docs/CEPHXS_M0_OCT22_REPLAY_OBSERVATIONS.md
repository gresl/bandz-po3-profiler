# M0-01 — 2026-10-22 EURUSD, matched replay observation

Status: **visual preliminary comparison, not passed PB parity**. Date of screenshots: 2026-10-26, 15:10–15:13 UTC-4; market date: 2026-10-22. The user supplied six successive matched screenshot pairs, one with `cephxs / Po3 [Ultimate+]` and one with `cephxs / CISD [base]` per checkpoint.

## Pair references (user's local screenshots, NOT copied into repository)

| Pair | Ultimate+ | Standalone [base] | Visible terminal quote from screenshot | Qualitative observation |
|---|---|---|---|---|
| 1 | image(20261026-191029).png | image(20261026-191036).png | ~1.12383 | Existing bearish red CISD line near 1.1242 on both; historical bullish cyan lines appear on both. |
| 2 | image(20261026-191057).png | image(20261026-191105).png | ~1.12437 | Red CISD reference near 1.1242 retained; price briefly rebounds. |
| 3 | image(20261026-191126).png | image(20261026-191131).png | ~1.12434 | Same primary red reference; price consolidates. |
| 4 | image(20261026-191208).png | image(20261026-191211).png | ~1.12336 | Breakdown produces another lower red reference; visible red lines broadly agree, but pixel-level exact price/time not captured. |
| 5 | image(20261026-191237).png | image(20261026-191249).png | ~1.12344 | Bounce after sell-off; blue and red marks need close-crop review for exact classification. |
| 6 | image(20261026-191303).png | image(20261026-191316).png | ~1.12280 | Bearish extension continues; primary CISD history appears broadly similar, with Po3-only C1/C2 and C3 overlay. |

## Findings (distinguish direct observation vs inference)

- Observed: same general price sequence and apparent red bearish CISD marks around **1.1242**. The standalone base draws multiple lower short red marks as the selloff develops.
- Observed: Po3 Ultimate+ additionally plots HTF/C1/C2/FVG and candle projections. Comparing these overlays to standalone is **not an engine-parity criterion**.
- **Not established**: exact equal level to 5 decimals, first confirmed 15m *close NY*, origin timestamps, original line width/PB class, and whether an older confirmed event is removed on reload.
- **No unequivocal PB-positive case** is demonstrable in these six paired checkpoints. This sequence may serve as a bearish regular-CISD / PB-negative control once original line widths and settings are verified; do not record `PB=no` as proven.
- The samples do not prove repainting or non-repainting. Replay forwards show event evolution but do not test reload persistence at the same historical endpoint.
- Neither source Settings pane nor Data Window readout appears in the 12 screenshots; settings are **assumed from the previous plan, not independently verified**.

## Interim classification and next action

`CISD_DIRECTIONAL_VISUAL_SIMILARITY / PB_UNCERTAIN / EVENT_TIME_UNVERIFIED`.

Do **not** change detector thresholds or implement PB based on this sample. Next capture **2026-10-08 bullish** case where an obvious thin PB was previously documented, preferably one fully zoomed matched pair when thin mark first appears, including Data Window / price level. Add **one PB-negative control**. For positive cases, note origin OPEN vs confirmation CLOSE and compare against standalone [base] at identical replay endpoint.

See M0 protocol: `docs/CEPHXS_BASE_PARITY_M0_PLAN.md`. Working Bandz Pine untouched.
