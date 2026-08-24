from dagster import Definitions, ScheduleDefinition, define_asset_job

from matchpulse_dagster.assets import flattened_exports, raw_matches, raw_standings, run_dbt_build

all_assets = [raw_matches, raw_standings, flattened_exports, run_dbt_build]

ingest_job = define_asset_job(
    name="ingest_and_transform",
    selection=all_assets,
)

daily_schedule = ScheduleDefinition(
    job=ingest_job,
    cron_schedule="0 6 * * *",
    name="daily_big_five_ingest",
)

defs = Definitions(
    assets=all_assets,
    jobs=[ingest_job],
    schedules=[daily_schedule],
)
