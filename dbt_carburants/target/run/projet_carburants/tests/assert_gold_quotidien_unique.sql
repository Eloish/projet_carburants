
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  -- Renvoie les combinaisons jour x département x carburant présentes plusieurs fois.
-- Le test passe s'il ne renvoie aucune ligne.
select
    snapshot_date,
    code_departement,
    carburant,
    count(*) as nb
from "carburants"."gold"."gold_prix_quotidien_dept"
group by
    snapshot_date,
    code_departement,
    carburant
having count(*) > 1
  
  
      
    ) dbt_internal_test