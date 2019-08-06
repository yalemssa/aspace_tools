#/usr/bin/python3
#~/anaconda3/bin/python

#this is useless right now
#from utilities.decorators import register, PLUGINS

import aspace_tools_logging as atl
logger = atl.logging.getLogger(__name__)

'''
JSON data structures for ArchivesSpace record creation, update, etc. Called by CRUD functions in
crud.py

TO-DO:
register functions and their variables with a decorator; latter doesn't seem very easy; seems like the only
way that the arguments get registered is when the function actually gets called???

TODO: change parameter names - have all URIs which are used to call the API just called 'uri'; like, all the
ones in row[0]

Add another argument for update_subrecord_component, etc. to define the subrecord and the component.

Continue adding stuff from remaining .py files

also need to work on the templates

would like to be able to set options - i.e. if something is empty don't add it. Or look for indexing error
'''

'''
-----------------------
CREATE RECORD FUNCTIONS
-----------------------
'''

@atl.as_tools_logger(logger)
def create_repositories(row):
    '''Creates a repository record.

       Parameters: repo_name
    '''
    new_repo = {'jsonmodel_type': 'repository', 'repo_name': row['repo_name']}
    return (new_repo, '/repositories')

@atl.as_tools_logger(logger)
def create_archival_objects(row):
    '''Creates an archival object record.

       Required Parameters: title, resource_uri, repo_uri

       Optional Parameters: date_begin, date_end, date_type, date_label, extent_type
                            extent_portion, extent_number, parent_uri

       NOTE: This function takes a DictReader row as input.'''
    #don't have any instances here right now. Add later. Make optional? Or add the container lookup somehow??
    new_ao = {'jsonmodel_type': 'archival_object', 'title': row['title'], 'level': 'file', 'publish': True,
                'dates': [{'jsonmodel_type': 'date', 'begin': row['date_begin'], 'end': row['date_end'],
                            'date_type': row['date_type'], 'label': row['date_label']}],
                'extents': [{'jsonmodel_type': 'extent', 'portion': row['extent_portion'], 'number': row['extent_number'],
                            'extent_type': row['extent_type']}],
                'parent': {'ref': row['parent_uri']},
                'resource': {'ref': row['resource_uri']},
                'repository': {'ref': row['repo_uri']}}
    #if just an empty string delete the key, otherwise the job will fail. Better way to do this?
    if row['extent_type'] == '':
        del new_ao['extents']
    if row['date_type'] == '':
        del new_ao['dates']
    if row['parent_uri'] == '':
        del new_ao['parent']
    endpoint = row['repo_uri'] + '/archival_objects'
    return (new_ao, endpoint)

@atl.as_tools_logger(logger)
def create_accessions(row):
    '''Creates an accession record.

       Parameters: repo_uri, identifier, title, accession_date
    '''
    new_accession = {'id_0': row['identifier'], 'title': row['title'], 'accession_date': row['accession_date'], 'repository': {'ref': row['repo_uri']},
                     'jsonmodel_type': 'accession'}
    endpoint = row['repo_uri'] + '/accessions'
    return (new_accession, endpoint)

@atl.as_tools_logger(logger)
def create_resources(row):
    '''Creates a resource record.

       Parameters: repo_uri, identifier, title, language, level, begin_date,
                   end_date, date_type, date_label, extent_type, extent_portion,
                   extent_number, container_summary

       TO-DO: make some of these optional, add options for notes, etc.
    '''
    new_resource = {'id_0': row['identifier'], 'title': row['title'], 'language': row['language'], 'level': row['level'],
                    'dates' : [{'begin': row['begin_date'], 'end': row['end_date'], 'date_type': row['date_type'], 'label': row['date_label'],
                                'jsonmodel_type': 'date'}],
                    'extents': [{'extent_type': row['extent_type'], 'portion': row['extent_portion'], 'number': row['extent_number'],
                                 'container_summary': row['container_summary'], 'jsonmodel_type': 'extent'}],
                    'repository': {'ref': row['repo_uri']}, 'jsonmodel_type': 'resource'}
    endpoint = row['repo_uri'] + '/resources'
    return (new_resource, endpoint)

