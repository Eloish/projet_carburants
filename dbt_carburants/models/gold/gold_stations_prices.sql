{{ config(materialized='table', schema='gold') }}

select
    s.id,
    s.adresse,
    s.ville,
    s.cp,
    s.departement,
    s.region,
    s.code_departement,
    s.type_station,
    s.services,
    s.latitude,
    s.longitude,
    p.carburant,
    p.prix,
    p.date_maj,
    p.snapshot_date,
    s.date_collecte
from {{ ref('silver_stations') }} s
inner join {{ ref('silver_prices') }} p
    on s.id = p.station_id