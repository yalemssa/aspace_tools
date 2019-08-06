SELECT 
rr.id
from rights_restriction rr
LEFT JOIN rights_restriction_type rrt on rrt.rights_restriction_id = rr.id
GROUP BY rr.id
HAVING(COUNT(rr.id) > 1)

