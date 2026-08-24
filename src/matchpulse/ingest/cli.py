"""CLI: ingest fixtures/standings for one or all Big Five competitions."""

from __future__ import annotations

import argparse
import sys

from matchpulse.clients.football_data import FootballDataOrgClient
from matchpulse.config import load_settings
from matchpulse.ingest.raw_landing import write_raw_json

SOURCE = "football_data"


def ingest_competition(code: str, *, entities: list[str]) -> None:
    settings = load_settings(require_token=True)
    comp = settings.get_competition(code)

    with FootballDataOrgClient(settings.api_token or "") as client:
        for entity in entities:
            if entity == "matches":
                payload = client.get_matches(comp.code, season=settings.season)
            elif entity == "standings":
                payload = client.get_standings(comp.code, season=settings.season)
            elif entity == "teams":
                payload = client.get_teams(comp.code, season=settings.season)
            else:
                raise ValueError(f"Unknown entity: {entity}")

            result = write_raw_json(
                settings.raw_dir,
                source=SOURCE,
                competition_code=comp.code,
                entity=entity,
                payload=payload,
            )
            status = "NEW" if result.wrote_new_file else "UNCHANGED"
            print(
                f"[{status}] {comp.code}/{entity} hash={result.payload_hash[:12]}… → {result.path}"
            )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ingest football-data.org raw payloads")
    parser.add_argument(
        "--competition",
        "-c",
        action="append",
        dest="competitions",
        help="Competition code (PL, PD, SA, BL1, FL1). Repeatable. Default: all.",
    )
    parser.add_argument(
        "--entity",
        "-e",
        action="append",
        dest="entities",
        choices=["matches", "standings", "teams"],
        help="Entity to pull. Repeatable. Default: matches+standings.",
    )
    args = parser.parse_args(argv)

    settings = load_settings(require_token=False)
    codes = args.competitions or [c.code for c in settings.competitions]
    entities = args.entities or ["matches", "standings"]

    for code in codes:
        ingest_competition(code, entities=entities)
    return 0


if __name__ == "__main__":
    sys.exit(main())
