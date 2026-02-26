from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import requests

from parser import parse_race_html

LOGGER = logging.getLogger(__name__)
DEFAULT_UA = "keiba-ev-analyzer/1.0 (+offline-first; respect-robots)"


@dataclass
class FetchConfig:
    timeout: int = 10
    retries: int = 2
    sleep_sec: float = 1.5
    user_agent: str = DEFAULT_UA


def fetch_race_page(url: str, config: Optional[FetchConfig] = None) -> str:
    cfg = config or FetchConfig()
    headers = {"User-Agent": cfg.user_agent}
    last_err: Exception | None = None
    for i in range(cfg.retries + 1):
        try:
            response = requests.get(url, headers=headers, timeout=cfg.timeout)
            response.raise_for_status()
            return response.text
        except Exception as exc:  # noqa: BLE001
            last_err = exc
            LOGGER.warning("fetch failed (%s/%s): %s", i + 1, cfg.retries + 1, exc)
            time.sleep(cfg.sleep_sec)
    raise RuntimeError(f"URL取得に失敗しました: {last_err}")


def fetch_to_html_file(url: str, output_path: Path, config: Optional[FetchConfig] = None) -> Path:
    html = fetch_race_page(url, config=config)
    output_path.write_text(html, encoding="utf-8")
    return output_path


def load_race_from_url(url: str, temp_path: Path) -> dict:
    LOGGER.info("利用規約・robots.txtを遵守してください。制限がある場合は --html/--csv を使ってください。")
    fetch_to_html_file(url, temp_path)
    return parse_race_html(temp_path)