@atl.as_tools_logger(logger)
def create_classification(row):
    '''Creates a classification record.

       Parameters: repo_uri, identifier, title, description
    '''
    new_classification = {'jsonmodel_type': 'classification', 'identifier': row['identifier'],
                          'title': row['title'], 'description': row['description'], 'repository': {'ref': row['repo_uri']}}
    endpoint = row['repo_uri'] + '/classifications'
    return (new_classification, endpoint)

@atl.as_tools_logger(logger)
def create_classification_term(row):
    '''Creates a classification term with or without a classification term parent.

       Parameters: parent_classification_uri, parent_classification_term_uri, repo_uri,
       title, description
    '''
    new_classification_term = {'jsonmodel_type': 'classification_term', 'identifier': row['identifier'],
                               'title': row['title'], 'description': row['description'], 'classification': {'ref': row['parent_classification_uri']},
                               'repository': {'ref': row['repo_uri']}}
    if row['parent_classification_term_uri'] != '':
        new_classification_term['parent'] = {'ref': row['parent_classification_term_uri']}
    endpoint = row['repo_uri'] + '/classification_terms'
    return (new_classification_term, endpoint)

@atl.as_tools_logger(logger)
def create_classification_scheme(row):
    '''Combines the create_classification and create_classification_term functions to create a multi-level
    classifcation scheme'''

@atl.as_tools_logger(logger)
def create_digital_objects(row):
    #I am surprised that a repo URI is not required here...
    '''Creates a digital object record.

       Parameters: archival_object_uri, dig_lib_url, thumbail_url, dig_object_id,
       dig_object_title, repo_uri
    '''
    new_digital_object = {'jsonmodel_type': 'digital_object',
                          'publish': True,
                          'file_versions': [{'file_uri': row['dig_lib_url'], 'jsonmodel_type': 'file_version',
                                             'xlink_show_attribute': 'new', 'publish': True},
                                             {'file_uri': row['thumbnail_url'], 'jsonmodel_type': 'file_version',
                                                                              'xlink_show_attribute': 'embed', 'publish': True}],
                          'digital_object_id': row['dig_object_id'],
                          'title': row['dig_object_title']}
    endpoint = row['repo_uri'] + '/digital_objects'
    return (new_digital_object, endpoint)

@atl.as_tools_logger(logger)
def create_digital_object_component(row):
    '''Creates a digital object component record.

       Parameters: repo_uri, parent_uri, component_id, title
    '''
    new_doc = {'component_id': row['component_id'], 'title': row['title'], 'parent': {'ref': row['parent_uri']},
               'repository': {'ref': row['repo_uri']}, 'jsonmodel_type': 'digital_object_component'}
    endpoint = row['repo_uri'] + '/digital_object_components'
    return (new_doc, endpoint)

@atl.as_tools_logger(logger)
def create_child(row):
    '''Creates a minimal child archival object record.

       Parameters: parent_uri, resource_uri, repo_uri, title, level
    '''
    new_ao = {'jsonmodel_type': 'archival_object', 'title': row['title'],
                'level': row['level'], 'parent': {'ref': row['parent_uri']},
                'resource': {'ref': row['resource_uri']}, 'repository': {'ref': row['repo_uri']},
                'publish': True}
    endpoint = row['repo_uri'] + '/archival_objects'
    return (new_ao, endpoint)

@atl.as_tools_logger(logger)
def create_location_profiles(row):
    '''Creates a location profile record.

       Parameters: name, dimension_units, depth, height, width
    '''
    new_location_profile = {'jsonmodel_type': 'location_profile', 'name': row['name'],
                              'dimension_units': row['dimension_units'], 'depth': row['depth'],
                              'height': row['height'], 'width': row['width']
                            }
    return (new_location_profile, '/location_profiles')

@atl.as_tools_logger(logger)
def create_digital_object_instances(record_json, row):
    '''Creates a instance of a digital object linked to an archival object record.

       Parameters: archival_object_uri, new_instance_uri
    '''
    #is there a publish option for this??
    new_ao_instance = {'jsonmodel_type': 'instance', 'instance_type': 'digital_object',
                       'digital_object': {'ref': row['new_instance_uri']}}
    record_json['instances'].append(new_ao_instance)
    return record_json

