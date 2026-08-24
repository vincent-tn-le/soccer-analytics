{{ config(materialized='table') }}

select
  match_id,
  competition_code,
  season,
  utc_date,
  status,
  matchday,
  home_team_id,
  away_team_id,
  home_goals,
  away_goals,
  winner,
  case
    when home_goals > away_goals then home_team_id
    when away_goals > home_goals then away_team_id
    else null
  end as winning_team_id,
  extracted_at
from {{ ref('stg_matches') }}
