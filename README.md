# MatchPulse — Big Five soccer analytics (DE MVP)

Data-engineering-first platform for Europe’s top five leagues: ingest → raw landing → Dagster → dbt (DuckDB) → Metabase.

**In MVP:** football-data.org adapter, idempotent raw JSON, Dagster assets, dbt dims/facts/marts, freshness ops table, Metabase via Compose.

**Later:** Redis live scores, Reddit match threads, Next.js, RAG.

## Quick start (passes)

### Pass 0 — repo + env

```bash
cd /path/to/soccer-analytics   # or this workspace
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
# Edit .env and set FOOTBALL_DATA_API_TOKEN from https://www.football-data.org/client/register
```

**Test Pass 0**

```bash
python -c "from matchpulse.config import load_settings; s=load_settings(); print(len(s.competitions), [c.code for c in s.competitions])"
# Expect: 5 ['PL', 'PD', 'SA', 'BL1', 'FL1']
```

### Pass 1 — config, adapter, raw landing (offline)

```bash
pytest tests/test_config_and_raw.py tests/test_seed_shape.py -q
python -m matchpulse.ingest.seed
python -m matchpulse.ingest.flatten
ls data/raw/football_data/PL/matches/latest.json
ls data/warehouse/export/
```

**Test Pass 1 (live API — needs token)**

```bash
python -m matchpulse.ingest.cli -c PL -e matches -e standings
python -m matchpulse.ingest.cli -c PL -e matches   # second run should print UNCHANGED if payload identical
```

### Pass 2 — Dagster ingest job (seed mode, no API)

```bash
export PYTHONPATH="$(pwd)/src:$(pwd)/orchestration:${PYTHONPATH:-}"
export DAGSTER_HOME="$(pwd)/orchestration/.dagster"
mkdir -p "$DAGSTER_HOME"

# Validate defs
dagster definitions validate -m matchpulse_dagster.definitions

# Materialize full graph using seed (no API token needed)
MATCHPULSE_USE_SEED=true dagster asset materialize \
  -m matchpulse_dagster.definitions \
  --select raw_matches raw_standings flattened_exports run_dbt_build
```

**Test Pass 2**

```bash
dagster definitions validate -m matchpulse_dagster.definitions
# Optional UI:
# MATCHPULSE_USE_SEED=true dagster dev -m matchpulse_dagster.definitions -h 127.0.0.1 -p 3001
```

### Pass 3 — dbt build + freshness

```bash
export MATCHPULSE_WAREHOUSE_PATH="$(pwd)/data/warehouse/matchpulse.duckdb"
export MATCHPULSE_EXPORT_DIR="$(pwd)/data/warehouse/export"
export MATCHPULSE_RAW_DIR="$(pwd)/data/raw"

python -m matchpulse.ingest.seed
python -m matchpulse.ingest.flatten

dbt build --project-dir transform --profiles-dir transform
```

**Test Pass 3**

```bash
dbt test --project-dir transform --profiles-dir transform
python - <<'PY'
import duckdb, os
con = duckdb.connect(os.environ["MATCHPULSE_WAREHOUSE_PATH"])
print(con.execute("select competition_code, count(*) from marts.fct_matches group by 1 order by 1").fetchall())
print(con.execute("select competition_code, entity, last_extracted_at from ops.ops_freshness order by 1,2").fetchdf())
PY
```

### Pass 4 — Compose (Metabase)

```bash
docker compose up -d
# Metabase: http://localhost:3000
# Add DuckDB or query CSVs under data/warehouse/export; or use duckdb CLI against matchpulse.duckdb
```

**Test Pass 4**

```bash
docker compose ps
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:3000
```

## Layout

```
config/competitions.yaml     # Big Five config
src/matchpulse/              # client, raw landing, flatten, CLI
orchestration/               # Dagster
transform/                   # dbt + DuckDB
data/raw/seed/               # offline fixtures
data/warehouse/              # duckdb + CSV exports
tests/
docker-compose.yml
```

## Remote

```bash
git remote -v
# origin  git@github.com:vincent-tn-le/soccer-analytics.git
```