@atl.as_tools_logger(logger)
def create_locations(row):
    '''Creates a full location record.

       Parameters: barcode, building, room, coordinate_1_label, coordinate_1_indicator,
       coordinate_2_label, coordinate_2_indicator, coordinate_3_label, coordinate_3_indicator,
       location_profile, repo_owner
    '''
    #make the location profile optional??
    new_location = {'jsonmodel_type': 'location', 'barcode': row['barcode'],
                    'building': row['building'], 'room': row['room'],
                    'coordinate_1_label': row['coordinate_1_label'],
                    'coordinate_1_indicator': row['coordinate_1_indicator'],
                    'coordinate_2_label': row['coordinate_2_label'],
                    'coordinate_2_indicator': row['coordinate_2_indicator'],
                    'coordinate_3_label': row['coordinate_3_label'],
                    'coordinate_3_indicator': row['coordinate_3_indicator'],
                    'location_profile': {'ref': row['location_profile']},
                    'owner_repo': {'ref': row['repo_owner']}}
    return (new_location, '/locations')

@atl.as_tools_logger(logger)
def create_events(row):
    '''Creates an event record.

       Parameters: event_type, outcome, date_begin, repo_uri, external_documents,
                   record_link, agent, external_doc_title, external_doc_location

       TO-DO: check if this works'''
    new_event = {'jsonmodel_type': 'event', 'event_type': row['event_type'], 'outcome': row['outcome'],
                'date': {'begin': row['date_begin'], 'date_type': 'single',
                        'jsonmodel_type': 'date', 'label': 'event'},
                'repository': {'ref': '/repositories/' + str(row['repo'])},
                'linked_records': [{'ref': row['record_link'], 'role': 'source'}],
                'linked_agents': [{'role': 'authorizer', 'ref': row['agent']}],
                'external_documents': []}
    if row['external_doc_title'] != '':
        external_document = {'jsonmodel_type': 'external_document', 'location': row['external_doc_location'],
                                'title': row['external_doc_title']}
        new_event['external_documents'].append(external_document)
    #double check if events are scoped to repositories
    return (new_event, '/events')

@atl.as_tools_logger(logger)
def create_top_containers(row):
    '''Creates a top container record.

       Parameters: barcode, indicator, container_profile_uri, location_uri,
                   start_date, repo_uri

    TO-DO: make sure that sub-containers can only be added to instance records,
    not anywhere within a container record. Almost certain this is this case.
    '''
    new_top_container = {'jsonmodel_type': 'top_container', 'indicator': row['indicator'],
                         'repository': {'ref': row['repo_uri']},
                         'container_locations': [{'jsonmodel_type': 'container_location',
                                                  'status': 'current', 'ref': row['location_uri'],
                                                  'start_date': row['start_date']}]}
    if row['barcode'] != '':
        new_top_container['barode'] = row['barcode']
    if row['container_profile_uri'] != '':
        new_top_container['container_profile'] = {'ref': container_profile_uri}
    endpoint = row['repo_uri'] + '/top_containers'
    return (new_top_container, endpoint)

@atl.as_tools_logger(logger)
def create_instances(record_json, row):
    '''Creates an instance of a top container and links to an archival object record.

       Parameters: record_uri, tc_uri, child_type, child_indicator, grandchild_type,
                   grandchild_indicator, instance_type
    '''
    new_instance = {'jsonmodel_type': 'instance', 'instance_type': row['instance_type'],
                    'sub_container': {'jsonmodel_type': 'sub_container',
                                      'top_container': {'ref': row['tc_uri']}}}
    if row['child_type'] != '':
        new_instance['sub_container']['type_2'] = row['child_type']
        new_instance['sub_container']['indicator_2'] = row['child_indicator']
    if row['grandchild_type'] != '':
        new_instance['sub_container']['type_3'] = row['grandchild_type']
        new_instance['sub_container']['indicator_3'] = row['grandchild_indicator']
    record_json['instances'].append(new_instance)
    return record_json

@atl.as_tools_logger(logger)
def create_multipart_note(record_json, row):
    '''Creates a multipart note and links it to a descriptive record.

       Parameters: record_uri, note_string, note_type
    '''
    new_note = {'jsonmodel_type': 'note_multipart',
                'publish': True,
                'subnotes': [{'content': row['note_string'],
                          'jsonmodel_type': 'note_text',
                          'publish': True}],
            'type': row['note_type']}
    record_json['notes'].append(new_note)
    return record_json

