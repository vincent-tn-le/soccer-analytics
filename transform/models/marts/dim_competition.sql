{{ config(materialized='table') }}

select distinct
  competition_code as competition_id,
  competition_code,
  case competition_code
    when 'PL' then 'Premier League'
    when 'PD' then 'La Liga'
    when 'SA' then 'Serie A'
    when 'BL1' then 'Bundesliga'
    when 'FL1' then 'Ligue 1'
  end as competition_name
from {{ ref('stg_matches') }}
