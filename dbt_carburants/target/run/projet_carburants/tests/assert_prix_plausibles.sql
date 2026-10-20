
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  

-- Renvoie les prix hors de la plage plausible (en euros par litre).
-- Le test passe s'il ne renvoie aucune ligne.
select
    station_id,
    carburant,
    snapshot_date,
    prix
from "carburants"."silver"."silver_prices"
where prix < 0.5
    or prix > 4
  
  
      
    ) dbt_internal_test