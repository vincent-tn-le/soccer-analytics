"""MatchPulse config helpers."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

load_dotenv()

REPO_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Competition:
    code: str
    name: str
    country: str
    provider: str
    provider_id: int
    timezone: str
    subreddits: tuple[str, ...] = ()


@dataclass(frozen=True)
class Settings:
    api_token: str | None
    raw_dir: Path
    warehouse_path: Path
    config_path: Path
    season: str
    competitions: tuple[Competition, ...]

    def get_competition(self, code: str) -> Competition:
        for c in self.competitions:
            if c.code == code:
                return c
        raise KeyError(f"Unknown competition code: {code}")


def _repo_path(value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else REPO_ROOT / path


def load_settings(
    config_path: str | Path | None = None,
    *,
    require_token: bool = False,
) -> Settings:
    cfg_path = _repo_path(
        config_path or os.getenv("MATCHPULSE_CONFIG_PATH", "config/competitions.yaml")
    )
    with cfg_path.open() as f:
        raw: dict[str, Any] = yaml.safe_load(f)

    competitions = tuple(
        Competition(
            code=c["code"],
            name=c["name"],
            country=c["country"],
            provider=c["provider"],
            provider_id=int(c["provider_id"]),
            timezone=c["timezone"],
            subreddits=tuple(c.get("subreddits") or ()),
        )
        for c in raw["competitions"]
    )

    token = os.getenv("FOOTBALL_DATA_API_TOKEN")
    if token in (None, "", "your_token_here"):
        token = None
    if require_token and not token:
        raise RuntimeError(
            "FOOTBALL_DATA_API_TOKEN is required. Copy .env.example → .env and add your token."
        )

    return Settings(
        api_token=token,
        raw_dir=_repo_path(os.getenv("MATCHPULSE_RAW_DIR", "data/raw")),
        warehouse_path=_repo_path(
            os.getenv("MATCHPULSE_WAREHOUSE_PATH", "data/warehouse/matchpulse.duckdb")
        ),
        config_path=cfg_path,
        season=str(raw.get("season", "2025")),
        competitions=competitions,
    )
