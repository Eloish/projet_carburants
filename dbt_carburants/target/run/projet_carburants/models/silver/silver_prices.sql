
  
    

  create  table "carburants"."silver"."silver_prices__dbt_tmp"
  
  
    as
  
  (
    




select
    id as station_id,
    snapshot_date,
    'gazole' as carburant,
    cast(gazole_prix as double precision) as prix,
    cast(gazole_maj as timestamp) as date_maj
from "carburants"."public"."carburants_raw"
where gazole_prix is not null

union all


select
    id as station_id,
    snapshot_date,
    'sp95' as carburant,
    cast(sp95_prix as double precision) as prix,
    cast(sp95_maj as timestamp) as date_maj
from "carburants"."public"."carburants_raw"
where sp95_prix is not null

union all


select
    id as station_id,
    snapshot_date,
    'sp98' as carburant,
    cast(sp98_prix as double precision) as prix,
    cast(sp98_maj as timestamp) as date_maj
from "carburants"."public"."carburants_raw"
where sp98_prix is not null

union all


select
    id as station_id,
    snapshot_date,
    'e10' as carburant,
    cast(e10_prix as double precision) as prix,
    cast(e10_maj as timestamp) as date_maj
from "carburants"."public"."carburants_raw"
where e10_prix is not null

union all


select
    id as station_id,
    snapshot_date,
    'e85' as carburant,
    cast(e85_prix as double precision) as prix,
    cast(e85_maj as timestamp) as date_maj
from "carburants"."public"."carburants_raw"
where e85_prix is not null

union all


select
    id as station_id,
    snapshot_date,
    'gplc' as carburant,
    cast(gplc_prix as double precision) as prix,
    cast(gplc_maj as timestamp) as date_maj
from "carburants"."public"."carburants_raw"
where gplc_prix is not null


  );
  