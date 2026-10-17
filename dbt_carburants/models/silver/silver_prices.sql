{{ config(materialized='table', schema='silver') }}

{% set carburants = ['gazole', 'sp95', 'sp98', 'e10', 'e85', 'gplc'] %}

{% for c in carburants %}
select
    id as station_id,
    snapshot_date,
    '{{ c }}' as carburant,
    cast({{ c }}_prix as double precision) as prix,
    cast({{ c }}_maj as timestamp) as date_maj
from {{ source('raw', 'carburants_raw') }}
where {{ c }}_prix is not null
{% if not loop.last %}
union all
{% endif %}
{% endfor %}