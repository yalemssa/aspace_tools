#!/usr/bin/python3
# ~/anaconda3/bin/python

'''
Query strings for getting data out of ArchivesSpace.'''

#############################################
############ User Input Queries #############
#############################################

def get_staff_ui_url(cls, row):
    '''Retrieves a staff interface URL for a given archival object. Custom reports, Bulk queries'''
    archival_object_id = row[0]
    return f"""SELECT CONCAT("https://archivesspace.library.yale.edu/resources/", ao.root_record_id, "#tree::archival_object_", ao.id) as url
    FROM archival_object ao
    WHERE ao.id = {archival_object_id}"""

def all_children(cls, row):
    '''Custom reports, Bulk queries'''
    call_number = row[0]
    return f"""SELECT replace(replace(replace(replace(replace(identifier, ',', ''), '"', ''), ']', ''), '[', ''), 'null', '') AS call_number
        , resource.title as resource_title
        , ao.id as ao_id
        , ao.display_string as child_title
        , ev.value as level
        , CONCAT('/repositories/', resource.repo_id, '/resources/', resource.id) as uri
    FROM archival_object ao
    JOIN resource on ao.root_record_id = resource.id
    LEFT JOIN enumeration_value ev on ev.id = ao.level_id
    WHERE resource.identifier like '%{call_number}%'
    ORDER BY ao.id"""

def all_instances(cls, row):
    '''Custom reports, Bulk queries'''
    call_number = row[0]
    return f"""SELECT replace(replace(replace(replace(replace(identifier, ',', ''), '"', ''), ']', ''), '[', ''), 'null', '') AS call_number
        , resource.title AS resource_title
        , ao.display_string AS ao_title
        , ev2.value AS level
        , tc.barcode AS barcode
        , cp.name AS container_profile
        , tc.indicator AS container_num
        , ev.value AS sc_type
        , sc.indicator_2 AS sc_num
        , CONCAT('/repositories/', tc.repo_id, '/top_containers/', tc.id) as tc_uri
        , CONCAT('/repositories/', resource.repo_id, '/resources/', resource.id) as resource_uri
        , CONCAT('/repositories/', resource.repo_id) as repo_uri
        , CONCAT('/repositories/', ao.repo_id, '/archival_objects/', ao.id) as ao_uri
    from sub_container sc
    LEFT JOIN enumeration_value ev on ev.id = sc.type_2_id
    JOIN top_container_link_rlshp tclr on tclr.sub_container_id = sc.id
    JOIN top_container tc on tclr.top_container_id = tc.id
    LEFT JOIN top_container_profile_rlshp tcpr on tcpr.top_container_id = tc.id
    LEFT JOIN container_profile cp on cp.id = tcpr.container_profile_id
    LEFT JOIN top_container_housed_at_rlshp tchar on tchar.top_container_id = tc.id
    JOIN instance on sc.instance_id = instance.id
    JOIN archival_object ao on instance.archival_object_id = ao.id
    JOIN resource on ao.root_record_id = resource.id
    LEFT JOIN enumeration_value ev2 on ev2.id = ao.level_id
    WHERE resource.identifier like '%{call_number}%'"""

def box_list(cls, row):
    '''Custom reports, Bulk queries'''
    call_number = row[0]
    return f"""SELECT DISTINCT replace(replace(replace(replace(replace(identifier, ',', ''), '"', ''), ']', ''), '[', ''), 'null', '') AS call_number
        , resource.title
        , tc.barcode as barcode
        , tc.indicator as box_number
        , CONCAT('/repositories/', resource.repo_id, ', /resources/', resource.id) as uri
    FROM sub_container sc
    JOIN top_container_link_rlshp tclr on tclr.sub_container_id = sc.id
    JOIN top_container tc on tclr.top_container_id = tc.id
    JOIN instance on sc.instance_id = instance.id
    JOIN archival_object ao on instance.archival_object_id = ao.id
    JOIN resource on ao.root_record_id = resource.id
    #add container profile, other data
    WHERE resource.identifier like '%{call_number}%'
    ORDER BY CAST(tc.indicator as unsigned)"""

