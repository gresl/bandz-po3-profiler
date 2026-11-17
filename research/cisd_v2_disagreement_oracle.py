"""Synthetic closed-event disagreement comparator for the opt-in Pine audit.

Independent Python reference for classification rules, not a Pine runtime or
Cephxs signal extractor. Synthetic bar indices are chart CLOSE identifiers.
"""
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class Signal:
    close_bar: int
    direction: str
    level: float
    state: str = "CONFIRMED"

@dataclass(frozen=True)
class Diff:
    category: str
    v2: Optional[Signal]
    legacy: Optional[Signal]

def compare(v2: list[Signal], legacy: list[Signal], *, cutoff: int = 0,
            tick: float = 0.00001, same_ticks: int = 3,
            near_ticks: int = 20) -> list[Diff]:
    """Greedy one-to-one exact-close matching, then +/-1 bar close matching.

    Both CONFIRMED and INVALIDATED V2 states retain confirmed-event status.
    Terminal/expired/superseded PENDING candidates are not confirmed signals.
    """
    is_final = {"CONFIRMED", "INVALIDATED"}
    v2 = [e for e in v2 if e.close_bar >= cutoff and e.state in is_final]
    legacy = [e for e in legacy if e.close_bar >= cutoff]
    used_v: set[int] = set()
    used_l: set[int] = set()
    results: list[Diff] = []
    for phase in (0, 1):
        for i, v in enumerate(v2):
            if i in used_v:
                continue
            choices = []
            for j, l in enumerate(legacy):
                if j in used_l or v.direction != l.direction:
                    continue
                time_gap = abs(v.close_bar-l.close_bar)
                level_ticks = abs(v.level-l.level)/tick
                eligible = time_gap == 0 if phase == 0 else (time_gap == 1 and level_ticks <= near_ticks+1e-7)
                if eligible:
                    choices.append((level_ticks, j))
            if choices:
                _, j = min(choices)
                l = legacy[j]
                used_v.add(i)
                used_l.add(j)
                if phase == 1:
                    category = "TIME_DIFF"
                elif abs(v.level - l.level) <= (same_ticks+1e-7)*tick:
                    category = "EXACT"
                else:
                    category = "LEVEL_DIFF"
                results.append(Diff(category, v, l))
    results.extend(Diff("V2_ONLY", v, None) for i, v in enumerate(v2) if i not in used_v)
    results.extend(Diff("LEGACY_ONLY", None, l) for j, l in enumerate(legacy) if j not in used_l)
    return results
