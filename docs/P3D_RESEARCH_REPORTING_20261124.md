# P3D preliminary research reporting

P3C local HTTPS staging passed 2026-11-24; real GBPUSD source registered,
awaiting first external TradingView delivery. No changes to installed
receiver, Nginx, live alerts, or public schema in this branch.

report.sql runs in a read-only transaction with UTC display and a bounded
statement timeout. Reports source health, quality counters, unique events,
duplicate associations, observed link lifecycle timing and a separate
inventory of existing normalized event types. No token or raw body shown.
Synthetic local-smoke sources excluded. The health report aggregates each
table separately to avoid delivery/event join multiplication.

Scope: observations only. Raw confirmations are not enabled on the real
P2B alert; unobserved events must not be interpreted as absent market
events. Follow-up emission depends on the live alert instance's memory and
selection switches. A missing early event, qualification, reclaim or
termination is unknown, not a loss or a confirmed active sequence.
Multiple links may belong to the same C2, and counts of linked observations
are not counts of trades. Duplicate associations count repeat accepted
event appearances, not distinct market signals. Omitted/invalid counters
sum reported envelope diagnostics across stored deliveries, including repeats.
No performance, win-rate, trade-entry or Cephxs parity conclusions from
this report. Cephxs event mapping and matched comparison windows require
separate validation using observed existing normalized event types, source
profiles, and actual signal coverage. No inferred equivalence by timestamp.

Next: run report on actual host after external delivery; inspect alert
snapshot settings and coverage, confirm backup inclusion of bandz_ingest
schema and restore test. P3C external acceptance remains pending. Do not
switch on extra raw alerts just to produce data unless specifically testing.
