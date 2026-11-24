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
