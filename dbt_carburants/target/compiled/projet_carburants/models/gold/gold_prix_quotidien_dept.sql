

-- Une ligne par jour x département x carburant : la série temporelle du projet
select
    p.snapshot_date,
    s.code_departement,
    s.departement,
    s.region,
    p.carburant,
    count(distinct s.id) as nb_stations,
    round(avg(p.prix)::numeric, 4) as prix_moyen,
    round((percentile_cont(0.5) within group (order by p.prix))::numeric, 4) as prix_median
from "carburants"."silver"."silver_stations" s
inner join "carburants"."silver"."silver_prices" p
    on s.id = p.station_id
where p.prix between 0.5 and 4  -- écarte les prix aberrants
group by
    p.snapshot_date,
    s.code_departement,
    s.departement,
    s.region,
    p.carburant