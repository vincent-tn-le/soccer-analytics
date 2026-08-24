"""Offline parse checks against seed-shaped payloads."""

from __future__ import annotations

import json
from pathlib import Path

from matchpulse.config import REPO_ROOT


def test_seed_matches_payload_shape() -> None:
    path = REPO_ROOT / "data/raw/seed/football_data/PL/matches_payload.json"
    data = json.loads(path.read_text())
    assert data["competition"]["code"] == "PL"
    assert len(data["matches"]) >= 1
    match = data["matches"][0]
    assert "homeTeam" in match and "awayTeam" in match
    assert "fullTime" in match["score"]


def test_seed_standings_payload_shape() -> None:
    path = REPO_ROOT / "data/raw/seed/football_data/PL/standings_payload.json"
    data = json.loads(path.read_text())
    table = data["standings"][0]["table"]
    assert table[0]["position"] == 1
    assert "points" in table[0]
