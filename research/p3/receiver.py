"""Small ASGI endpoint, loopback only until staging acceptance."""
import asyncio
import json
import logging
import os

import psycopg
from bandz_batch import MAX_BYTES
from storage import TOKEN, ingest

LOG = logging.getLogger("bandz_ingest")
PREFIX = "/bandz-hook/"


def make_app(dsn):
    async def app(scope, receive, send):
        if scope["type"] != "http":
            return

        async def respond(status, obj):
            body = json.dumps(obj, separators=(",", ":")).encode()
            await send({"type": "http.response.start", "status": status,
                        "headers": [(b"content-type", b"application/json"),
                                    (b"cache-control", b"no-store")]})
            await send({"type": "http.response.body", "body": body})

        path = scope["path"]
        if path == "/healthz" and scope["method"] == "GET":
            return await respond(200, {"status": "up"})
        token = path[len(PREFIX):] if path.startswith(PREFIX) else ""
        if TOKEN.fullmatch(token) is None:
            return await respond(404, {"status": "not_found"})
        if scope["method"] != "POST":
            return await respond(405, {"status": "method_not_allowed"})
        headers = scope["headers"]
        types = [v for k, v in headers if k.lower() == b"content-type"]
        lengths = [v for k, v in headers if k.lower() == b"content-length"]
        if len(types) != 1 or types[0].split(b";")[0].strip().lower() != b"application/json":
            return await respond(415, {"status": "unsupported_media_type"})
        if any(k.lower() == b"content-encoding" for k, _ in headers):
            return await respond(415, {"status": "unsupported_encoding"})
        if len(lengths) > 1 or (lengths and (not lengths[0].isdigit() or len(lengths[0]) > 8)):
            return await respond(400, {"status": "invalid_length"})
        if lengths and int(lengths[0]) > MAX_BYTES:
            return await respond(413, {"status": "invalid_size"})
        raw = bytearray()
        try:
            async with asyncio.timeout(1.5):
                while True:
                    msg = await receive()
                    if msg["type"] == "http.disconnect":
                        return
                    chunk = msg.get("body", b"")
                    if len(raw) + len(chunk) > MAX_BYTES:
                        return await respond(413, {"status": "invalid_size"})
                    raw.extend(chunk)
                    if not msg.get("more_body", False):
                        break
        except TimeoutError:
            return await respond(408, {"status": "body_timeout"})
        if lengths and len(raw) != int(lengths[0]):
            return await respond(400, {"status": "invalid_length"})
        if not raw:
            return await respond(400, {"status": "empty_body"})
        try:
            status, result = await asyncio.to_thread(ingest, dsn, token, bytes(raw))
        except Exception as exc:
            # Never log exception messages, headers, token, URI or payload.
            LOG.error("ingest failure class=%s", type(exc).__name__)
            return await respond(503, {"status": "unavailable"})
        return await respond(status, result)
    return app


def create_app():
    return make_app(os.environ["BANDZ_DSN"])
