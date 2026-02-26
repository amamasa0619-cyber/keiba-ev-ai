from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
from bs4 import BeautifulSoup

from utils import normalize_distance, normalize_surface, parse_float, parse_int

REQUIRED_RACE_COLS = {
    "horse_name",
    "horse_no",
    "frame_no",
    "sex_age",
    "weight",
    "jockey",
    "trainer",
    "odds",
    "popularity",
}


def _coerce_horses(df: pd.DataFrame) -> list[dict[str, Any]]:
    horses: list[dict[str, Any]] = []
    for _, r in df.iterrows():
        horses.append(
            {
                "horse_name": str(r.get("horse_name", "")),
                "horse_no": parse_int(r.get("horse_no")),
                "frame_no": parse_int(r.get("frame_no")),
                "sex_age": str(r.get("sex_age", "")),
                "weight": parse_float(r.get("weight")),
                "jockey": str(r.get("jockey", "")),
                "trainer": str(r.get("trainer", "")),
                "odds": parse_float(r.get("odds")),
                "popularity": parse_int(r.get("popularity")),
            }
        )
    return horses


def _extract_histories(df: pd.DataFrame) -> dict[str, list[dict[str, Any]]]:
    if "horse_name" not in df.columns:
        return {}
    history_cols = {
        "race_date",
        "venue",
        "race_name",
        "surface",
        "distance",
        "track_condition",
        "finish",
        "field_size",
        "popularity",
        "last3f",
        "time",
        "margin",
        "corner_order",
    }
    if not history_cols.intersection(df.columns):
        return {}

    histories: dict[str, list[dict[str, Any]]] = {}
    for _, row in df.iterrows():
        horse_name = str(row.get("horse_name", "")).strip()
        if not horse_name:
            continue
        if pd.isna(row.get("race_date")):
            continue
        h = {
            "race_date": str(row.get("race_date", "")),
            "venue": str(row.get("venue", "")),
            "race_name": str(row.get("race_name", "")),
            "surface": normalize_surface(row.get("surface")),
            "distance": normalize_distance(row.get("distance")),
            "track_condition": str(row.get("track_condition", "")),
            "finish": parse_int(row.get("finish")),
            "field_size": parse_int(row.get("field_size")),
            "popularity": parse_int(row.get("popularity")),
            "last3f": parse_float(row.get("last3f")),
            "time": str(row.get("time", "")),
            "margin": parse_float(row.get("margin")),
            "corner_order": str(row.get("corner_order", "")),
        }
        histories.setdefault(horse_name, []).append(h)

    for horse in histories:
        histories[horse] = histories[horse][:10]
    return histories


def parse_race_csv(path: Path) -> dict[str, Any]:
    df = pd.read_csv(path)
    missing = REQUIRED_RACE_COLS - set(df.columns)
    if missing:
        raise ValueError(f"CSVに必須列が不足: {sorted(missing)}")

    race = {
        "race_name": str(df.get("race_name", pd.Series(["Unknown"])).iloc[0]),
        "race_date": str(df.get("race_date_meta", pd.Series([""])).iloc[0]),
        "venue": str(df.get("venue_meta", pd.Series([""])).iloc[0]),
        "surface": normalize_surface(df.get("surface_meta", pd.Series([""])).iloc[0]),
        "distance": normalize_distance(df.get("distance_meta", pd.Series([None])).iloc[0]),
        "horses": _coerce_horses(df.drop_duplicates(subset=["horse_name", "horse_no"])),
        "histories": _extract_histories(df),
    }
    return race


def parse_race_html(path: Path) -> dict[str, Any]:
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "lxml")
    script = soup.find("script", {"id": "race-data", "type": "application/json"})
    if not script:
        raise ValueError("保存HTML内にJSON(script#race-data)が見つかりません。CSV入力の利用を推奨します。")
    data = json.loads(script.text)
    data.setdefault("histories", {})
    return data
