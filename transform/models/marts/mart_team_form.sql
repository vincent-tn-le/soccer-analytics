{{ config(materialized='table') }}

-- Simple form proxy: points per game from current standings snapshot
select
  competition_code,
  team_id,
  team_name,
  played,
  points,
  case when played > 0 then round(points * 1.0 / played, 3) else null end as ppg,
  goal_diff,
  snapshot_at
from {{ ref('fct_standings_snapshot') }}
