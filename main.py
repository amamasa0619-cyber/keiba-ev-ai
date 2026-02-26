from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Any

import pandas as pd

from betting import equal_stake, kelly_stake, recommendation_label
from ev import enrich_ev
from features import build_horse_features
from model import estimate_win_probs
from parser import parse_race_csv, parse_race_html
from scraper import load_race_from_url
from utils import setup_logging

logger = logging.getLogger(__name__)


def _implied_probs(horses: list[dict[str, Any]]) -> list[float]:
    probs = [(1.0 / h["odds"]) if h.get("odds") and h["odds"] > 0 else 0.0 for h in horses]
    s = sum(probs)
    return [p / s for p in probs] if s > 0 else [0.0] * len(horses)


def build_dataset(race: dict[str, Any]) -> list[dict[str, Any]]:
    horses: list[dict[str, Any]] = []
    implied = _implied_probs(race["horses"])
    for idx, horse in enumerate(race["horses"]):
        row = dict(horse)
        row["implied_prob"] = implied[idx]
        row["race_surface"] = race.get("surface")
        row["race_distance"] = race.get("distance")
        row["features"] = build_horse_features(row, race)
        horses.append(row)
    preds = estimate_win_probs(horses)
    for i, p in enumerate(preds):
        horses[i]["pred_win_prob"] = p
    horses = enrich_ev(horses)
    for h in horses:
        h["recommendation"] = recommendation_label(h)
    return sorted(horses, key=lambda x: x["ev"], reverse=True)


def render_console(race: dict[str, Any], rows: list[dict[str, Any]], budget: int) -> None:
    print(f"\n=== {race.get('race_name', 'Race')} ({race.get('venue', '-')}, {race.get('race_date', '-')}) ===")
    print("※期待値は推定値であり、利益を保証しません。")
    display = pd.DataFrame(
        [
            {
                "馬番": r.get("horse_no"),
                "馬名": r.get("horse_name"),
                "オッズ": r.get("odds"),
                "市場確率": round(r.get("implied_prob", 0) * 100, 2),
                "推定勝率": round(r.get("pred_win_prob", 0) * 100, 2),
                "EV": round(r.get("ev", 0), 3),
                "推奨度": r.get("recommendation"),
                "脚質": r.get("features", {}).get("想定脚質", "不明"),
            }
            for r in rows
        ]
    )
    print(display.to_string(index=False))

    print("\n--- 推奨買い目（均等） ---")
    print(equal_stake(rows, budget) or "該当なし")
    print("--- 推奨買い目（簡易ケリー 0.5） ---")
    print(kelly_stake(rows, budget, fraction=0.5) or "該当なし")


def to_output_csv(rows: list[dict[str, Any]], out_path: Path) -> None:
    records = []
    for r in rows:
        f = r.get("features", {})
        records.append(
            {
                "馬名": r.get("horse_name"),
                "馬番": r.get("horse_no"),
                "単勝オッズ": r.get("odds"),
                "市場確率": r.get("implied_prob"),
                "推定勝率": r.get("pred_win_prob"),
                "期待値": r.get("ev"),
                "推奨度": r.get("recommendation"),
                "推奨買い目金額(均等)": None,
                "芝/ダート実績要約": f"芝{f.get('芝出走回数', 0)}走 平均{f.get('芝平均着順', '-')}",
                "距離実績要約": f"同距離帯{f.get('同距離帯出走回数', 0)}走 平均{f.get('同距離帯平均着順', '-')}",
                "脚質要約": f"最多:{f.get('最多脚質', '不明')} 先行力:{round(f.get('先行力', 0), 2)}",
            }
        )
    pd.DataFrame(records).to_csv(out_path, index=False, encoding="utf-8-sig")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="競馬期待値分析CLI")
    p.add_argument("--url", type=str, help="レースURL")
    p.add_argument("--html", type=Path, help="保存済みHTML")
    p.add_argument("--csv", type=Path, help="CSV入力")
    p.add_argument("--output", type=Path, default=Path("output.csv"))
    p.add_argument("--budget", type=int, default=10000)
    p.add_argument("--verbose", action="store_true")
    return p.parse_args()


def load_race(args: argparse.Namespace) -> dict[str, Any]:
    if args.csv:
        return parse_race_csv(args.csv)
    if args.html:
        return parse_race_html(args.html)
    if args.url:
        return load_race_from_url(args.url, Path("fetched_race.html"))
    raise ValueError("--url / --html / --csv のいずれかを指定してください")


def main() -> None:
    args = parse_args()
    setup_logging(args.verbose)
    race = load_race(args)
    rows = build_dataset(race)
    render_console(race, rows, args.budget)
    to_output_csv(rows, args.output)
    logger.info("saved output to %s", args.output)


if __name__ == "__main__":
    main()
