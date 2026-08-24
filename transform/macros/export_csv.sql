{% macro export_csv(name) %}
read_csv_auto('{{ env_var("MATCHPULSE_EXPORT_DIR", "../data/warehouse/export") }}/{{ name }}.csv', header=true)
{% endmacro %}
