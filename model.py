from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RuleWeights:
    market: float = 0.35
    recent: float = 0.2
    avg_finish: float = 0.15
    condition_fit: float = 0.15
    style_fit: float = 0.05
    trend: float = 0.05
    jockey: float = 0.03
    surface_fit: float = 0.02


def _clip01(v: float) -> float:
    return max(0.0, min(1.0, v))


def _score_from_finish(avg_finish: float | None) -> float:
    if avg_finish is None:
        return 0.4
    return _clip01((18 - avg_finish) / 18)


def _score_trend(trend: str) -> float:
    return {"改善": 0.7, "横ばい": 0.5, "悪化": 0.3}.get(trend, 0.45)


def _score_style(front_power: float, race_surface: str, race_distance: int | None) -> float:
    if race_surface == "ダート" or (race_distance and race_distance <= 1600):
        return _clip01(0.4 + 0.6 * front_power)
    return _clip01(0.3 + 0.7 * (1 - abs(front_power - 0.5)))


def estimate_win_probs(horses: list[dict[str, Any]], weights: RuleWeights = RuleWeights()) -> list[float]:
    raw_scores: list[float] = []
    for h in horses:
        market_prob = h.get("implied_prob", 0.0) or 0.0
        f = h.get("features", {})
        recent_score = _score_from_finish(f.get("直近3走平均着順"))
        avg_score = _score_from_finish(f.get("平均着順"))
        cond_fit = float(f.get("類似条件複勝率", 0.0))
        style_score = _score_style(float(f.get("先行力", 0.0)), h.get("race_surface", "不明"), h.get("race_distance"))
        trend_score = _score_trend(str(f.get("近走傾向", "不明")))
        jockey_score = 0.5
        surface_avg = f.get("芝平均着順") if h.get("race_surface") == "芝" else f.get("ダート平均着順")
        surface_score = _score_from_finish(surface_avg)

        score = (
            weights.market * market_prob
            + weights.recent * recent_score
            + weights.avg_finish * avg_score
            + weights.condition_fit * cond_fit
            + weights.style_fit * style_score
            + weights.trend * trend_score
            + weights.jockey * jockey_score
            + weights.surface_fit * surface_score
        )
        raw_scores.append(max(score, 1e-6))

    total = sum(raw_scores)
    return [s / total for s in raw_scores] if total > 0 else [1 / len(horses)] * len(horses)
