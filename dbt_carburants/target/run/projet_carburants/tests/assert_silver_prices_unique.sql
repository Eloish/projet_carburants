
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  -- Renvoie les combinaisons station x carburant x jour présentes plusieurs fois.
-- Le test passe s'il ne renvoie aucune ligne.
select
    station_id,
    carburant,
    snapshot_date,
    count(*) as nb
from "carburants"."silver"."silver_prices"
group by
    station_id,
    carburant,
    snapshot_date
having count(*) > 1
  
  
      
    ) dbt_internal_test