@atl.as_tools_logger(logger)
def create_container_profiles(row):
    '''Creates a container profile record.

       Paramaters: name, extent_dimension, height, width, depth, dimension_units
    '''
    new_container_profile = {'jsonmodel_type': 'container_profile', 'name': row['name'],
                             'extent_dimension': row['extent_dimension'], 'height': row['height'],
                             'width': row['width'], 'depth': row['depth'], 'dimension_units': row['dimension_units']}
    return (new_container_profile, '/container_profiles')

@atl.as_tools_logger(logger)
def create_hm_external_ids(record_json, row):
    '''Creates an external ID subrecord and links it to a descriptive record.

       Parameters: uri, hm_number
    '''
    new_external_id = {'jsonmodel_type': 'external_id',
                        'external_id': row['hm_number'],
                        'source': 'local_surrogate_call_number'}
    if record_json['external_ids']:
        ex_ids = [e['external_id'] for e in record_json['external_ids']]
        if hm_number in ex_ids:
            print('Record already has HM external ID')
        else:
            record_json['external_ids'].append(new_external_id)
    else:
        record_json['external_ids'].append(new_external_id)
    # else:
    #     record_json['external_ids'] = [new_external_id]
    #record_json = add_access_notes(record_json, row)
    return record_json

@atl.as_tools_logger(logger)
def create_file_version(record_json, row):
    '''Creates a single file version record and adds it to a digital object record.

       Parameters: uri, file_version_url, xlink_show_attribute
    '''
    new_file_version = {'jsonmodel_type': 'file_version', 'file_uri': row['file_version_url'],
                        'publish': True, 'xlink_show_attribute': row['xlink_show_attribute']}
    record_json['file_versions'].append(new_file_version)
    return record_json

@atl.as_tools_logger(logger)
def create_file_versions(record_json, row):
    '''Creates multiple file versions and adds them to a digital object record.

       Parameters: uri, file_version_url_01, file_version_url_02, digital_object_id
    '''
    record_json['publish'] = True
    record_json['digital_object_id'] = row['digital_object_id']
    #digital library link
    file_version_01 = {'file_uri': row['file_version_url_01'], 'jsonmodel_type': 'file_version',
                                   'xlink_show_attribute': 'new', 'publish': True}
    #thumbnail link
    file_version_02 = {'file_uri': row['file_version_url_02'], 'jsonmodel_type': 'file_version',
                                  'xlink_show_attribute': 'embed', 'publish': True}
    record_json['file_versions'].extend([file_version_01, file_version_02])
    return record_json


#change this - just applies to UseSurrogate right now
@atl.as_tools_logger(logger)
def create_access_notes(record_json, row):
    '''Creates an accessrestrict note for HM microfilm surrogates and
       links it to a descriptive record.

       Parameters: uri, external_id
    '''
    note_text = f"This material has been microfilmed. Patrons must use {row['external_id']} instead of the originals."
    new_note = {'jsonmodel_type': 'note_multipart',
                'publish': True,
                'subnotes': [{'content': note_text,
                          'jsonmodel_type': 'note_text',
                          'publish': True}],
                'type': 'accessrestrict',
                'rights_restriction': {'local_access_restriction_type': ['UseSurrogate']}}
    record_json['notes'].append(new_note)
    return record_json

@atl.as_tools_logger(logger)
def create_local_access_restriction(record_json, row):
    '''Creates a local access restriction type and links it to an existing note in a
       descriptive record.

       Parameters: uri, persistent_id, local_type
    '''
    for note in record_json['notes']:
        if note['persistent_id'] == row['persistent_id']:
            note['rights_restriction']['local_access_restriction_type'].append(row['local_type'])
    return record_json

@atl.as_tools_logger(logger)
def create_timebound_restriction(record_json, row):
    '''Creates a timebound restriction type and links it to a note in a descriptive
       record.

       Parameters: uri, persistent_id, begin, end
    '''
    for note in record_json['notes']:
        if note['persistent_id'] == row['persistent_id']:
            #this might not work for some of the older records which
            #don't have the rights restriction dictionary
            note['rights_restriction']['begin'] = row['begin']
            note['rights_restriction']['end'] = row['end']
    return record_json

