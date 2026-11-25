# P3C HTTPS staging

P3B accepted on actual VPS, including restart persistence. New Nginx
route only: `/bandz-hook/` to loopback port 8081. Existing /hook/ and
journal routes unchanged. Verified existing safe logging format and
absence of real IP directives in supplied inventory. Verify recent
successful POSTs from TradingView sender IPs in existing safe log
before applying allowlist. Local getent resolves 127.0.1.1, not public
DNS evidence; do not assume external DNS or proxy topology from it.

Install bandz-http.conf in conf.d, bandz-location.conf in snippets,
include location snippet inside webhook.grecea.net HTTPS server only.
Check nginx -t, reload gracefully, verify authenticated synthetic
batch through local TLS with certificate verification, repeat duplicate
and conflict smoke, unknown token rejected. Keep loopback allow for
authenticated diagnostics. No public health route. Limit 40 KiB,
5 r/s per sender IP burst 10, no delaying; timeouts are individual
operation limits, not a total deadline. Separate safe log contains
no request URI, query or token. Error log suppressed at route;
existing server-level safe logging preserved. Ensure other
infrastructure (e.g. CDN) does not log secret path. Review logrotate
and backup retention. Do not paste token into chat, logs or GitHub.

Only after HTTPS smoke passes register a fresh high-entropy per-source
token and enable the new webhook on existing P2B live alert. Start with
GBPUSD 15/240 V2, no changes to existing Cephxs delivery or P2A alerts.
First actual provider delivery still required for P3C acceptance.
No trade execution. No live qualified delivery proof yet.

References:
https://www.tradingview.com/support/solutions/43000529348-how-to-configure-webhook-alerts/
https://nginx.org/en/docs/http/ngx_http_access_module.html
https://nginx.org/en/docs/http/ngx_http_limit_req_module.html
https://nginx.org/en/docs/http/ngx_http_proxy_module.html

## VPS HTTPS acceptance — 24 November 2026

Pinned nginx configuration commit c76c8e7ab7ba33b3172d976609a8fdd9b7d7ee1e
installed. Existing safe log showed 109 successful POSTs from published
TradingView sender IPs. Public DNS lookup returned an address; no change
made to existing DNS or routes. nginx -t/reload passed; nginx, Bandz,
existing receiver and worker all active. Local HTTPS synthetic source 3:
HTTP 200 two inserts (12 ms), HTTP 200 two duplicates (10 ms), HTTP 409
conflict (8 ms), HTTP 404 unknown token (6 ms). Counts 2|3|4|1; source
subsequently disabled. TLS verification enabled. Safe log showed method,
status, timing, upstream status, no URI or token. Real GBPUSD 15/240 V2
source 4 registered and user reports URL configured in P2B alert. Initial
query zero deliveries/events; no Bandz external delivery confirmed yet.
No need to generate artificial live market signals. Keep P2B running.
P3C local deployment accepted, external provider delivery pending.
Backup and retention verification and passive monitoring remain open.

## First external delivery evidence — 25 November 2026
Seven TradingView POSTs from allowlisted addresses 52.89.214.238 and 54.218.53.128 between 24 Nov 20:45:06 UTC and 25 Nov 06:15:03 UTC all returned HTTP 200/upstream 200. Nginx request times 201–459 ms, upstream 5–7 ms. External transport smoke passed. Database event contents, diagnostic counters, qualification and market quality remain to be inspected; seven deliveries are not seven trades. No claim of full lifecycle or strategy acceptance.
