{{ config(materialized='view') }}

select
  competition_code,
  cast(season as varchar) as season,
  standing_type,
  cast(position as integer) as position,
  cast(team_id as bigint) as team_id,
  team_name,
  cast(played as integer) as played,
  cast(won as integer) as won,
  cast(draw as integer) as draw,
  cast(lost as integer) as lost,
  cast(points as integer) as points,
  cast(goals_for as integer) as goals_for,
  cast(goals_against as integer) as goals_against,
  cast(goal_diff as integer) as goal_diff,
  payload_hash,
  cast(extracted_at as timestamp) as extracted_at
from {{ export_csv('standings') }}
