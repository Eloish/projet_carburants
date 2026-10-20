{{ config(severity='warn') }}

-- Renvoie les prix hors de la plage plausible (en euros par litre).
-- Le test passe s'il ne renvoie aucune ligne.
select
    station_id,
    carburant,
    snapshot_date,
    prix
from {{ ref('silver_prices') }}
where prix < 0.5
    or prix > 4