"""Dagster assets: parameterized raw ingest + flatten + dbt build."""

import os
import subprocess

from dagster import AssetExecutionContext, MaterializeResult, asset

from matchpulse.clients.football_data import FootballDataOrgClient
from matchpulse.config import REPO_ROOT, load_settings
from matchpulse.ingest.flatten import flatten_to_csv
from matchpulse.ingest.raw_landing import write_raw_json
from matchpulse.ingest.seed import install_seed

SOURCE = "football_data"


def _use_seed() -> bool:
    return os.getenv("MATCHPULSE_USE_SEED", "false").lower() in {"1", "true", "yes"}


def _codes() -> list[str]:
    settings = load_settings(require_token=False)
    raw = os.getenv("MATCHPULSE_COMPETITIONS", "")
    if raw.strip():
        return [c.strip() for c in raw.split(",") if c.strip()]
    return [c.code for c in settings.competitions]


@asset(group_name="ingest")
def raw_matches(context: AssetExecutionContext) -> MaterializeResult:
    codes = _codes()
    if _use_seed():
        install_seed(competitions=codes)
        return MaterializeResult(metadata={"mode": "seed", "competitions": codes})

    settings = load_settings(require_token=True)
    results = []
    with FootballDataOrgClient(settings.api_token or "") as client:
        for code in codes:
            payload = client.get_matches(code, season=settings.season)
            result = write_raw_json(
                settings.raw_dir,
                source=SOURCE,
                competition_code=code,
                entity="matches",
                payload=payload,
            )
            results.append(
                {"competition": code, "hash": result.payload_hash[:12], "new": result.wrote_new_file}
            )
            context.log.info(
                "matches %s hash=%s new=%s", code, result.payload_hash[:12], result.wrote_new_file
            )
    return MaterializeResult(metadata={"mode": "api", "results": results})


@asset(group_name="ingest")
def raw_standings(context: AssetExecutionContext) -> MaterializeResult:
    codes = _codes()
    if _use_seed():
        install_seed(competitions=codes)
        return MaterializeResult(metadata={"mode": "seed", "competitions": codes})

    settings = load_settings(require_token=True)
    results = []
    with FootballDataOrgClient(settings.api_token or "") as client:
        for code in codes:
            payload = client.get_standings(code, season=settings.season)
            result = write_raw_json(
                settings.raw_dir,
                source=SOURCE,
                competition_code=code,
                entity="standings",
                payload=payload,
            )
            results.append(
                {"competition": code, "hash": result.payload_hash[:12], "new": result.wrote_new_file}
            )
            context.log.info(
                "standings %s hash=%s new=%s",
                code,
                result.payload_hash[:12],
                result.wrote_new_file,
            )
    return MaterializeResult(metadata={"mode": "api", "results": results})


@asset(group_name="ingest", deps=[raw_matches, raw_standings])
def flattened_exports(context: AssetExecutionContext) -> MaterializeResult:
    export_dir = flatten_to_csv()
    context.log.info("Flattened exports to %s", export_dir)
    return MaterializeResult(metadata={"export_dir": str(export_dir)})


@asset(group_name="transform", deps=[flattened_exports])
def run_dbt_build(context: AssetExecutionContext) -> MaterializeResult:
    settings = load_settings(require_token=False)
    transform_dir = REPO_ROOT / "transform"
    env = os.environ.copy()
    env["MATCHPULSE_RAW_DIR"] = str(settings.raw_dir)
    env["MATCHPULSE_WAREHOUSE_PATH"] = str(settings.warehouse_path)
    env["MATCHPULSE_EXPORT_DIR"] = str(settings.warehouse_path.parent / "export")

    cmd = [
        "dbt",
        "build",
        "--project-dir",
        str(transform_dir),
        "--profiles-dir",
        str(transform_dir),
    ]
    context.log.info("Running: %s", " ".join(cmd))
    proc = subprocess.run(cmd, cwd=str(REPO_ROOT), env=env, capture_output=True, text=True)
    if proc.stdout:
        context.log.info(proc.stdout)
    if proc.returncode != 0:
        context.log.error(proc.stderr)
        raise RuntimeError(f"dbt build failed:\n{proc.stderr}\n{proc.stdout}")
    return MaterializeResult(metadata={"dbt_returncode": 0})
