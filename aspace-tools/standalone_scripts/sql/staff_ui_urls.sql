SELECT CONCAT("https://archivesspace.library.yale.edu/resources/", ao.root_record_id, "#tree::archival_object_", ao.id) as url
FROM archival_object ao
WHERE ao.id = 1354023
