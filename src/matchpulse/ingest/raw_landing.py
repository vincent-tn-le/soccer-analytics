"""Idempotent raw landing for API payloads."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class RawWriteResult:
    path: Path
    payload_hash: str
    wrote_new_file: bool
    competition_code: str
    entity: str


def payload_hash(payload: dict[str, Any] | list[Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def write_raw_json(
    raw_dir: Path,
    *,
    source: str,
    competition_code: str,
    entity: str,
    payload: dict[str, Any],
    extracted_at: datetime | None = None,
) -> RawWriteResult:
    """Write raw payload under data/raw/{source}/{competition}/{entity}/.

    Uses content-addressed filename when possible: if the same hash already
    exists for this entity, skip rewrite (idempotent).
    """
    extracted_at = extracted_at or datetime.now(timezone.utc)
    digest = payload_hash(payload)
    target_dir = raw_dir / source / competition_code / entity
    target_dir.mkdir(parents=True, exist_ok=True)

    # Prefer stable latest pointer + hash-named archive
    hash_path = target_dir / f"{digest[:16]}.json"
    latest_path = target_dir / "latest.json"
    envelope = {
        "source": source,
        "competition_code": competition_code,
        "entity": entity,
        "extracted_at": extracted_at.isoformat(),
        "payload_hash": digest,
        "payload": payload,
    }

    wrote_new = False
    if not hash_path.exists():
        hash_path.write_text(json.dumps(envelope, indent=2))
        wrote_new = True
    latest_path.write_text(json.dumps(envelope, indent=2))

    return RawWriteResult(
        path=latest_path,
        payload_hash=digest,
        wrote_new_file=wrote_new,
        competition_code=competition_code,
        entity=entity,
    )


def read_latest_raw(raw_dir: Path, source: str, competition_code: str, entity: str) -> dict[str, Any]:
    path = raw_dir / source / competition_code / entity / "latest.json"
    with path.open() as f:
        return json.load(f)
