"""Pure reference model for one CLOSE-candle legacy CISD gate snapshot.

This does not execute Pine and is not an independent market-feed validation.
The ordering mirrors the legacy detector's *actual* condition and the
first-failed-predicate presented by the research-only skip audit.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class LegacyCisdSnapshot:
    side: str
    opening: float
    closing: float
    run_first_open: float | None
    run_last_open: float | None
    run_len: int
    run_age: int | None
    min_run: int = 2
    sensitivity: str = "Standard"
    already_on_bar: bool = False

@dataclass(frozen=True)
class Decision:
    direction_ok: bool
    level: float | None
    level_ok: bool
    min_run_ok: bool
    crossed: bool
    age_ok: bool
    unique_ok: bool
    confirmed: bool
    first_failure: str

def audit(s: LegacyCisdSnapshot) -> Decision:
    if s.side not in ("Bullish", "Bearish"):
        raise ValueError("side must be Bullish or Bearish")
    if s.sensitivity not in ("Standard", "Sensitive"):
        raise ValueError("sensitivity must be Standard or Sensitive")
    direction_ok = s.closing > s.opening if s.side == "Bullish" else s.closing < s.opening
    level = s.run_last_open if s.sensitivity == "Sensitive" else s.run_first_open
    level_ok = level is not None
    min_run_ok = s.run_len >= s.min_run
    crossed = level_ok and (s.closing > level if s.side == "Bullish" else s.closing < level)
    age_ok = s.run_age is not None and s.run_age <= 60
    unique_ok = not s.already_on_bar
    gates = [
        ("CANDLE_COLOR", direction_ok),
        ("NO_REFERENCE_LEVEL", level_ok),
        ("MIN_RUN", min_run_ok),
        ("NO_CLOSE_THROUGH", crossed),
        ("RUN_TOO_OLD", age_ok),
        ("ALREADY_ON_BAR", unique_ok),
    ]
    failed = next((reason for reason, passed in gates if not passed), "CONFIRMED")
    return Decision(direction_ok, level, level_ok, min_run_ok, crossed, age_ok,
                    unique_ok, failed == "CONFIRMED", failed)