'''
-----------------------
UPDATE RECORD FUNCTIONS
-----------------------
'''

@atl.as_tools_logger(logger)
def update_identifiers(record_json, row):
    '''Moves resource identifiers which are split across multiple fields into a
       single field.

       Parameters: uri, identifier
    '''
    record_json['id_0'] = row['identifier']
    if 'id_1' in record_json:
        del record_json['id_1']
    if 'id_2' in record_json:
        del record_json['id_2']
    if 'id_3' in record_json:
        del record_json['id_3']
    return record_json

@atl.as_tools_logger(logger)
def update_container_type(record_json, row):
    '''Updates the container type of a top container record.

       Parameters: uri, container_type
    '''
    record_json['type'] = container_type
    return record_json

@atl.as_tools_logger(logger)
def link_agent_to_record(record_json, row):
    '''Links an agent record to a descriptive record.

       Parameters: agent_uri, record_uri
    '''
    record_json['linked_agents'].append({'ref': row['agent_uri']})
    return record_json

@atl.as_tools_logger(logger)
def link_event_to_record(record_json, row):
    '''Links an event record to a descriptive record.

       Parameters: record_uri, event_uri
    '''
    record_json['linked_events'].append({'ref': row['event_uri']})
    return record_json

@atl.as_tools_logger(logger)
def link_record_to_classification(record_json, row):
    '''Links a record to a classification or classification term

       Parameters: classification_uri, record_uri

       TO-DO: check if possible to link records to other types of
       records such as agents
    '''
    record_json['linked_records'].append({'ref': row['record_uri']})
    return record_json

#abstract
@atl.as_tools_logger(logger)
def update_top_containers(record_json, row):
    '''Updates a top container record with barcode and adds a type value of 'Box'
       to the record.

       Parameters: tc_uri, barcode
    '''
    record_json['barcode'] = row['barcode']
    record_json['type'] = 'Box'
    new_location = {'jsonmodel_type': 'container_location', 'ref': '/locations/9', 'status': 'current', 'start_date': '2017-03-01'}
    record_json['container_locations'].append(new_location)
    return record_json

@atl.as_tools_logger(logger)
def update_dates(record_json, row):
    '''Updates date subrecords'''

@atl.as_tools_logger(logger)
def update_date_type(record_json, row):
    '''Checks whether a date lacks end value, or whether the begin and end values
      and if either are true changes the date type to 'single'

      Parameters: uri
    '''
    for date in record_json['dates']:
        if 'end' not in date:
            date['date_type'] = 'single'
        elif date['end'] == date['begin']:
            date['date_type'] = 'single'
    return record_json

@atl.as_tools_logger(logger)
def update_folder_numbers(record_json, row):
    '''Updates indicator numbers in instance subrecords.

       Parameters: uri, old_folder, new_folder
    '''
    for instance in record_json['instances']:
        if instance['indicator_2'] == row['old_folder']:
            instance['indicator_2'] = row['new_folder']
    return record_json

@atl.as_tools_logger(logger)
def update_revision_statements(record_json, row):
    '''Updates a revision statement.

       Parameters: uri, revision_date, old_text, new_text
    '''
    for revision_statement in record_json['revision_statements']:
        if revision_statement['description'] == row['old_text']:
            revision_statement['description'] = row['new_text']
    return record_json

@atl.as_tools_logger(logger)
def update_notes(record_json, row):
    '''Updates singlepart or multipart notes.

       Parameters: uri, persistent_id, new_text
    '''
    for note in record_json['notes']:
        if note['jsonmodel_type'] == 'note_multipart':
            if note['persistent_id'] == persistent_id:
                note['subnotes'][0]['content'] = note_text
        elif note['jsonmodel_type'] == 'note_singlepart':
            if note['persistent_id'] == persistent_id:
                note['content'] = [note_text]
    return record_json