def new_accessions(cls, row):
    '''Custom reports, Bulk queries'''
    begin_date = row[0]
    end_date = row[1]
    return f"""SELECT accession.title as accession_title
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

def barcode_data(cls, row):
    '''Custom reports, Bulk queries'''
    barcode = row[0]
    return f"""SELECT tc.barcode AS barcode
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

def music_data(cls, row):
    '''Custom reports, Bulk queries'''
    parent_id = row[0]
    return f"""select CONCAT('/repositories/', ao.repo_id, '/archival_objects/', ao.id) as uri
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

def distinct_creators(cls, row):
    '''Custom reports, Bulk queries'''
    parent_id = row[0]
    return f"""select DISTINCT CONCAT('/repositories/', ao.repo_id, '/archival_objects/', ao.parent_id) as parent_uri
        , CONCAT('/repositories/', ao2.repo_id, '/resources/', ao2.root_record_id) as resource_uri
        , CONCAT('/repositories/', ao2.repo_id) as repo_id
        , CONCAT(np.primary_name, ', ', np.rest_of_name) as name
    from archival_object ao
    join archival_object ao2 on ao2.id = ao.parent_id
    left join linked_agents_rlshp lar on lar.archival_object_id = ao.id
    left join name_person np on lar.agent_person_id = np.agent_person_id
    where ao.parent_id = {parent_id}
    and np.is_display_name is not null"""

def inventory_query(cls, row):
    '''Custom reports, Bulk queries'''
    parent_id = row[0]
    resource_id = row[1]
    return f'''SELECT CONCAT('/repositories/', archival_object.repo_id, '/archival_objects/', archival_object.id) as uri
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

def get_user_repositories(cls, row):
    '''Retrieves a list of users and the repository numbers in which they have permissions. Administrative reports,
    Custom reports, Bulk queries
    '''
    repo_id = row[0]
    return f"""
    SELECT DISTINCT CONCAT('/agents/people/', user.agent_record_id) as agent_uri
        , CONCAT('/users/', user.id) as user_uri
        , np.sort_name as name_person
        , user.name as user
        , user.username as username
        , g.repo_id as group_repo_id
    from user
    left join group_user gu on user.id = gu.user_id
    left join `group` g on gu.group_id = g.id
    left join agent_person ap on ap.id = user.agent_record_id
    left join name_person np on np.agent_person_id = ap.id
    where user.agent_record_id is not null
    and g.repo_id = 1 or g.repo_id = {repo_id}
    order by group_repo_id"""

def mssa_acquisitions_by_fy(cls, row):
    '''Retrieves a list of accessions between a given YYYY-MM-DD date range.
    Custom reports, Bulk queries'''
    begin = row[0]
    end = row[1]
    return f"""SELECT accession.title as accession_title
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
    AND accession.accession_date BETWEEN {begin} AND {end}"""

#################################################
########## Record Retrieval Queries ###########
#################################################

def all_notes(cls):
    '''Retrieves all notes. Record retrieval'''
    return open('scripts/sql/notes/all_notes.sql', encoding='utf-8').read()

def all_agent_notes(cls):
    '''Retrieves all notes associated with agent records. Record retrieval'''
    return open('scripts/sql/notes/all_agent_notes.sql', encoding='utf-8').read()

def all_extents(cls):
    '''Retrieves all records with extent subrecords. Record retrieval'''
    return open('scripts/sql/extents/all_extents.sql', encoding='utf-8').read()

def all_use_restrictions(cls):
    '''Retrieves all use restriction notes. Record retrieval'''
    return open('scripts/sql/notes/all_use_restrictions.sql', encoding='utf-8').read()

def all_access_restrictions(cls):
    '''Retrieves all access restriction notes. Record retrieval'''
    return open('scripts/sql/notes/all_accessrestrict_notes.sql', encoding='utf-8').read()

def all_agent_links(cls):
    '''Retrieves agents and their record links. Record retrieval'''
    return open('scripts/sql/agents/all_agent_links_name_table.sql', encoding='utf-8').read()

def all_agent_links_except_fortunoff(cls):
    '''Retrieves agents and their record links for all repositories except for
    Fortunoff (14). Record retrieval'''
    return open('scripts/sql/agents/agents_linked_no14.sql', encoding='utf-8').read()

def all_subject_links(cls):
    '''Retrieves subjects and their record links. Record retrieval'''
    return open('scripts/sql/subjects/all_subject_links.sql', encoding='utf-8').read()

def all_subject_resource_links(cls):
    '''Retrieves subjects and their resource record links. Record retrieval'''
    return open('scripts/sql/subjects/all_subject_resource_links.sql', encoding='utf-8').read()

def all_subjects_terms(cls):
    '''Retrieves a list of all subject terms associated with subject records
    Record retrieval'''
    return open('scripts/sql/subjects/all_subject_terms.sql', encoding='utf-8').read()

def all_access_notes_with_machine_actionable_restrictions(cls):
    '''Retrieves data about resources and archival objects with access notes
    which include machine-actionable restrictions. Record retrieval'''
    return open('scripts/sql/notes/access_notes_with_mars.sql', encoding='utf-8').read()

def all_locations(cls):
    '''Retrieves all location records. Record retrieval'''
    return open('scripts/sql/containers_locations/all_locations.sql', encoding='utf-8').read()

def controlled_values(cls):
    '''Retrieves a list of commonly-used enumeration values. Record retrieval'''
    return open('scripts/sql/enumerations/get_controlled_values.sql', encoding='utf-8').read()

def all_permissions(cls):
    '''Retrieves a list of all permissions associated with all users. Record retrieval'''
    return open('scripts/sql/admin/all_permissions.sql', encoding='utf-8').read()

def all_digital_objects(cls):
    '''Retrieves all digital object records. Record retrieval'''
    return open('scripts/sql/digital_objects/all_digital_objects.sql', encoding='utf-8').read()

def all_archival_object_dates(cls):
    '''Retrieves all date subrecords associated with archival objects. Record retrieval'''
    return open('scripts/sql/dates/all_archival_object_dates.sql', encoding='utf-8').read()

#################################################
########## YAMS Data Auditing Queries ###########
#################################################

def last_modified(cls):
    '''YAMS Data Auditing'''
    return open('scripts/sql/archival_objects/last_modified.sql', encoding='utf-8').read()

def unstructured_dates(cls):
    '''Data auditing: YAMS. Dates'''
    return open('scripts/sql/dates/unstructured_dates.sql', encoding='utf-8').read()

def check_date_types(cls):
    '''Data auditing: YAMS. Dates'''
    return open('scripts/sql/dates/check_date_types.sql', encoding='utf-8').read()

###########################################
####### MSSA Data Auditing Queries ########
###########################################

def subcontainer_folder_ranges(cls):
    '''Retrieves a list of sub-container records with hyphens indicating folder ranges. Data auditing: MSSA'''
    return open('scripts/sql/containers_locations/subcontainer_folder_ranges.sql', encoding='utf-8').read()

def expiring_restrictions(cls):
    '''Retrieves University Archives restrictions expiring between 2011-2020. Data auditing: MSSA.'''
    return open('scripts/sql/restrictions/expiring_restrictions.sql', encoding='utf-8').read()

def archival_objects_no_dates(cls):
    '''Retrieves a list of archival objects without dates.'''
    return open('scripts/sql/dates/archival_objects_no_dates.sql', encoding='utf-8').read()

def unstructured_dates_with_years(cls):
    '''Retrieves a list of dates with expression values that contain a four-digit
    value, but which do not have a structured begin or end date. Need to add URI
    information so this list will be actionable.'''
    return open('scripts/sql/dates/unstructured_dates_with_years.sql', encoding='utf-8').read()

def unstructured_dates_with_years_count(cls):
    '''Retrieves a count of dates with expression values that contain a four-digit
    value, but which do not have a structured begin or end date.'''
    return open('scripts/sql/counts/unstructured_dates_with_years_count.sql', encoding='utf-8').read()

def dates_without_years(cls):
    '''Retrieves a list of dates without a four-digit value.'''
    return open('scripts/sql/dates/dates_without_years.sql', encoding='utf-8').read()

def dates_without_years_count(cls):
    '''Retrieves a count of date expressions without a four-digit value.'''
    return open('scripts/sql/counts/dates_without_years_count.sql', encoding='utf-8').read()

def unparsed_date_count(cls):
    '''Retrieves a count of date expressions for dates without a begin or end field'''
    return open('scripts/sql/counts/unparsed_date_count.sql', encoding='utf-8').read()

def malformed_subcontainer_count(cls):
    '''Retrieves a count of weird sub containers'''
    return open('scripts/sql/counts/malformed_subcontainer_count.sql', encoding='utf-8').read()

def archival_object_date_count(cls):
    '''Retrieves a count of archival object dates by repository'''
    return open('scripts/sql/counts/archival_object_date_count.sql', encoding='utf-8').read()

def resources_created_by_month_count(cls):
    '''Retrieves a count of MSSA resources created by YYYY-MM'''
    return open('scripts/sql/counts/resources_created_by_month_count.sql', encoding='utf-8').read()

def archival_objects_created_by_month_count(cls):
    '''Retrieves a count of MSSA archival objects created by YYYY-MM'''
    return open('scripts/sql/counts/archival_objects_created_by_month_count.sql', encoding='utf-8').read()

def locations_with_barcodes_and_location_profiles(cls):
    '''Retrieves MSSA locations with barcodes and location profiles. Data auditing: MSSA.'''
    return open('scripts/sql/containers_locations/locations_with_barcodes_and_location_profiles.sql', encoding='utf-8').read()

def containers_in_unbarcoded_locations(cls):
    '''Retrieves unbarcoded locations with associated containers. Data auditing: MSSA.'''
    return open('scripts/sql/containers_locations/containers_in_unbarcoded_locations.sql', encoding='utf-8').read()

def unbarcoded_locations_with_no_containers(cls):
    '''Retrieves unbarcoded locations with no associated containers. PData auditing: MSSA.'''
    return open('scripts/sql/containers_locations/unbarcoded_locations_with_no_containers.sql', encoding='utf-8').read()

def barcoded_locations_with_no_containers(cls):
    '''Retrieves barcoded locations with no associated containers. Data auditing: MSSA.'''
    return open('scripts/sql/containers_locations/barcoded_locations_with_no_containers.sql', encoding='utf-8').read()

def containers_at_offsite_storage(cls):
    '''Retrieves MSSA containers at LSF. Data auditing: MSSA.'''
    return open('scripts/sql/containers_locations/containers_at_offsite_storage.sql', encoding='utf-8').read()

def containers_not_at_offsite_storage(cls):
    '''Retrieves MSSA containers not at LSF. Data auditing: MSSA.'''
    return open('scripts/sql/containers_locations/containers_not_at_offsite_storage.sql', encoding='utf-8').read()

def containers_with_no_location(cls):
    '''Retrieves top containers with no locations. Data auditing: MSSA'''
    return open('scripts/sql/containers_locations/containers_with_no_location.sql', encoding='utf-8').read()

# def unassociated_enum_helper(subrec_table, subrec_column, enumeration_id):
#     '''Helper function, internal only'''
#     return f"""select ev.id
#         , ev.value
#     from enumeration_value ev
#     LEFT JOIN {subrec_table} on {subrec_table}.{subrec_column} = ev.id
#     where {subrec_table}.id is null
#     and ev.enumeration_id = {enumeration_id}
#     UNION
#     select ev.id
#         , ev.value
#     from enumeration_value ev
#     RIGHT JOIN {subrec_table} on {subrec_table}.{subrec_column} = ev.id
#     where {subrec_table}.id is null
#     and ev.enumeration_id = {enumeration_id}"""

