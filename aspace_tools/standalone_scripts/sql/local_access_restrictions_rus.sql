select CONCAT('/repositories/', resource.repo_id, '/resources/', resource.id) as resource_uri
	, npi.persistent_id
	, ev.value as rights_restriction
	, replace(replace(replace(replace(replace(identifier, ',', ''), '"', ''), ']', ''), '[', ''), 'null', '') AS call_number
	, resource.title
FROM resource
JOIN note on note.resource_id = resource.id
LEFT JOIN note_persistent_id npi on npi.note_id = note.id
JOIN rights_restriction rr on rr.resource_id = resource.id
JOIN rights_restriction_type rrt on rrt.rights_restriction_id = rr.id
LEFT JOIN enumeration_value ev on ev.id = rrt.restriction_type_id
WHERE resource.identifier like '%RU %'
AND note.notes like '%accessrestrict%'