{{ config(materialized='view') }}

select
  cast(match_id as bigint) as match_id,
  competition_code,
  cast(season as varchar) as season,
  cast(utc_date as timestamp) as utc_date,
  status,
  cast(matchday as integer) as matchday,
  cast(home_team_id as bigint) as home_team_id,
  home_team_name,
  cast(away_team_id as bigint) as away_team_id,
  away_team_name,
  cast(home_goals as integer) as home_goals,
  cast(away_goals as integer) as away_goals,
  winner,
  payload_hash,
  cast(extracted_at as timestamp) as extracted_at
from {{ export_csv('matches') }}