def unused_extent_types(cls):
    '''Data auditing: YAMS'''
    return open('scripts/sql/enumerations/unused_extent_types.sql', encoding='utf-8').read()

def unused_top_container_types(cls):
    '''Data auditing: YAMS'''
    return open('scripts/sql/enumerations/unused_top_container_types.sql', encoding='utf-8').read()

def unused_child_container_types(cls):
    '''Data auditing: YAMS'''
    return open('scripts/sql/enumerations/unused_child_container_types.sql', encoding='utf-8').read()

def unused_grandchild_container_types(cls):
    '''Data auditing: YAMS'''
    return open('scripts/sql/enumerations/unused_grandchild_container_types.sql', encoding='utf-8').read()

def unused_subject_sources(cls):
    '''Data auditing: YAMS'''
    return open('scripts/sql/enumerations/unused_subject_sources.sql', encoding='utf-8').read()


##############################
####### COUNT QUERIES ########
##############################

# TO-DO - add ability to filter by repository using an input value in the dash app
# def count_helper(table_name, table_alias, column_name, repo=None):
#     '''Need to keep this out of the drop-down list - maybe import from another file???'''
#     return f"""
#     SELECT ev.value as {table_alias}
#         , COUNT(*) as count
#     FROM {table_name}
#     LEFT JOIN enumeration_value ev on ev.id = {table_name}.{column_name}
#     GROUP BY ev.value
#     ORDER BY count DESC
#     """

