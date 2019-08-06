#this gets a report of HM films and their external ids

SELECT CONCAT('/repositories/', ao.root_record_id, '/archival_objects/', ao.id) as uri
	, npi.persistent_id
	, note.notes as note_json
	, e.external_id as external_id
	, e.source as external_id_source
	, tc.indicator
FROM archival_object ao
LEFT JOIN note on note.archival_object_id = ao.id
LEFT JOIN note_persistent_id npi on npi.note_id = note.id
LEFT JOIN external_id e on e.archival_object_id = ao.id
LEFT JOIN instance on instance.archival_object_id = ao.id
LEFT JOIN sub_container sc on sc.instance_id = instance.id
LEFT JOIN top_container_link_rlshp tclr on tclr.sub_container_id = sc.id
LEFT JOIN top_container tc on tc.id tclr.top_container_id
WHERE note.notes like '%accessrestrict%'
AND tc.indicator like '%U%'