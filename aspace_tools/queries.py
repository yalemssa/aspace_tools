#!/usr/bin/python3
#~/anaconda3/bin/python

'''
Query strings for getting data out of ArchivesSpace. These are imported by process_data.py and run by the DB query functions.

Note:
	To run a single query string from the queries.py file, just use the DBConn class in utilities.dbssh.
'''

from . import aspace_tools_logging as atl

logger = atl.logging.getLogger(__name__)

def get_expiring_restrictions():
	query_string = f"""SELECT ev.value as rights_restriction_type
		 , rr.begin
		 , rr.end
		 , replace(replace(replace(replace(replace(r2.identifier, ',', ''), '"', ''), ']', ''), '[', ''), 'null', '') AS call_number
		 , replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(ao.display_string, '<', ''), '>', ''), '/', ''), '=', ''), '"', ''), 'emph', ''), 'render', ''), 'title', ''), ' xlink:typesimple italic', ''), 'italic', ''), 'underline', ''), 'smcaps', '') as child_title
		 , r2.title as parent_title
		 , CONCAT('/repositories/', ao.repo_id, '/archival_objects/', ao.id) as uri
		 , ao.repo_id
	FROM rights_restriction rr
	JOIN rights_restriction_type rrt on rr.id = rrt.rights_restriction_id
	JOIN archival_object ao on ao.id = rr.archival_object_id
	JOIN resource r2 on r2.id = ao.root_record_id
	LEFT JOIN enumeration_value ev on ev.id = rrt.restriction_type_id
	JOIN note on note.archival_object_id = ao.id
	WHERE rr.end is not null
	and r2.identifier like '%RU%'
	and rr.end in ('2010-01-01', '2011-01-01', '2012-01-01', '2013-01-01', '2014-01-01', '2015-01-01',
							'2016-01-01', '2017-01-01', '2018-01-01', '2019-01-01', '2020-01-01')
	UNION ALL
	SELECT ev.value as rights_restriction_type
		 , rr.begin
		 , rr.end
		, replace(replace(replace(replace(replace(r.identifier, ',', ''), '"', ''), ']', ''), '[', ''), 'null', '') AS call_number
		, NULL as child_title
		, r.title as parent_title
		, CONCAT('/repositories/', r.repo_id, '/resources/', r.id) as uri
		, r.repo_id
	FROM rights_restriction rr
	JOIN rights_restriction_type rrt on rr.id = rrt.rights_restriction_id
	JOIN resource r on r.id = rr.resource_id
	LEFT JOIN enumeration_value ev on ev.id = rrt.restriction_type_id
	WHERE rr.end is not null
	and r.identifier like '%RU%'
	and rr.end in ('2010-01-01', '2011-01-01', '2012-01-01', '2013-01-01', '2014-01-01', '2015-01-01',
							'2016-01-01', '2017-01-01', '2018-01-01', '2019-01-01', '2020-01-01')"""
	return query_string

def get_new_accessions(row):
	begin_date = row[0]
	end_date = row[1]
	query_string = f"""SELECT accession.title as accession_title
		, upper(replace(replace(replace(replace(replace(accession.identifier, '[', ''), '"', ''), ',null', ''), ',', '-'), ']', '')) as accession_id
		, CONCAT(extent.number, ' ', ev.value) as extent
		, extent.container_summary
		, replace(replace(replace(replace(replace(resource.identifier, '[', ''), '"', ''), ',null', ''), ',', '-'), ']', '') as resource_id
		, resource.title as resource_title
		, accession.accession_date
		, resource.create_time as resource_create_time
		, resource.finding_aid_date
		, if(resource.create_time like '%2015%', 'ADDITION', 'REVIEW') as collection_type
	FROM accession
	LEFT JOIN extent on extent.accession_id = accession.id
	LEFT JOIN date on date.accession_id = accession.id
	LEFT JOIN enumeration_value ev on ev.id = extent.extent_type_id
	LEFT JOIN spawned_rlshp sr on sr.accession_id = accession.id
	LEFT JOIN resource on sr.resource_id = resource.id
	WHERE accession.repo_id = 12
	AND accession.accession_date BETWEEN '{begin_date}' AND '{end_date}'"""
	return query_string