def archival_object_publication_status_count(cls):
    return open('scripts/sql/counts/archival_object_publication_status_count.sql', encoding='utf-8').read()

def century_begin_count(cls):
    '''Retrieves a count of all years rounded to the closest century'''
    return open('scripts/sql/counts/century_begin_count.sql', encoding='utf-8').read()

def decade_count(cls):
    '''Retrieves a count of all years rounded to the closest decade'''
    return open('scripts/sql/counts/decade_count.sql', encoding='utf-8').read()

def archival_object_count_by_repo(cls):
    return open('scripts/sql/counts/archival_object_count_by_repo.sql', encoding='utf-8').read()

def child_count(cls):
    '''Retrieves a count of archival objects associated with each resource record.'''
    return open('scripts/sql/counts/resource_child_count.sql', encoding='utf-8').read()

def extent_type_count(cls):
    '''Retrieves a count of extent types used in descriptive records.'''
    return open('scripts/sql/counts/extent_type_count.sql', encoding='utf-8').read()

def container_type_count(cls):
    '''Retrieves a count of container types used in top container records.'''
    return open('scripts/sql/counts/container_type_count.sql', encoding='utf-8').read()

def child_container_type_count(cls):
    '''Retrieves a count of container types used in top container records.'''
    return open('scripts/sql/counts/child_container_type_count.sql', encoding='utf-8').read()

