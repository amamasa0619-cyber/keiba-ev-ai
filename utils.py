from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Iterable, Optional


LOGGER_NAME = "keiba_ev"


def setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    )


def parse_int(value: object) -> Optional[int]:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    match = re.search(r"-?\d+", text.replace(",", ""))
    return int(match.group(0)) if match else None


def parse_float(value: object) -> Optional[float]:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    match = re.search(r"-?\d+(?:\.\d+)?", text.replace(",", ""))
    return float(match.group(0)) if match else None


def normalize_surface(text: object) -> str:
    if text is None:
        return "不明"
    t = str(text)
    if "芝" in t:
        return "芝"
    if "ダ" in t or "ダート" in t:
        return "ダート"
    return "不明"


def normalize_distance(value: object) -> Optional[int]:
    return parse_int(value)


def safe_mean(values: Iterable[Optional[float]]) -> Optional[float]:
    nums = [v for v in values if v is not None]
    return sum(nums) / len(nums) if nums else None


def to_percentage(value: Optional[float], ndigits: int = 1) -> str:
    if value is None:
        return "-"
    return f"{value * 100:.{ndigits}f}%"


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
