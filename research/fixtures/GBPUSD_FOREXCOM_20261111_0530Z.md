# Fixture: GBPUSD 2026-11-11 05:30–05:45 UTC

**Type:** observed Bandz audit + Cephxs chart reference; **not** a full OHLC fixture. Do not present as a validated parity test.

| Item | Value | Evidence |
|---|---|---|
| Chart symbol/feed | `FOREXCOM:GBPUSD` | Bandz C6 audit |
| Chart timeframe | 15 minutes | TradingView screenshots |
| Candle OPEN | 2026-11-11 05:30 UTC | Chart axis / audit |
| Candle CLOSE | 2026-11-11 05:45 UTC | Bandz C6 audit |
| Bandz direction | bearish | Bandz audit |
| Bandz raw reference level | 1.33454 | Bandz audit |
| Bandz confirmation close price | ~1.33440 | Bandz audit (rounding) |
| Bandz confirmed close | 2026-11-11 05:45 UTC | Bandz fixed-close selector |
| Cephxs line direction | bearish | Cephxs-only screenshot |
| Cephxs line confirmation timestamp | **UNKNOWN** | Draw anchor is not event-fire time |
| Cephxs intrabar provisional first-observed time | **UNKNOWN** | No captured tick-by-tick live log |
| Price after 05:45 | Not used to classify at-close event | Anti-hindsight requirement |

### What is known

Bandz independently logs this event, including later-event registry selection. Cephxs shows a bearish red line in the same area, but neither its origin x-coordinate nor a static screenshot proves it fired 15 minutes before Bandz. The chart's 05:30 label is candle OPEN, while the Bandz audit prints candle CLOSE.

### Next capture

1. Run new V2 **alongside** legacy Bandz at the same replay endpoint after the candle closes.
2. Capture the V2 table, whether a V2 candidate was born, and its confirmation close.
3. Obtain an authorized exact-feed 15m OHLC export if possible. The currently captured screenshots do not provide a dependable full OHLC series.
4. For early warning: log provisional signal appearance during real incoming ticks and distinguish from 05:45 closed-bar confirmation.
5. Do NOT mark MATCH / LEVEL_DIFF / TIME_DIFF until both confirmed event times and levels are independently observed.

## Related controls

- Positive bearish: Nov 11 2026 07:45 UTC Bandz 1.33300; 13:15 UTC Bandz 1.33095.
- Positive bullish: Nov 12 2026 07:30 UTC Bandz 1.32606.
- Earlier October fixtures: see `docs/CISD_V2_NOV2026_RESEARCH_SPEC.md`.
- Negative controls: 2026-10-28 13:15–13:45 UTC bearish waiting without final; verify exact reference event semantics before using it as a raw-CISD negative.
