from __future__ import annotations

from typing import Any

from style_classifier import classify_running_style


def attach_style_to_histories(histories: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for h in histories[:10]:
        row = dict(h)
        row["running_style"] = classify_running_style(row.get("corner_order"), row.get("field_size"))
        out.append(row)
    return out