def get_barcode_data(row):
	barcode = row[0]
	query_string = f"""SELECT tc.barcode AS barcode
		, replace(replace(replace(replace(replace(identifier, ',', ''), '"', ''), ']', ''), '[', ''), 'null', '') AS call_number
		, resource.title AS resource_title
	    , ao.display_string AS ao_title
		, cp.name AS container_profile
		, tc.indicator AS container_num
	    , ev.value AS sc_type
	    , sc.indicator_2 AS sc_num
	from sub_container sc
	LEFT JOIN enumeration_value ev on ev.id = sc.type_2_id
	LEFT JOIN top_container_link_rlshp tclr on tclr.sub_container_id = sc.id
	LEFT JOIN top_container tc on tclr.top_container_id = tc.id
	LEFT JOIN top_container_profile_rlshp tcpr on tcpr.top_container_id = tc.id
	LEFT JOIN container_profile cp on cp.id = tcpr.container_profile_id
	LEFT JOIN top_container_housed_at_rlshp tchar on tchar.top_container_id = tc.id
	LEFT JOIN instance on sc.instance_id = instance.id
	LEFT JOIN archival_object ao on instance.archival_object_id = ao.id
	LEFT JOIN resource on ao.root_record_id = resource.id
	WHERE tc.barcode like '{barcode}'"""
	return query_string

def get_music_data(row):
	parent_id = row[0]
	query_string = f"""select CONCAT('/repositories/', ao.repo_id, '/archival_objects/', ao.id) as uri
		, CONCAT('/repositories/', ao.repo_id, '/archival_objects/', ao.parent_id) as parent_uri
		, ao2.display_string as parent_display_string
		, ao.display_string as display_string
		, CONCAT('/agents/people/', np.agent_person_id) as agent_uri
		, CONCAT(np.primary_name, ', ', np.rest_of_name) as name
		, np.sort_name as sort_name
	from archival_object ao
	join archival_object ao2 on ao2.id = ao.parent_id
	left join linked_agents_rlshp lar on lar.archival_object_id = ao.id
	left join name_person np on lar.agent_person_id = np.agent_person_id
	where ao.parent_id = {parent_id}
	and np.is_display_name is not null"""
	return query_string

def get_distinct_creators(row):
	parent_id = row[0]
	query_string = f"""select DISTINCT CONCAT('/repositories/', ao.repo_id, '/archival_objects/', ao.parent_id) as parent_uri
		, CONCAT('/repositories/', ao2.repo_id, '/resources/', ao2.root_record_id) as resource_uri
		, CONCAT('/repositories/', ao2.repo_id) as repo_id
		, CONCAT(np.primary_name, ', ', np.rest_of_name) as name
	from archival_object ao
	join archival_object ao2 on ao2.id = ao.parent_id
	left join linked_agents_rlshp lar on lar.archival_object_id = ao.id
	left join name_person np on lar.agent_person_id = np.agent_person_id
	where ao.parent_id = {parent_id}
	and np.is_display_name is not null"""
	return query_string

