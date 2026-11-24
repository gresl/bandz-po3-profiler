# P2B initial acceptance

P2A first live raw alert accepted 2026-11-24. P2B adds opt-in qualified
C2+CISD dispatch in Preview only. Existing P1 qualification predicate is
unchanged. Same envelope and ID namespace as P2A (additive event kind);
receiver compatibility not established. No live qualified dispatch yet.
Qualified events are independent of whether early notification was enabled.
Emitted qualified links populate the existing notified-link/C2 caches.

Native test: install new indicator separately, FOREXCOM:GBPUSD 15m/4H,
V2, Chart sequence slot; preserve P2A settings. Preview Nov 23 UTC,
raw OFF, early ON, qualified ON, other defaults. Replay through 10:15 UTC.
Expect five prior lifecycle notifications plus C2_CISD_QUALIFIED at 10:00
for 06:00 bearish C2, linked CISD 09:45, level 1.31231. Qualification must
share signal and link IDs with 09:45 early event; observed_ms must be
10:00, not 09:45. Earlier rejected 02:00 C2 must not qualify.
Export Pine Logs CSV. Do not replace P2A server alert.

Limitations: native Pine compile and regression pending. Prior P1A/P1B
timing discrepancy remains open. No proof of profitable entries.
Live qualified notification deliberately unavailable; separate acceptance
required before enabling it. No changes to receiver or production webhook.

## Native Preview acceptance — 24 November 2026

Export pine-logs-Bandz P2B_46aeb.csv: eight valid JSON rows, six unique event IDs, zero omitted/invalid identities. Reconstructed all signal, C2, link and event IDs exactly. Expected five P2A events plus qualified at 10:00 UTC (C2 start 06:00, CISD confirmation 09:45, origin 08:00, level 1.31231, close 1.31138). Earlier 02:00 C2 rejected, no qualification. Duplicate identical rows at 09:45 and 10:00 (same IDs, payloads and log timestamps); cause not established, not evidence of duplicate server delivery. Preview acceptance passed for this fixture; live qualification remains disabled. Receiver idempotency mandatory; native live qualification and restart behavior still untested.
