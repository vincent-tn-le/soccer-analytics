{{ config(materialized='table') }}

with teams as (
  select home_team_id as team_id, home_team_name as team_name, competition_code
  from {{ ref('stg_matches') }}
  union
  select away_team_id, away_team_name, competition_code
  from {{ ref('stg_matches') }}
  union
  select team_id, team_name, competition_code
  from {{ ref('stg_standings') }}
)

select distinct
  team_id,
  team_name,
  competition_code
from teams
where team_id is not null
