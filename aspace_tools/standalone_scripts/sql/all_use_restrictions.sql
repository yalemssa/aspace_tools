SELECT repository.name 
	, CAST(note.notes as CHAR (15000) CHARACTER SET UTF8) AS text
	, ao.display_string as ao_title
    , resource.title as resource_title
    , CONCAT('/repositories/', ao.repo_id, '/archival_objects/', ao.id) as URI
    , rr.restriction_note_type
    , rr.begin
    , rr.end
    , ev.value as restriction_type
FROM note_persistent_id npi
JOIN note on note.id = npi.note_id
JOIN archival_object ao on ao.id = note.archival_object_id
JOIN resource on ao.root_record_id = resource.id
JOIN repository on ao.repo_id = repository.id
LEFT JOIN rights_restriction rr on rr.archival_object_id = ao.id
LEFT JOIN rights_restriction_type rrt on rrt.rights_restriction_id = rr.id
LEFT JOIN enumeration_value ev on ev.id = rrt.restriction_type_id
WHERE note.notes LIKE '%"type":"userestrict"%'
UNION ALL
SELECT repository.name 
	, CAST(note.notes as CHAR (15000) CHARACTER SET UTF8) AS text
	, NULL as ao_title
    , resource.title as title
    , CONCAT('/repositories/', resource.repo_id, '/resources/', resource.id) as URI
    , rr.restriction_note_type
    , rr.begin
    , rr.end
    , ev.value as restriction_type
FROM note_persistent_id npi
JOIN note on note.id = npi.note_id
JOIN resource on resource.id = note.resource_id
JOIN repository on resource.repo_id = repository.id
LEFT JOIN rights_restriction rr on rr.resource_id = resource.id
LEFT JOIN rights_restriction_type rrt on rrt.rights_restriction_id = rr.id
LEFT JOIN enumeration_value ev on ev.id = rrt.restriction_type_id
WHERE note.notes LIKE '%"type":"userestrict"%'