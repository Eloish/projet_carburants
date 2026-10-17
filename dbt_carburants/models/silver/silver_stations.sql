{{ config(materialized='table', schema='silver') }}

with source_data as (
    select
        id,
        snapshot_date,
        nullif(trim(adresse), '') as adresse,
        nullif(trim(ville), '') as ville,
        nullif(trim(cp), '') as cp,
        nullif(trim(departement), '') as departement,
        nullif(trim(region), '') as region,
        nullif(trim(code_departement), '') as code_departement,

        -- Type de station (A = Autoroute, R = Route)
        nullif(trim(pop), '') as type_station,

        -- Services disponibles
        nullif(trim(services_service), '') as services,

        -- Coordonnées GPS nettoyées
        case
            when abs(cast(latitude as double precision)) > 1000
                then cast(latitude as double precision) / 100000.0
            else cast(latitude as double precision)
        end as latitude,

        case
            when abs(cast(longitude as double precision)) > 1000
                then cast(longitude as double precision) / 100000.0
            else cast(longitude as double precision)
        end as longitude,

        nullif(trim(carburants_disponibles), '') as carburants_disponibles,
        nullif(trim(horaires_automate_24_24), '') as horaires_automate_24_24,
        gazole_prix, sp95_prix, sp98_prix, e10_prix, e85_prix, gplc_prix
    from {{ source('raw', 'carburants_raw') }}
    where id is not null
)

-- Une seule ligne par station : la plus récente
select distinct on (id)
    id,
    adresse,
    ville,
    cp,
    departement,
    region,
    code_departement,
    type_station,
    services,
    latitude,
    longitude,
    carburants_disponibles,
    horaires_automate_24_24,
    snapshot_date as derniere_vue,
    current_timestamp as date_collecte
from source_data
where latitude is not null
    and longitude is not null
    and (
        gazole_prix is not null
        or sp95_prix is not null
        or sp98_prix is not null
        or e10_prix is not null
        or e85_prix is not null
        or gplc_prix is not null
    )
order by id, snapshot_date desc