@atl.as_tools_logger(logger)
def update_access_notes(record_json, row):
    '''Updates existing accessrestrict notes for HM films.

       Parameters: uri, persistent_id, external_id
    '''
    note_text = f"This material has been microfilmed. Patrons must use {external_id} instead of the originals"
    for note in record_json['notes']:
        if note['persistent_id'] == row['persistent_id']:
            note['subnotes'][0]['content'] = row['note_text']
            note['rights_restriction'] = {'local_access_restriction_type': ['UseSurrogate']}
    return record_json

@atl.as_tools_logger(logger)
def update_locations(record_json, row):
    '''Updates location records with barcodes, location profiles, repositories,
       and, optionally, coordinate 1 indicator

       Parameters: uri, barcode, location_profile, owner_repo, coordinate_2_indicator
    '''
    record_json['barcode'] = row['barcode']
    record_json['location_profile'] = {'ref': row['location_profile']}
    record_json['owner_repo'] = {'ref': row['owner_repo']}
    if row['coordinate_2_indicator'] != '':
        record_json['coordinate_2_indicator'] = row['coordinate_2_indicator']
    return record_json

@atl.as_tools_logger(logger)
def update_location_coordinates(record_json, row):
    '''Updates location labels and indicators.

       Parameters: coordinate_1_label, coordinate_1_indicator, coordinate_2_label,
                   coordinate_2_indicator, coordinate_3_label, coordinate_3_indicator
    '''
    record_json['coordinate_1_indicator'] = row['coordinate_1_indicator']
    record_json['coordinate_1_label'] = row['coordinate_1_label']
    record_json['coordinate_2_indicator'] = row['coordinate_2_indicator']
    record_json['coordinate_2_label'] = row['coordinate_2_label']
    record_json['coordinate_3_indicator'] = row['coordinate_3_indicator']
    record_json['coordinate_3_label'] = row['coordinate_3_label']
    return record_json

@atl.as_tools_logger(logger)
def update_record_component(record_json, row):
    '''Updates a non-nested field in a top-level record

       Parameters: record_uri, updated_text

       NOTE: Changed the valued to title for testing purposes; need to add a
       component type argument
    '''
    record_json['title'] = row['updated_text']
    return record_json

@atl.as_tools_logger(logger)
def update_record_components(record_json, row):
    '''Updates non-nested fields in a top-level record

       Parameters: uri, fields, values

       NOTE: fields must match JSON keys in AS JSON response
    '''
    for field, value in row.items():
        if field != 'uri':
            record_json[field] = value
    return record_json

#also need to define the subrecord here.
@atl.as_tools_logger(logger)
def update_subrecord_component(record_json, row):
    '''Updates a nested field in a top-level record

       Parameters: uri, subrecord, component, updated_text


       TODO: is this even necessary?
    '''
    for item in record_json[subrecord]:
            item[component] = row['updated_text']
    return record_json

#also need to define the subrecord here...
@atl.as_tools_logger(logger)
def update_subrecord_components(record_json, row):
    '''Updates nested fields in a top-level record

       Parameters: uri, fields, values

       NOTE: fields must match JSON keys in AS JSON response
    '''
    for field, value in row.items():
        if field != 'uri':
            for item in record_json[subrecord]:
                item[field] = value

@atl.as_tools_logger(logger)
def update_record_pub_status(record_json, row):
    '''Updates publication status of top-level record

       Parameters: uri, updated_status
    '''
    if row['updated_status'] == '1':
        record_json['publish'] = True
    elif row['updated_status'] == '0':
        record_json['publish'] = False
    return record_json

@atl.as_tools_logger(logger)
def update_subrecord_pub_status(record_json, row):
    '''Updates publication status of subrecord

       Parameters: uri, subrecord, updated_status
    '''
    pass

#if the subnote is also unpublished will need to fix that as well
@atl.as_tools_logger(logger)
def update_note_pub_status(record_json, row):
    '''Updates publication status of a note

       Parameters: uri, persistent_id, updated_status

       NOTE: also need to change pub status of sub-notes...
    '''
    for note in record_json['notes']:
        if note['persistent_id'] == row['persistent_id']:
            if row['updated_status'] == '1':
                note['publish'] = True
            elif row['updated_status'] == '0':
                note['publish'] = False
    return record_json

