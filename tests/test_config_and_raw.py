"""Unit tests for config + raw landing (no network)."""

from __future__ import annotations

import json
from pathlib import Path

from matchpulse.config import load_settings
from matchpulse.ingest.raw_landing import payload_hash, write_raw_json


def test_competitions_yaml_has_big_five() -> None:
    settings = load_settings(require_token=False)
    codes = {c.code for c in settings.competitions}
    assert codes == {"PL", "PD", "SA", "BL1", "FL1"}
    assert settings.season == "2025"


def test_raw_landing_idempotent(tmp_path: Path) -> None:
    payload = {"competition": {"code": "PL"}, "matches": [{"id": 1}]}
    first = write_raw_json(
        tmp_path, source="football_data", competition_code="PL", entity="matches", payload=payload
    )
    second = write_raw_json(
        tmp_path, source="football_data", competition_code="PL", entity="matches", payload=payload
    )
    assert first.payload_hash == second.payload_hash == payload_hash(payload)
    assert first.wrote_new_file is True
    assert second.wrote_new_file is False
    latest = json.loads((tmp_path / "football_data/PL/matches/latest.json").read_text())
    assert latest["payload"]["matches"][0]["id"] == 1
