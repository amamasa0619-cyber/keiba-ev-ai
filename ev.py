from __future__ import annotations

from typing import Any


def enrich_ev(horses: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for h in horses:
        odds = h.get("odds") or 0.0
        pred = h.get("pred_win_prob") or 0.0
        ev = pred * odds if odds else 0.0
        h2 = dict(h)
        h2["ev"] = ev
        h2["expected_return_pct"] = ev * 100
        out.append(h2)
    return out
