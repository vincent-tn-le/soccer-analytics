"""Install seed raw envelopes so dbt can build without API calls."""

from __future__ import annotations

import json

from matchpulse.config import REPO_ROOT, load_settings
from matchpulse.ingest.raw_landing import write_raw_json

SEED_ROOT = REPO_ROOT / "data" / "raw" / "seed" / "football_data"


def install_seed(*, competitions: list[str] | None = None) -> None:
    settings = load_settings(require_token=False)
    codes = competitions or [c.code for c in settings.competitions]

    for code in codes:
        for entity in ("matches", "standings"):
            payload_path = SEED_ROOT / "PL" / f"{entity}_payload.json"
            payload = json.loads(payload_path.read_text())
            if code != "PL" and "competition" in payload:
                payload = json.loads(json.dumps(payload))
                payload["competition"]["code"] = code
                payload["competition"]["name"] = settings.get_competition(code).name
                if entity == "matches":
                    for i, m in enumerate(payload.get("matches", [])):
                        m["id"] = 500000 + (abs(hash(code)) % 10000) * 10 + i
            write_raw_json(
                settings.raw_dir,
                source="football_data",
                competition_code=code,
                entity=entity,
                payload=payload,
            )
            print(f"seeded {code}/{entity}")


def main() -> None:
    install_seed()


if __name__ == "__main__":
    main()
