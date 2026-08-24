{{ config(materialized='view') }}

select
  competition_code,
  entity,
  cast(extracted_at as timestamp) as extracted_at,
  payload_hash,
  path
from {{ export_csv('extracts') }}
