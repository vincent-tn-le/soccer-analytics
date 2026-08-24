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
  extracted_at as snapshot_at
from {{ ref('stg_standings') }}
where standing_type = 'TOTAL'
