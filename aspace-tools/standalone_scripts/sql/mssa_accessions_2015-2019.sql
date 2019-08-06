select CONCAT('/repositories/', accession.repo_id, '/accessions/', accession.id) as uri
	, replace(replace(replace(replace(replace(accession.identifier, ',', '.'), '"', ''), ']', ''), '[', ''), 'null', '') AS call_number
	, accession.display_string
	,  ev2.value as resource_type
	, accession.accession_date
	, extent.number
	, ev.value as extent_type
	, ev3.value as portion
	, extent.container_summary
	, accession.created_by
from accession
left join extent on extent.accession_id = accession.id
left join enumeration_value ev on ev.id = extent.extent_type_id
left join enumeration_value ev2 on ev2.id = accession.resource_type_id
left join enumeration_value ev3 on ev3.id = extent.portion_id
where (accession_date like '%2015%' or accession_date like '%2016%' or accession_date like '%2017%' or accession_date like '%2018%' or accession_date like '%2019%')
and repo_id = 12
order by accession.accession_date desc