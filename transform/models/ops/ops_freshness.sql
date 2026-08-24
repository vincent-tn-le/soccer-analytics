{{ config(materialized='table') }}

select
  competition_code,
  entity,
  extracted_at as last_extracted_at,
  payload_hash,
  path
from {{ ref('stg_extracts') }}