def inventory_query(row):
	parent_id = row[0]
	resource_id = row[1]
	query_string = f'''SELECT CONCAT('/repositories/', archival_object.repo_id, '/archival_objects/', archival_object.id) as uri
		, CONCAT('/repositories/', archival_object.repo_id, '/archival_objects/', archival_object.parent_id) as parent_uri
		, CONCAT('/repositories/', archival_object.repo_id, '/resources/', archival_object.root_record_id) as resource_uri
		, archival_object.position
		, enumeration_value.value as ao_level
	FROM archival_object
	LEFT JOIN enumeration_value on enumeration_value.id = archival_object.level_id
	WHERE archival_object.parent_id = {parent_id}
	UNION ALL
	SELECT CONCAT('/repositories/', archival_object.repo_id, '/archival_objects/', archival_object.id) as uri
		, archival_object.parent_id as parent_uri
		, CONCAT('/repositories/', archival_object.repo_id, '/resources/', archival_object.root_record_id) as resource_uri
		, archival_object.position
		, enumeration_value.value as ao_level
	FROM archival_object
	LEFT JOIN enumeration_value on enumeration_value.id = archival_object.level_id
	WHERE archival_object.parent_id is null
	AND archival_object.root_record_id = {resource_id}
	AND archival_object.display_string not like "Inventory"'''
	return query_string

get_updated_locations = """
SELECT location.barcode
	, location.title as location_title
	, CONCAT('/repositories/', repository.id) as repo_uri
	, CONCAT('/locations/', location.id) as location_uri
	, CONCAT('/location_profiles/', lp.id) as location_profile_uri
	, lp.name as location_profile_name
from location
left join location_profile_rlshp lpr on lpr.location_id = location.id
left join location_profile lp on lpr.location_profile_id = lp.id
left join owner_repo_rlshp orr on orr.location_id = location.id
left join repository on orr.repository_id = repository.id
WHERE location.barcode is not null
AND lp.id is not null
"""

get_location_data = """
#Report of MSSA materials with NO location
#Report of MSSA materials in all non-LSF locations
#Report of MSSA locations with NO material

SELECT CONCAT('/locations/', location.id) as location_uri
	, location.barcode
	, location.title
	, CONCAT('/repositories/', tc.repo_id, '/top_containers/', tc.id) as tc_uri
	, tc.indicator
	, tc.barcode
FROM location
LEFT JOIN top_container_housed_at_rlshp tchar on location.id = tchar.location_id
LEFT JOIN top_container tc on tc.id = tchar.top_container_id
WHERE (tc.repo_id = 12)
#WHERE (tc.repo_id is null)
AND location.id != 9
AND (location.title not like '%CWMHL%' and location.title not like '%Music Library%'
		and location.title not like '%Beinecke%' and location.title not like '%Iron Mountain%')
AND location.barcode is not null
"""

get_materials_w_no_location = """
select CONCAT('/repositories/', tc.repo_id, '/top_containers/', tc.id) as uri
	, tc.barcode
	, tc.indicator
	, resource.title
	, location.id
from top_container tc
LEFT JOIN top_container_housed_at_rlshp tchar on tchar.top_container_id = tc.id
LEFT JOIN location on tchar.location_id = location.id
LEFT JOIN top_container_link_rlshp tclr on tclr.top_container_id = tc.id
LEFT JOIN sub_container sc on tclr.sub_container_id = sc.id
LEFT JOIN instance on sc.instance_id = instance.id
LEFT JOIN archival_object ao on instance.archival_object_id = ao.id
LEFT JOIN resource on resource.id = ao.root_record_id
where location.id is null
and tc.repo_id = 12
UNION
select CONCAT('/repositories/', tc.repo_id, '/top_containers/', tc.id) as uri
	, tc.barcode
	, tc.indicator
	, resource.title
	, location.id
from top_container tc
RIGHT JOIN top_container_housed_at_rlshp tchar on tchar.top_container_id = tc.id
RIGHT JOIN location on tchar.location_id = location.id
RIGHT JOIN top_container_link_rlshp tclr on tclr.top_container_id = tc.id
RIGHT JOIN sub_container sc on tclr.sub_container_id = sc.id
RIGHT JOIN instance on sc.instance_id = instance.id
RIGHT JOIN archival_object ao on instance.archival_object_id = ao.id
RIGHT JOIN resource on resource.id = ao.root_record_id
where location.id is null
and tc.repo_id = 12
"""
