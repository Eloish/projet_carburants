

select
    p.snapshot_date,
    s.region,
    s.departement,
    s.code_departement,
    s.type_station,
    p.carburant,
    count(distinct s.id) as nb_stations,
    round(avg(p.prix)::numeric, 3) as prix_moyen,
    min(p.prix) as prix_min,
    max(p.prix) as prix_max
from "carburants"."silver"."silver_stations" s
inner join "carburants"."silver"."silver_prices" p
    on s.id = p.station_id
group by
    p.snapshot_date,
    s.region,
    s.departement,
    s.code_departement,
    s.type_station,
    p.carburant