def grandchild_container_type_count(cls):
    '''Retrieves a count of container types used in top container records.'''
    return open('scripts/sql/counts/grandchild_container_type_count.sql', encoding='utf-8').read()

def container_profile_count(cls):
    '''Retrieves a count of container profiles linked to top container records.'''
    return open('scripts/sql/counts/container_profile_count.sql', encoding='utf-8').read()

def instance_type_count(cls):
    '''Retrieves a count of instance types linked to descriptive records.'''
    return open('scripts/sql/counts/instance_type_count.sql', encoding='utf-8').read()

def archival_record_level_count(cls):
    '''Retrieves a count of archival object levels.'''
    return open('scripts/sql/counts/archival_record_level_count.sql', encoding='utf-8').read()

def subject_source_count(cls):
    '''Retrieves a count of subject sources.'''
    return open('scripts/sql/counts/subject_source_count.sql', encoding='utf-8').read()

def acquisition_type_count(cls):
    '''Retrieves a count of acquisition types used in accession records.'''
    return open('scripts/sql/counts/acquisition_type_count.sql', encoding='utf-8').read()

def accession_resource_type_count(cls):
    '''Retrieves a count of resource type values - i.e. 'records', 'papers' - assigned in accession records'''
    return open('scripts/sql/counts/accession_resource_type_count.sql', encoding='utf-8').read()

def date_calendar_count(cls):
    '''Retrieves a count of calendar types used in date records.'''
    return open('scripts/sql/counts/date_calendar_count.sql', encoding='utf-8').read()

def date_certainty_count(cls):
    '''Retrieves a count of certainty values used in date records.'''
    return open('scripts/sql/counts/date_certainty_count.sql', encoding='utf-8').read()

def date_era_count(cls):
    '''Retrieves a count of era values used in date records.'''
    return open('scripts/sql/counts/date_era_count.sql', encoding='utf-8').read()

def date_label_count(cls):
    '''Retrieves a count of label values used in date records.'''
    return open('scripts/sql/counts/date_label_count.sql', encoding='utf-8').read()

def date_type_count(cls):
    '''Retrieves a count of type values used in date records.'''
    return open('scripts/sql/counts/date_type_count.sql', encoding='utf-8').read()

def digital_object_level_count(cls):
    '''Retrieves a count of digital object levels.'''
    return open('scripts/sql/counts/digital_object_level_count.sql', encoding='utf-8').read()

def digital_object_type_count(cls):
    '''Retrieves a count of digital object types.'''
    return open('scripts/sql/counts/digital_object_type_count.sql', encoding='utf-8').read()

