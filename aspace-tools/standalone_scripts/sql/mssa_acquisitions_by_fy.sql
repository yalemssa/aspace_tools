SELECT accession.title as accession_title
	, upper(replace(replace(replace(replace(replace(accession.identifier, '[', ''), '"', ''), ',null', ''), ',', '-'), ']', '')) as accession_id
	, CONCAT(extent.number, ' ', ev.value) as extent
	, extent.container_summary
	, replace(replace(replace(replace(replace(resource.identifier, '[', ''), '"', ''), ',null', ''), ',', '-'), ']', '') as resource_id
	, resource.title as resource_title
	, accession.accession_date
	, resource.create_time as resource_create_time
	, resource.finding_aid_date
	, if(resource.create_time like '%2015-06%', 'ADDITION', 'REVIEW') as collection_type
FROM accession
LEFT JOIN extent on extent.accession_id = accession.id
LEFT JOIN date on date.accession_id = accession.id
LEFT JOIN enumeration_value ev on ev.id = extent.extent_type_id
LEFT JOIN spawned_rlshp sr on sr.accession_id = accession.id
LEFT JOIN resource on sr.resource_id = resource.id
WHERE accession.repo_id = 12
AND accession.accession_date BETWEEN '2017-07-01' AND '2018-06-30'