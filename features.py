from __future__ import annotations

from collections import Counter
from statistics import mean
from typing import Any

from horse_history import attach_style_to_histories
from style_classifier import summarize_styles


DIST_BANDS = {
    "短距離": (1000, 1400),
    "マイル": (1401, 1800),
    "中距離": (1801, 2400),
    "長距離": (2401, 4000),
}


def _distance_band(distance: int | None) -> str:
    if distance is None:
        return "不明"
    for name, (mn, mx) in DIST_BANDS.items():
        if mn <= distance <= mx:
            return name
    return "不明"


def _finish_trend(last_finishes: list[int]) -> str:
    if len(last_finishes) < 2:
        return "不明"
    if last_finishes[-1] < last_finishes[0]:
        return "改善"
    if last_finishes[-1] > last_finishes[0]:
        return "悪化"
    return "横ばい"


def build_horse_features(horse: dict[str, Any], race: dict[str, Any]) -> dict[str, Any]:
    histories = attach_style_to_histories(race.get("histories", {}).get(horse["horse_name"], []))
    finishes = [h["finish"] for h in histories if isinstance(h.get("finish"), int)]
    last3 = finishes[:3]

    same_cond = [
        h
        for h in histories
        if h.get("surface") == race.get("surface")
        and h.get("distance")
        and race.get("distance")
        and abs(h["distance"] - race["distance"]) <= 200
    ]

    surface_records = {
        s: [h["finish"] for h in histories if h.get("surface") == s and isinstance(h.get("finish"), int)]
        for s in ("芝", "ダート")
    }

    band_counter = Counter(_distance_band(h.get("distance")) for h in histories)
    style_stats = summarize_styles([h.get("running_style", "不明") for h in histories])
    trend = _finish_trend(last3)

    feats: dict[str, Any] = {
        "過去走数": len(histories),
        "平均着順": mean(finishes) if finishes else None,
        "直近3走平均着順": mean(last3) if last3 else None,
        "勝利数": sum(1 for f in finishes if f == 1),
        "複勝圏内回数": sum(1 for f in finishes if f <= 3),
        "着外回数": sum(1 for f in finishes if f > 3),
        "同距離帯出走回数": len(same_cond),
        "同距離帯平均着順": mean([h["finish"] for h in same_cond if h.get("finish")]) if same_cond else None,
        "距離帯成績": dict(band_counter),
        "芝出走回数": len(surface_records["芝"]),
        "芝平均着順": mean(surface_records["芝"]) if surface_records["芝"] else None,
        "ダート出走回数": len(surface_records["ダート"]),
        "ダート平均着順": mean(surface_records["ダート"]) if surface_records["ダート"] else None,
        "類似条件勝率": sum(1 for h in same_cond if h.get("finish") == 1) / len(same_cond) if same_cond else 0.0,
        "類似条件連対率": sum(1 for h in same_cond if (h.get("finish") or 99) <= 2) / len(same_cond) if same_cond else 0.0,
        "類似条件複勝率": sum(1 for h in same_cond if (h.get("finish") or 99) <= 3) / len(same_cond) if same_cond else 0.0,
        "直近3走着順": last3,
        "近走傾向": trend,
        "想定脚質": style_stats["最多脚質"],
        "直近3走脚質傾向": [h.get("running_style", "不明") for h in histories[:3]],
    }
    feats.update(style_stats)
    return feats
