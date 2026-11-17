"""Independent CLOSED-BAR reference model for Bandz CISD V2 research.

Synthetic-fixture-only testing. Not a broker/TradingView feed emulator, Pine compiler,
or a recreation of Cephxs implementation. All timestamps are explicit UTC
15m candle CLOSE timestamps, not Pine plot anchors.
"""
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional

@dataclass(frozen=True)
class Bar:
    opening: datetime
    open: float
    high: float
    low: float
    close: float

    @property
    def closing(self) -> datetime:
        return self.opening + timedelta(minutes=15)

@dataclass
class Event:
    bullish: bool
    origin: int
    pivot: int
    born: int
    level: float
    extreme: float
    state: str = "PENDING"
    confirmed_at: Optional[datetime] = None
    terminal_at: Optional[datetime] = None
    reason: str = "PENDING"


def evaluate(bars: list[Bar], *, pivot_len: int = 1, bridge: int = 2,
             max_scan: int = 12, min_run: int = 1, expiry: int = 10,
             min_range: float = 0.0) -> list[Event]:
    """Returns chronological candidate events. No future data used at any step."""
    events: list[Event] = []
    for i, b in enumerate(bars):
        p = i - pivot_len
        if p >= pivot_len:
            for bullish in (True, False):
                pivot_price = bars[p].low if bullish else bars[p].high
                left = range(p - pivot_len, p)
                right = range(p + 1, i + 1)
                if bullish:
                    is_pivot = all(bars[j].low > pivot_price for j in (*left, *right))
                else:
                    is_pivot = all(bars[j].high < pivot_price for j in (*left, *right))
                if not is_pivot:
                    continue
                recent = None
                for k in range(p, max(-1, p - bridge - 1), -1):
                    c = bars[k]
                    opp = c.close < c.open if bullish else c.close > c.open
                    if opp:
                        recent = k
                        break
                if recent is None:
                    continue
                origin = recent
                for k in range(recent - 1, max(-1, recent - max_scan - 1), -1):
                    c = bars[k]
                    opp = c.close < c.open if bullish else c.close > c.open
                    if not opp:
                        break
                    origin = k
                size = abs(bars[origin].open - bars[recent].close)
                if recent - origin + 1 < min_run or size < min_range:
                    continue
                for ev in events:
                    if ev.state == "PENDING" and ev.bullish == bullish:
                        ev.state = "SUPERSEDED"
                        ev.terminal_at = b.closing
                        ev.reason = "SUPERSEDED"
                events.append(Event(bullish, origin, p, i, bars[origin].open, pivot_price))
        for ev in events:
            if ev.state == "PENDING":
                breached = b.low < ev.extreme if ev.bullish else b.high > ev.extreme
                crossed = b.close > ev.level if ev.bullish else b.close < ev.level
                if breached:
                    ev.state, ev.terminal_at, ev.reason = "REJECTED", b.closing, "PIVOT_BREACH"
                elif i - ev.born >= expiry:
                    ev.state, ev.terminal_at, ev.reason = "EXPIRED", b.closing, "EXPIRED"
                elif crossed:
                    ev.state, ev.confirmed_at, ev.reason = "CONFIRMED", b.closing, "CONFIRMED"
            elif ev.state == "CONFIRMED" and i > ev.born:
                breached = b.low < ev.extreme if ev.bullish else b.high > ev.extreme
                if breached:
                    ev.state, ev.terminal_at, ev.reason = "INVALIDATED", b.closing, "INVALID_AFTER_CONFIRM"
    return events


def bars_from_ohlc(rows: list[tuple[float, float, float, float]]) -> list[Bar]:
    start = datetime(2026, 11, 11, 0, 0, tzinfo=timezone.utc)
    return [Bar(start + timedelta(minutes=15*i), *values) for i, values in enumerate(rows)]
