"""Strict Bandz P2A/P2B batch decoder. No network or database side effects.

The caller must authenticate the registered source before invoking decode.
Decimal preserves the price representation emitted by Pine format.mintick.
"""
from dataclasses import dataclass
from decimal import Decimal, DecimalException
import json
import re

SCHEMA = "bandz.po3.p2a.v1"
MAX_BYTES = 40960
MAX_EVENTS = 32
LINK_KINDS = {
    "C2_CISD_LINKED_EARLY", "C2_CISD_QUALIFIED",
    "C2_CISD_RECLAIMED", "C2_CISD_LINK_ENDED",
}
C2_KINDS = {
    "C2_CONFIRMED", "C2_REJECTED",
    "C2_SEQUENCE_ENDED", "C2_SEQUENCE_UNTRACKED",
}
ENVELOPE = {
    "schema", "symbol", "chart_tf", "anchor_tf", "engine", "bar_close_ms",
    "bar_close_price", "event_count", "omitted_count",
    "invalid_identity_count", "events",
}
EVENT = {
    "event_id", "kind", "side", "observed_ms", "c2_start_ms",
    "cisd_close_ms", "origin_open_ms", "level", "signal_id",
    "c2_id", "link_id", "reason",
}


class InvalidBatch(ValueError):
    pass


@dataclass(frozen=True)
class Source:
    symbol: str
    chart_tf: str = "15"
    anchor_tf: str = "240"
    engine: str = "V2"
    # ForexCOM GBPUSD/EURUSD/AUDUSD tick precision. Set per registered source.
    price_places: int = 5


def require(ok, reason):
    if not ok:
        raise InvalidBatch(reason)


def object_pairs(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def bad_constant(_):
    raise InvalidBatch("nonfinite JSON constant")


def integer(value, name, lo=0, hi=2**63-1):
    require(type(value) is int and lo <= value <= hi, name)
    return value


def timestamp(value, name):
    return integer(value, name, 946684800000, 4102444800000)


def price(value, places):
    require(type(value) in (int, Decimal), "invalid price type")
    d = Decimal(value)
    require(d.is_finite() and 0 < d < 10000000, "invalid price")
    require(d.as_tuple().exponent >= -places, "price precision")
    return format(d, f".{places}f")


def decode(raw: bytes, source: Source):
    """Return validated envelope, with original Decimal values preserved.

    No historical-age check here: Preview imports and live acceptance use
    different policies. Live transport must enforce its own freshness policy.
    """
    require(isinstance(raw, bytes) and 0 < len(raw) <= MAX_BYTES, "body size")
    require(0 <= source.price_places <= 10, "source precision")
    try:
        b = json.loads(raw.decode("utf-8"), parse_float=Decimal,
                       parse_constant=bad_constant, object_pairs_hook=object_pairs)
    except (UnicodeError, ValueError, RecursionError, DecimalException) as exc:
        raise InvalidBatch("invalid JSON") from exc
    require(type(b) is dict and set(b) == ENVELOPE, "envelope fields")
    require(b["schema"] == SCHEMA, "schema")
    require((b["symbol"], b["chart_tf"], b["anchor_tf"], b["engine"]) ==
            (source.symbol, source.chart_tf, source.anchor_tf, source.engine),
            "source mismatch")
    require(source.chart_tf == "15" and source.anchor_tf == "240" and
            source.engine in ("V2", "Legacy"), "unsupported profile")
    close = timestamp(b["bar_close_ms"], "bar close")
    price(b["bar_close_price"], source.price_places)
    n = integer(b["event_count"], "event count", 0, MAX_EVENTS)
    omitted = integer(b["omitted_count"], "omitted count", 0, 10000)
    invalid = integer(b["invalid_identity_count"], "invalid identity count", 0, 10000)
    require(type(b["events"]) is list and len(b["events"]) == n, "count mismatch")
    require(n + omitted + invalid > 0, "empty batch")
    stream = f"{source.symbol}|{source.chart_tf}|{source.engine}"
    context = f"{stream}|{source.anchor_tf}"
    seen = set()
    for e in b["events"]:
        require(type(e) is dict and set(e) == EVENT, "event fields")
        kind = e["kind"]
        require(type(kind) is str and
                (kind == "CISD_CONFIRMED" or kind in LINK_KINDS or kind in C2_KINDS),
                "event kind")
        require(e["side"] in ("BULL", "BEAR"), "side")
        side = 1 if e["side"] == "BULL" else -1
        observed = timestamp(e["observed_ms"], "observed time")
        require(observed == close, "event/bar mismatch")
        require(type(e["reason"]) is str and 0 < len(e["reason"]) <= 128, "reason")
        raw_event = kind == "CISD_CONFIRMED"
        has_signal = raw_event or kind in LINK_KINDS
        sig = c2 = link = None
        if has_signal:
            confirmed = timestamp(e["cisd_close_ms"], "CISD close")
            origin = timestamp(e["origin_open_ms"], "origin open")
            require(origin < confirmed <= observed, "signal chronology")
            level = price(e["level"], source.price_places)
            sig = f"{stream}|{side}|{confirmed}|{origin}|{level}"
            if raw_event:
                require(confirmed == observed, "raw confirmation time")
        else:
            require(all(e[k] is None for k in ("cisd_close_ms", "origin_open_ms", "level")),
                    "structural event signal fields")
        if raw_event:
            require(e["c2_start_ms"] is None, "raw event C2")
        else:
            start = timestamp(e["c2_start_ms"], "C2 start")
            require(start <= observed, "C2 chronology")
            c2 = f"{context}|{side}|{start}"
            if has_signal:
                link = f"{c2}|{sig}"
        require((e["signal_id"], e["c2_id"], e["link_id"]) == (sig, c2, link),
                "identity mismatch")
        key = sig if raw_event else link if has_signal else c2
        eid = f"p2a1|{kind}|{key}|{observed}"
        require(e["event_id"] == eid, "event ID mismatch")
        require(eid not in seen, "duplicate event within batch")
        seen.add(eid)
    return b
