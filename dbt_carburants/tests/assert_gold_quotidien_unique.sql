-- Renvoie les combinaisons jour x département x carburant présentes plusieurs fois.
-- Le test passe s'il ne renvoie aucune ligne.
select
    snapshot_date,
    code_departement,
    carburant,
    count(*) as nb
from {{ ref('gold_prix_quotidien_dept') }}
group by
    snapshot_date,
    code_departement,
    carburant
having count(*) > 1