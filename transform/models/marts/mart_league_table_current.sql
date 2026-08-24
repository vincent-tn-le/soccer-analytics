{{ config(materialized='table') }}

select
  competition_code,
  season,
  position,
  team_id,
  team_name,
  played,
  won,
  draw,
  lost,
  points,
  goals_for,
  goals_against,
  goal_diff,
  snapshot_at
from {{ ref('fct_standings_snapshot') }}