def event_type_count(cls):
    '''Retrieves a count of event types.'''
    return open('scripts/sql/counts/event_type_count.sql', encoding='utf-8').read()

def event_outcome_count(cls):
    '''Retrieves a count of event outcomes.'''
    return open('scripts/sql/counts/event_outcome_count.sql', encoding='utf-8').read()

def extent_portion_count(cls):
    '''Retrieves a count of portion values used in extent records.'''
    return open('scripts/sql/counts/extent_portion_count.sql', encoding='utf-8').read()

def file_version_checksum_method_count(cls):
    '''Retrieves a count of checksum method values used in file version records.'''
    return open('scripts/sql/counts/file_version_checksum_method_count.sql', encoding='utf-8').read()

def file_version_use_statement_count(cls):
    '''Retrieves a count of use statement values used in file version records.'''
    return open('scripts/sql/counts/file_version_use_statement_count.sql', encoding='utf-8').read()

def processing_priority_count(cls):
    '''Retrieves a count of processing priority values used in collection management records.'''
    return open('scripts/sql/counts/processing_priority_count.sql', encoding='utf-8').read()

def processing_status_count(cls):
    '''Retrieves a count of processing status values used in collection management records.'''
    return open('scripts/sql/counts/processing_status_count.sql', encoding='utf-8').read()

def machine_actionable_restriction_count(cls):
    '''Retrieves a count of machine actionable restriction types linked to accessrestrict or userestrict notes.'''
    return open('scripts/sql/counts/machine_actionable_restriction_count.sql', encoding='utf-8').read()

def resource_type_count(cls):
    '''Retrieves a count of resource types.'''
    return open('scripts/sql/counts/resource_type_count.sql', encoding='utf-8').read()

def finding_aid_description_rules_count(cls):
    '''Retrieves a count of finding aid description rule values used in resource records.'''
    return open('scripts/sql/counts/finding_aid_description_rules_count.sql', encoding='utf-8').read()

def finding_aid_status_count(cls):
    '''Retrieves a count of finding aid status values used in resource records.'''
    return open('scripts/sql/counts/finding_aid_status_count.sql', encoding='utf-8').read()

def container_profile_dimension_unit_count(cls):
    '''Retrieves a count of dimension units used in container profile records.'''
    return open('scripts/sql/counts/container_profile_dimension_unit_count.sql', encoding='utf-8').read()

def location_profile_dimension_unit_count(cls):
    '''Retrieves a count of dimension units used in location profile records.'''
    return open('scripts/sql/counts/location_profile_dimension_unit_count.sql', encoding='utf-8').read()

def temporary_location_count(cls):
    '''Retrieves a count of temporary locations.'''
    return open('scripts/sql/counts/temporary_location_count.sql', encoding='utf-8').read()

def name_person_order_count(cls):
    '''Retrieves a count of name order values used in name person records.'''
    return open('scripts/sql/counts/name_person_order_count.sql', encoding='utf-8').read()

def linked_agent_role_count(cls):
    '''Retrieves a count of linked agent roles.'''
    return open('scripts/sql/counts/linked_agent_role_count.sql', encoding='utf-8').read()

def term_type_count(cls):
    '''Retrieves a count of term types used in subject term records.'''
    return open('scripts/sql/counts/term_type_count.sql', encoding='utf-8').read()

def name_source_count(cls):
    '''Retrieves a combined count of sources used in name person, name family, and
    name corporate entity records.'''
    return open('scripts/sql/counts/name_source_count.sql', encoding='utf-8').read()

def name_rule_count(cls):
    '''Retrieves a combined count of rules used in name person, name family, and name corporate entity records.'''
    return open('scripts/sql/counts/name_rules_count.sql', encoding='utf-8').read()

### NEW STUFF ###

def ref_id_refs(cls):
    '''Retrieves a list of archival objects with Ref IDs which start with "ref", indicating they were not auto-generated and may not be unique'''
    return open('scripts/sql/archival_objects/ref_id_refs.sql', encoding='utf-8').read()

def all_structured_dates(cls):
    '''Retrieves a combined list of all structured begin and end dates in Archivesspace'''
    return open('scripts/sql/dates/structured_date_union.sql', encoding='utf-8').read()

