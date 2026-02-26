from __future__ import annotations

from typing import Any


def recommendation_label(row: dict[str, Any]) -> str:
    ev = row.get("ev", 0.0)
    prob = row.get("pred_win_prob", 0.0)
    if ev > 1.1 and prob >= 0.12:
        return "推奨本命"
    if ev > 1.0 and prob >= 0.05:
        return "穴馬候補"
    return "見送り"


def equal_stake(candidates: list[dict[str, Any]], budget: int) -> dict[str, int]:
    picks = [c for c in candidates if c.get("ev", 0) > 1.0]
    if not picks:
        return {}
    unit = budget // len(picks)
    return {p["horse_name"]: unit for p in picks}


def kelly_stake(candidates: list[dict[str, Any]], budget: int, fraction: float = 0.5) -> dict[str, int]:
    stakes: dict[str, int] = {}
    for c in candidates:
        p = c.get("pred_win_prob", 0.0)
        odds = c.get("odds", 0.0)
        b = max(odds - 1, 1e-6)
        kelly = (b * p - (1 - p)) / b
        alloc = max(0.0, kelly) * fraction
        stake = int(budget * alloc)
        if stake > 0:
            stakes[c["horse_name"]] = stake
    return stakes
