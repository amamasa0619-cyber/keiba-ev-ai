from __future__ import annotations

from collections import Counter
from typing import Iterable, Optional

from utils import parse_int

STYLE_NIGE = "逃げ"
STYLE_SENKO = "先行"
STYLE_SASHI = "差し"
STYLE_OIKOMI = "追込"
STYLE_UNKNOWN = "不明"


def _extract_positions(corner_order: object) -> list[int]:
    if corner_order is None:
        return []
    text = str(corner_order).strip()
    if not text:
        return []
    parts = [p for p in text.replace("-", ",").split(",") if p.strip()]
    positions: list[int] = []
    for part in parts:
        val = parse_int(part)
        if val is not None:
            positions.append(val)
    return positions


def classify_running_style(corner_order: object, field_size: Optional[int]) -> str:
    positions = _extract_positions(corner_order)
    if not positions or not field_size or field_size <= 0:
        return STYLE_UNKNOWN
    first = positions[0]
    fourth = positions[-1]
    rel = fourth / field_size
    if first <= 2 and rel <= 0.35:
        return STYLE_NIGE
    if rel <= 0.5:
        return STYLE_SENKO
    if rel <= 0.75:
        return STYLE_SASHI
    return STYLE_OIKOMI


def summarize_styles(styles: Iterable[str]) -> dict[str, object]:
    cnt = Counter([s for s in styles if s])
    total = sum(cnt.values())
    dominant = cnt.most_common(1)[0][0] if total else STYLE_UNKNOWN
    return {
        "逃げ回数": cnt.get(STYLE_NIGE, 0),
        "先行回数": cnt.get(STYLE_SENKO, 0),
        "差し回数": cnt.get(STYLE_SASHI, 0),
        "追込回数": cnt.get(STYLE_OIKOMI, 0),
        "最多脚質": dominant,
        "先行力": (cnt.get(STYLE_NIGE, 0) + cnt.get(STYLE_SENKO, 0)) / total if total else 0.0,
        "差し追込比率": (cnt.get(STYLE_SASHI, 0) + cnt.get(STYLE_OIKOMI, 0)) / total if total else 0.0,
    }
