# P3B staging deployment

Target inventory 2026-11-24: Ubuntu 24.04.5 LTS / PostgreSQL 16.15;
po3-journal active at 127.0.0.1:8080, separate worker, LuxAlgo at 3000.
3.0 GiB available RAM and 80 GB available disk. Proposed Bandz listener 8081.
New Linux and PostgreSQL role bandzingest, peer authentication over Unix
socket. No password or production alert tokens required for local test.
No nginx configuration, firewall change or redirection of existing alerts.

Storage: exact authenticated raw bytes + SHA-256, source-scoped durable event
identity, event association per delivery. Identical events are duplicates,
conflicting IDs cause entire event savepoint rollback while retaining the
conflict delivery. 200 only after outer commit. Freshness policy chosen
for staging: 15 minutes old, 60 seconds ahead. This is a local policy,
not a TradingView guarantee; historical Preview payloads are not accepted
through the live endpoint. 40,960-byte cap, 32 events. Token format 64 lower
case hex characters, digest in DB. Unknown/disabled token creates no row.
Authorized invalid or stale body is retained only within size/type limits.

Before deploying: ensure names/schema/port unused, verify peer auth, inspect
effective public table privileges (including inherited PUBLIC privileges).
Use distro python3-psycopg and python3-uvicorn only after reviewing apt
simulation; separate application directory, no dependency changes in old venv.
Initial service binds only localhost; do not expose through nginx until
successful local duplicate/conflict/restart tests. Use synthetic source,
distinct from future live source; disable it after tests.
The role has no DELETE on event tables and no grants on public schema
tables. Existing PUBLIC grants must be checked on the real host.

TradingView webhook timeout is 3 seconds. Per-statement timeout and lock
timeout are not a global deadline; total request latency still needs
measurement. No claims of production latency or exactly-once delivery.
Provider failures, retry behavior, rate limits, token-safe reverse proxy
logging, TLS, retention, source version namespace and operational metrics
remain P3C gates. Native P2B revised build compiled per user; first real
qualified delivery pending.