def published_rus_with_unpublished_children(cls):
    '''Retrieves a list of published MSSA RU resource records with at least one unpublished child'''
    return open('scripts/sql/mssa_auditing/published_rus_w_unpublished_aos.sql', encoding='utf-8').read()

def archival_object_leading_and_trailing_spaces(cls):
    '''Retrieves a report of all archival objects with leading or trailing spaces in their titles'''
    return open('scripts/sql/archival_objects/get_leading_trailing_spaces.sql', encoding='utf-8').read()

def enumeration_positions(cls):
    '''Retrieves a report of the position of each enumeration value'''
    return open('scripts/sql/enumerations/get_enum_positions.sql', encoding='utf-8').read()

def suppressed_resources(cls):
    '''Retrieves a report of all suppressed resource records'''
    return open('scripts/sql/resources/suppressed_resources.sql', encoding='utf-8').read()

def split_identifiers(cls):
    '''Retrieves a report of unsuppressed resource identifiers with values in the id_1,
    id_2, and id_3 fields.'''
    return open('scripts/sql/resources/split_identifiers.sql', encoding='utf-8').read()

def containers_missing_types(cls):
    '''Retrieves a report of containers without a value in the type field.'''
    return open('scripts/sql/containers_locations/containers_missing_type.sql', encoding='utf-8').read()

def qualified_researcher_notes(cls):
    '''Retrieves a report of archival object or resource access notes which
    include the word "qualified"'''
    return open('scripts/sql/notes/qualified_researcher_notes.sql', encoding='utf-8').read()

def malformed_cuids(cls):
    '''Retrieves a report of non-standard usage of component unique identifiers
    in MSSA archival object records.'''
    return open('scripts/sql/archival_objects/malformed_mssa_cuids.sql', encoding='utf-8').read()

def subcontainers_with_grandchildren(cls):
    '''Retrieves a report of all archival object instances with values in the
    grandchild indicator field.'''
    return open('scripts/sql/containers_locations/subcontainers_with_grandchildren.sql', encoding='utf-8').read()

def preservica_notes(cls):
    '''Retrieves notes with Preservica URLs'''
    return open('scripts/sql/notes/preservica_notes.sql', encoding='utf-8').read()

def preservica_instances(cls):
    '''Retrieves archival object records with Preservica digital object instances'''
    return open('scripts/sql/containers_locations/preservica_digital_object_instances.sql', encoding='utf-8').read()

def preservica_digital_objects(cls):
    '''Retrieves digital object records with "Preservica" in the title field'''
    return open('scripts/sql/digital_objects/preservica_digital_objects.sql', encoding='utf-8').read()

def lowercase_subjects(cls):
    '''Retrieves a list of subject records that start with a lowercase letter'''
    return open('scripts/sql/subjects/lowercase_subjects.sql', encoding='utf-8').read()

def database_data(cls):
    '''Retrieves a list of tables and fields in the ArchivesSpace database'''
    return open('scripts/sql/admin/db_info.sql', encoding='utf-8').read()

def unassociated_agents(cls):
    '''Retrieves a list of agents which are not associated with a descriptive
    record'''
    return open('scripts/sql/agents/unassociated_agents.sql', encoding='utf-8').read()

def unassociated_subjects(cls):
    '''Retrieves a list of subjects which are not associated with a descriptive
    record'''
    return open('scripts/sql/subjects/unassociated_subjects.sql', encoding='utf-8').read()

def personal_names_with_dates_in_primary_name(cls):
    '''Retrieves a list of people agents which have dates in the primary name field'''
    return open('scripts/sql/agents/personal_names_with_dates_in_primary_name.sql', encoding='utf-8').read()

def corporate_entities_with_trailing_periods(cls):
    '''Retrieves a list of corporate entity agents which have trailing periods'''
    return open('scripts/sql/agents/corporate_entities_with_trailing_periods.sql', encoding='utf-8').read()

def personal_names_with_trailing_periods(cls):
    '''Retrieves a list of people agents with trailing periods'''
    return open('scripts/sql/agents/personal_names_with_trailing_periods.sql', encoding='utf-8').read()

def arabic_notes(cls):
    '''Retrieves a list of Arabic scope and content notes'''
    return open('scripts/sql/notes/arabic_notes.sql', encoding='utf-8').read()