@atl.as_tools_logger(logger)
def update_names(record_json, row):
    '''Updates name records to fix improper field usages

       Parameters: uri, sort_name, primary_name, rest_of_name, dates, prefix,
                   suffix, title, qualifier, name_order
    '''
    for name in record_json['names']:
        if 'is_display_name' in name:
            if name['is_display_name']:
                if name['sort_name'] == row['sort_name']:
                    name['primary_name'] = row['primary_name']
                    name['rest_of_name'] = row['rest_of_name']
                    name['dates'] = row['dates']
                    name['prefix'] = row['prefix']
                    name['suffix'] = row['suffix']
                    name['title'] = row['title']
                    name['qualifier'] = row['qualifier']
                    name['name_order'] = row['name_order']
    return record_json

@atl.as_tools_logger(logger)
def update_sources_auth_ids(record_json, row):
    '''Updates an agent record with a source value of 'local' and removes vendor-added
       authority ID codes. Used for agents and subjects remediation project.

       Parameters: uri
    '''
    if 'display_name' in record_json:
        if 'authority_id' not in record_json['display_name']:
            if record_json['display_name']['source'] != 'local':
                for name in record_json['names']:
                    if name['sort_name'] == record_json['display_name']['sort_name']:
                        if 'authority_id' not in name:
                            name['source'] = 'local'
        if 'authority_id' in record_json['display_name']:
            if 'http' not in record_json['display_name']['authority_id']:
                if 'dts' in record_json['display_name']['authority_id']:
                    for name in record_json['names']:
                        if name['sort_name'] == record_json['display_name']['sort_name']:
                            if name['authority_id'] == record_json['display_name']['authority_id']:
                                del name['authority_id']
                        if name['source'] != 'local':
                            name['source'] = 'local'

'''
-----------------------
DELETE RECORD FUNCTIONS
-----------------------
'''

#so, for some reason I was able to do this - but deleting the whole instance will not work
@atl.as_tools_logger(logger)
def delete_subcontainers(record_json):
    '''Deletes a sub_container subrecord in an instance subrecord

       Parameters: uri
    '''
    for instance in record_json['instances']:
        if 'sub_container' in instance:
            if 'type_2' in instance['sub_container']:
                if instance['sub_container']['type_2'] == 'reel':
                    del instance['sub_container']['type_2']
                    del instance['sub_container']['indicator_2']
            if 'type_3' in instance['sub_container']:
                if instance['sub_container']['type_3'] == 'reel':
                    del instance['sub_container']['type_3']
                    del instance['sub_container']['indicator_3']
    return record_json

@atl.as_tools_logger(logger)
def delete_notes(record_json):
    '''Deletes a note subrecord in a descriptive record

       Parameters: uri, persistent_id
    '''
    for note in record_json['notes']:
        if note['persistent_id'] == row['persistent_id']:
            note.clear()
    return record_json

@atl.as_tools_logger(logger)
def delete_rights_restriction(record_json):
    '''Deletes a local access restriction in an accessrestrict note

       Parameters: uri, persistent_id
    '''
    for note in record_json['notes']:
        if note['persistent_id'] == row['persistent_id']:
            if 'rights_restriction' in note:
                del note['rights_restriction']
    return record_json

@atl.as_tools_logger(logger)
def delete_instances(record_json):
    '''Deletes an instance

    TO-DO: check if this can be extracted to all subrecords
    Make sure to use the .clear() method'''

# def add_access_notes(record_json, row):
#     exists = 0
#     if len(record_json['notes']) > 0:
#         for note in record_json['notes']:
#             if note['type'] == 'accessrestrict':
#                 if 'This material has been microfilmed' in note['subnotes'][0]['content']:
#                     print('Note exists!')
#                     exists = 1
#     if exists == 0:
#         record_json = new_use_surrogate_notes.create_access_note(record_json, row)
#     return record_json

'''
-----------------------
GET RECORD FUNCTIONS
-----------------------
'''

@atl.as_tools_logger(logger)
def get_series(record_json, row):
    '''Gets a list of series-level ancestors for a list of URIs

       Parameters: uri
    '''
    for ancestor in record_json['ancestors']:
        if ancestor['level'] == 'series':
            row.append(ancestor['ref'])
    return (row, record_json)

