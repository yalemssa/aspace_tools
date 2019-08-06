select resource.repo_id 
	, CAST(note.notes as CHAR (500000) CHARACTER SET UTF8) AS Text
	, CONCAT('/repositories/', resource.repo_id, '/resources/', resource.id) AS URI
    , npi.persistent_id as persistent_id
from resource
JOIN note on note.resource_id = resource.id
JOIN note_persistent_id npi on npi.note_id = note.id
WHERE note.notes LIKE '%"type":"accessrestrict"%'
#WHERE resource.repo_id = 5
UNION ALL
select 
	, CAST(note.notes as CHAR (500000) CHARACTER SET UTF8) AS Text
	, CONCAT('/repositories/', ao.repo_id, '/archival_objects/', ao.id) AS URI
    , npi.persistent_id as persistent_id
from archival_object ao
JOIN note on note.archival_object_id = ao.id
JOIN note_persistent_id npi on npi.note_id = note.id
WHERE note.notes LIKE '%"type":"accessrestrict"%'
#WHERE ao.repo_id = 5
UNION ALL
select CAST(note.notes as CHAR (500000) CHARACTER SET UTF8) AS Text
	, CONCAT('/repositories/', do.repo_id, 'digital_objects/', do.id) AS URI
    , npi.persistent_id as persistent_id
from digital_object do 
JOIN note on note.digital_object_id = do.id
JOIN note_persistent_id npi on npi.note_id = note.id
WHERE note.notes LIKE '%"type":"accessrestrict"%'
#WHERE do.repo_id = 5
UNION ALL
select CAST(note.notes as CHAR (500000) CHARACTER SET UTF8) AS Text
	, CONCAT('/repositories/', doc.repo_id, '/digital_object_components/', doc.id) AS URI
    , npi.persistent_id as persistent_id
from digital_object_component doc
JOIN note on note.digital_object_component_id = doc.id
JOIN note_persistent_id npi on npi.note_id = note.id
WHERE note.notes LIKE '%"type":"accessrestrict"%'
#WHERE doc.repo_id = 5