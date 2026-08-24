"""Flatten raw envelopes into tabular files for dbt."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from matchpulse.config import load_settings


def _latest_paths(raw_dir: Path, entity: str) -> list[Path]:
    root = raw_dir / "football_data"
    if not root.exists():
        return []
    return sorted(root.glob(f"*/{entity}/latest.json"))


def flatten_to_csv(export_dir: Path | None = None) -> Path:
    settings = load_settings(require_token=False)
    export_dir = export_dir or (settings.warehouse_path.parent / "export")
    export_dir.mkdir(parents=True, exist_ok=True)

    matches_path = export_dir / "matches.csv"
    standings_path = export_dir / "standings.csv"
    extracts_path = export_dir / "extracts.csv"

    match_rows: list[dict] = []
    standing_rows: list[dict] = []
    extract_rows: list[dict] = []

    for path in _latest_paths(settings.raw_dir, "matches"):
        envelope = json.loads(path.read_text())
        code = envelope["competition_code"]
        extract_rows.append(
            {
                "competition_code": code,
                "entity": "matches",
                "extracted_at": envelope["extracted_at"],
                "payload_hash": envelope["payload_hash"],
                "path": str(path),
            }
        )
        payload = envelope["payload"]
        for m in payload.get("matches", []):
            ft = (m.get("score") or {}).get("fullTime") or {}
            match_rows.append(
                {
                    "match_id": m.get("id"),
                    "competition_code": code,
                    "season": settings.season,
                    "utc_date": m.get("utcDate"),
                    "status": m.get("status"),
                    "matchday": m.get("matchday"),
                    "home_team_id": (m.get("homeTeam") or {}).get("id"),
                    "home_team_name": (m.get("homeTeam") or {}).get("name"),
                    "away_team_id": (m.get("awayTeam") or {}).get("id"),
                    "away_team_name": (m.get("awayTeam") or {}).get("name"),
                    "home_goals": ft.get("home"),
                    "away_goals": ft.get("away"),
                    "winner": (m.get("score") or {}).get("winner"),
                    "payload_hash": envelope["payload_hash"],
                    "extracted_at": envelope["extracted_at"],
                }
            )

    for path in _latest_paths(settings.raw_dir, "standings"):
        envelope = json.loads(path.read_text())
        code = envelope["competition_code"]
        extract_rows.append(
            {
                "competition_code": code,
                "entity": "standings",
                "extracted_at": envelope["extracted_at"],
                "payload_hash": envelope["payload_hash"],
                "path": str(path),
            }
        )
        for block in envelope["payload"].get("standings", []):
            if block.get("type") != "TOTAL":
                continue
            for row in block.get("table", []):
                team = row.get("team") or {}
                standing_rows.append(
                    {
                        "competition_code": code,
                        "season": settings.season,
                        "standing_type": block.get("type"),
                        "position": row.get("position"),
                        "team_id": team.get("id"),
                        "team_name": team.get("name"),
                        "played": row.get("playedGames"),
                        "won": row.get("won"),
                        "draw": row.get("draw"),
                        "lost": row.get("lost"),
                        "points": row.get("points"),
                        "goals_for": row.get("goalsFor"),
                        "goals_against": row.get("goalsAgainst"),
                        "goal_diff": row.get("goalDifference"),
                        "payload_hash": envelope["payload_hash"],
                        "extracted_at": envelope["extracted_at"],
                    }
                )

    def _write(path: Path, rows: list[dict]) -> None:
        if not rows:
            # write header-only friendly empty with known columns
            path.write_text("")
            return
        with path.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

    _write(matches_path, match_rows)
    _write(standings_path, standing_rows)
    _write(extracts_path, extract_rows)
    print(f"wrote {len(match_rows)} matches → {matches_path}")
    print(f"wrote {len(standing_rows)} standings → {standings_path}")
    print(f"wrote {len(extract_rows)} extracts → {extracts_path}")
    return export_dir


if __name__ == "__main__":
    flatten_to_csv()