@atl.as_tools_logger(logger)
def get_agents(agent_json):
    '''Retrieves data about agents

       Parameters: uri
    '''
    data = []
    if 'agent_type' in agent_json:
        data.append(agent_json['agent_type'])
    else:
        data.append('no_agent_type')
    if 'create_time' in agent_json:
        data.append(agent_json['create_time'])
    else:
        data.append('no_create_time')
    if 'created_by' in agent_json:
        data.append(agent_json['created_by'])
    else:
        data.append('no_created_by')
    if 'display_name'in agent_json:
        if 'authority_id' in agent_json['display_name']:
            data.append(agent_json['display_name']['authority_id'])
        else:
            data.append('no_authority_id')
        if 'sort_name' in agent_json['display_name']:
            data.append(agent_json['display_name']['sort_name'])
            print(agent_json['display_name']['sort_name'])
        else:
            data.append('no_sort_name')
        if 'primary_name' in agent_json['display_name']:
            data.append(agent_json['display_name']['primary_name'])
        else:
            data.append('no_primary_name')
        if 'corporate_entities' in uri:
            if 'subordinate_name_1' in agent_json['display_name']:
                data.append(agent_json['display_name']['subordinate_name_1'])
            else:
                data.append('no_subordinate_name')
        if 'people' in uri:
            if 'rest_of_name' in agent_json['display_name']:
                data.append(agent_json['display_name']['rest_of_name'])
            else:
                data.append('no_rest_of_name')
        if 'families' in uri:
            data.append('family_name')
        if 'dates' in agent_json['display_name']:
            data.append(agent_json['display_name']['dates'])
        else:
            data.append('no_dates')
        if 'source' in agent_json['display_name']:
            data.append(agent_json['display_name']['source'])
        else:
            data.append('no_source')
        if 'qualifier' in agent_json['display_name']:
            data.append(agent_json['display_name']['qualifier'])
        else:
            data.append('no_qualifier')
    else:
        data.append('no_display_name_')
    if 'is_linked_to_published_record' in agent_json:
        data.append(agent_json['is_linked_to_published_record'])
    else:
        data.append('no_is_linked_to_pub_rec')
    if 'linked_agent_roles' in agent_json:
        data.append(agent_json['linked_agent_roles'])
    else:
        data.append('no_linked_agent_roles')
    if 'title' in agent_json:
        data.append(agent_json['title'])
    else:
        data.append('no_title')
    if 'is_linked_to_record' in agent_json:
        data.append(agent_json['is_linked_to_record'])
    else:
        data.append('no_link_to_record')
    if 'used_within_repositories' in agent_json:
        data.append(agent_json['used_within_repositories'])
    else:
        data.append('not_used_within_repos')
    if 'uri' in agent_json:
        data.append(agent_json['uri'])
    else:
        data.append('no_uri')
    if 'dates_of_existence' in agent_json:
        data.append(agent_json['dates_of_existence'])
    else:
        data.append('no_dates_of_existence')
    if 'agent_contacts' in agent_json:
        data.append(agent_json['agent_contacts'])
    else:
        data.append('no_contact_info')
    if 'notes' in agent_json:
        data.append(agent_json['notes'])
    else:
        data.append('no_notes')
    return data

@atl.as_tools_logger(logger)
def get_subjects(subject_json, row):
    '''Retrieves data about subjects

       Parameters: uri
    '''
    terms = []
    if 'title' in subject_json:
        row.append(subject_json['title'])
    else:
        row.append('NO_VALUE')
    if 'authority_id' in subject_json:
        row.append(subject_json['authority_id'])
    else:
        row.append('NO_VALUE')
    if 'source' in subject_json:
        row.append(subject_json['source'])
    else:
        row.append('NO_VALUE')
    if 'is_linked_to_published_record' in subject_json:
        row.append(subject_json['is_linked_to_published_record'])
    else:
        row.append('NO_VALUE')
    if 'terms' in subject_json:
        for term in subject_json['terms']:
            terms.append([term['term'], term['term_type']])
        row.append(terms)
    else:
        row.append('NO_VALUE')
    if 'used_within_repositories' in subject_json:
        row.append(subject_json['used_within_repositories'])
    else:
        row.append('NO_VALUE')
    if 'created_by' in subject_json:
        row.append(subject_json['created_by'])
    else:
        row.append('NO_VALUE')
    return row
