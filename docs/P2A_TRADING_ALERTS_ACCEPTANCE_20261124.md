# P2A — Trading Alerts Engine prototype (2026-11-24)

Separate indicator: `indicators/Bandz_Po3_P2A_Alerts.pine`. Based on the P1B
branch, preserving original engine prefix except title. P1B and clean V2
are not replaced. No order automation, no qualified alerts, no webhook receiver
changes. First supported context: standard 15-minute chart, 4H source profile,
Chart CISD slot. V2 or Legacy selected engine; initial test V2 GBPUSD.

## Settings

| Setting | Default |
|---|---|
| Alerts mode | Off |
| Raw CISD confirmations | Off |
| Early C2 + CISD links | On |
| Structural C2 confirmed | Off |
| Reclaimed notified link | On |
| Rejected notified C2 | On |
| Ended notified link | On |
| Ended / untracked notified C2 | Off |
| Direction | Both |
| Preview log interval | 2026-11-23 00:00 to 2026-11-24 00:00 UTC (exclusive) |

Preview never calls alert(); it records selected JSON batches in Pine Logs.
Live calls alert() only on a confirmed realtime chart close; one batch per
bar. The P1 audit panel can remain OFF. Unsupported chart contexts are
suppressed with a Pine Logs warning. No alert event for linked-at-close,
linked-after-close or QUALIFIED in P2A.

## First native acceptance (no live alert or webhook needed)

1. Copy Raw Pine script into a NEW TradingView indicator; preserve P1B/V2.
2. FOREXCOM:GBPUSD, standard 15m, 4H source, V2, Sequence CISD from Chart,
   UTC. Preserve other P1B settings. Set Alerts mode = Preview, other
   P2A settings at defaults. Optionally keep P1 C2 summary enabled.
3. Replay to the same endpoint on Nov 23 (through 10:15 UTC); load preceding
   history. Open Pine Logs. Search for P2A_PREVIEW. Copy the lines or screenshot.
4. Expected conditional on identical detector/sequence inputs and replay
   history: 03:45 early link, 05:15 reclaim, 05:45 link ended, 06:00 C2 rejected,
   09:45 early link. 10:00 qualification must NOT produce an alert under
   these defaults. Raw 08:30 bullish CISD also not selected. Compare actual
   emitted IDs and times; do not treat these examples as forced outputs.
5. Optional single toggle Raw CISD confirmations ON: raw and early on same
   close must be retained together in one JSON batch. No need for another
   manual candle-by-candle study. If native compile fails send error.
6. Only after preview validation: exit Replay, set mode Live, create a
   technical alert on this indicator with "Any alert() function call",
   enable app notification. Do NOT set production webhook yet. Recreate
   alert after script/input changes; TradingView servers snapshot settings.

## Payload contract

One JSON object, schema bandz.po3.p2a.v1, with symbol (standard ticker ID),
chart_tf, anchor_tf, engine, bar_close_ms, bar_close_price, event_count,
omitted_count, invalid_identity_count and events array. Each event has event_id,
kind, side, observed_ms, c2_start_ms, cisd_close_ms, origin_open_ms, level,
signal_id, c2_id, link_id, reason. Missing applicable values use JSON null.
UTC timestamps are integer epoch milliseconds; levels formatted to tick size.
Raw IDs include side, confirmation timestamp, origin candle open, level,
symbol, chart TF and engine; C2 identity adds source HTF. Link combines C2
and signal. Event IDs add event kind and observed close. No bar_index in
identity. Equal price at different closes or origins is distinct. IDs are
deterministic for equivalent observed data/configuration; not a proof of
equivalence across different replay initialization or feed settings.
Receiver must enforce idempotency; bounded local caches are not durable.
Different parameter sets with identical event identities intentionally
share IDs; multi-profile configuration namespacing deferred to P3.

Reclaim/link-end only for early link emitted in this instance; reject/sequence
end only for earlier emitted C2. These are emission attempts, not receipt
acknowledgments. No retrospective notifications in Live. Preview starts its
notification state at preview-from, while collector warms up on earlier bars.
A restart/recreation loses local notification history. Max 512 remembered
IDs per cache; batch cap 32 events or 28k item characters, overflow reported
explicitly, not queued or retried. Missing origin identity fails closed.
P1 audit bounded and recalculated; same original sequence rules apply.

P2A is an experimental notification contract, NOT compatible by assertion
with the existing receiver's single-event schema. P3 must implement/verify
batch ingestion, authentication, replay protection, deduplication, routing,
and error handling before enabling a production webhook. The P1A/P1B
09:15 vs 09:45 discrepancy remains open. No native Pine execution in CI;
static source checks and independent Python fixtures only.

Vendor references:
- https://www.tradingview.com/pine-script-docs/concepts/alerts/
- https://www.tradingview.com/pine-script-docs/faq/alerts/
- https://www.tradingview.com/support/solutions/43000773947-alert-name-and-message-size-limits/
- https://www.tradingview.com/support/solutions/43000690939-alert-was-triggered-too-often-and-stopped/


## Native Preview acceptance — 24 November 2026

User supplied TradingView screenshots and pine-logs-Bandz P2A_0c2a5.csv.
Native compilation successful. FOREXCOM:GBPUSD / 15 / 240 / V2; audit
panel OFF; default alert selection; Preview mode. All five exported
messages parsed as valid JSON. Independently verified counts, unique IDs,
reconstructed C2/signal/link/event identities, UTC close timestamps and
null fields for structural rejection. Zero omitted and invalid identities.

| Log open UTC Nov 23 | Payload close UTC | Kind | C2 start UTC | CISD origin UTC | Level |
|---|---|---|---|---|---|
| 03:30 | 03:45 | C2_CISD_LINKED_EARLY | 02:00 | 03:00 | 1.31082 |
| 05:00 | 05:15 | C2_CISD_RECLAIMED | 02:00 | 03:00 | 1.31082 |
| 05:30 | 05:45 | C2_CISD_LINK_ENDED | 02:00 | 03:00 | 1.31082 |
| 05:45 | 06:00 | C2_REJECTED | 02:00 | null | null |
| 09:30 | 09:45 | C2_CISD_LINKED_EARLY | 06:00 | 08:00 | 1.31231 |

First three events share signal and link IDs; first four share C2 ID.
Reclaim reason CLOSE_BACK_THROUGH; link end C2_NEW_EXTREME_OR_LINK_CLEARED;
reject C2_CLOSED_OUTSIDE_C1. Raw and qualification events absent as expected.
Matches P1B event times, not proof of P1A parity. Each batch contains one
event; simultaneous native raw+early batching remains untested.

Next: one optional-but-useful native Preview run with Raw ON (same endpoint)
to prove batching; then Live mode, raw ON temporarily to speed up transport
smoke test, no webhook, no trade action, one GBPUSD alert via Any alert()
function call. Validate actual server alert message and close timestamp.
Return raw OFF and recreate alert after test. Follow-up notification
history is local to alert instance, so no historical followups expected.
Qualified dispatch and production receiver remain disabled/unmodified.
