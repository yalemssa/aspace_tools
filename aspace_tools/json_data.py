#!/usr/bin/python3
#~/anaconda3/bin/python

'''NOTE - LOGGING CURRENTLY TURNED OFF'''


import json
#this is useless right now
#from utilities.decorators import register, PLUGINS

#from aspace_tools import aspace_tools_logging as atl

'''
JSON data structures for ArchivesSpace record creation, update, etc. Called by CRUD functions in
crud.py

Todo:
    register functions and their variables with a decorator; latter doesn't seem very easy; seems like the only way that the arguments get registered is when the function actually gets called???
    change parameter names - have all URIs which are used to call the API just called 'uri'; like, all the ones in csv_row[0]
    Add another argument for update_subrecord_component, etc. to define the subrecord and the component.
    Continue adding stuff from remaining .py files
    also need to work on the templates
    would like to be able to set options - i.e. if something is empty don't add it. Or look for indexing error
'''

#logger = atl.logging.getLogger(__name__)

class ASJsonData():

    def __init__(self):
        '''Nothing here'''

    #@atl.as_tools_logger(logger)
    def create_repositories(self, csv_row):
        '''Creates a repository record.

           Parameters:
            csv_row['repo_name']: The name of the repository

           Returns:
            tuple: The JSON structure and the API endpoint.
        '''
        new_repo = {'jsonmodel_type': 'repository', 'name': csv_row['repo_name']}
        return (new_repo, '/repositories')

    def create_ms_135_archival_objects(self, csv_row):
        '''Creates archival object records for MS 135 reconciliation project

           Parameters:
            csv_row['tc_uri']: The URI of the linked container
            csv_row['type_2']: The child instance type (i.e. folder)
            csv_row['indicator_2']: The child indicator
            csv_row['parent_uri']: The URI of the parent record
            csv_row['title']: The archival_object title
            csv_row['date_expression']: The date expression
            csv_row['date_begin']: The begin date
            csv_row['date_end']: The end date
            csv_row['date_type']: The date type

           Returns:
            tuple: The JSON structure and the API endpoint
        '''
        new_ao = {'jsonmodel_type': 'archival_object', 'title': csv_row['title'], 'level': 'file', 'publish': True,
                    'dates': [{'jsonmodel_type': 'date', 'expression': csv_row['date_expression'],
                                'begin': csv_row['date_begin'], 'end': csv_row['date_end'],
                                'date_type': csv_row['date_type'], 'label': 'creation'}],
                    'instances': [{'jsonmodel_type': 'instance', 'instance_type': 'mixed_materials',
                        'sub_container': {'jsonmodel_type': 'sub_container',
                                          'type_2': csv_row['type_2'],
                                          'indicator_2': csv_row['indicator_2'],
                                          'top_container': {'ref': csv_row['tc_uri']}}}],
                    'parent': {'ref': csv_row['parent_uri']},
                    'resource': {'ref': '/repositories/12/resources/4814'},
                    'repository': {'ref': '/repositories/12'}}
        #if just an empty string delete the key, otherwise the job will fail. Better way to do this?
        if csv_row['parent_uri'] == '':
            del new_ao['parent']
        endpoint = '/repositories/12/archival_objects'
        return (new_ao, endpoint)

    ##@atl.as_tools_logger(logger)
    #want to be able to add instances to these at the same time...
    def create_archival_objects(self, csv_row):
        '''Creates an archival object record.

           Parameters:
            csv_row['title']: The title of the archival object.
            csv_row['resource_uri']: The URI of the parent resource.
            csv_row['repo_uri']: The URI of the parent repository.

           Other Parameters:
            csv_row['date_begin']: The begin date of the archival object. Format YYYY-MM-DD.
            csv_row['date_end']: The end date of the archival object. Format YYYY-MM-DD.
            csv_row['date_type']: The date type, i.e. single, inclusive, bulk.
            csv_row['date_label']: The date label, i.e. creation.
            csv_row['extent_type']: The extent type, i.e. photographs.
            csv_row['extent_portion']: The extent portion, i.e. whole, part.
            csv_row['extent_number']: The extent number, i.e. 1.
            csv_row['parent_uri']: The URI of the parent archival object

           Returns:
            tuple: The JSON structure and the API endpoint.
        '''
        #don't have any instances here right now. Add later. Make optional? Or add the container lookup somehow??
        new_ao = {'jsonmodel_type': 'archival_object', 'title': csv_row['title'], 'level': 'file', 'publish': True,
                    'dates': [{'jsonmodel_type': 'date', 'begin': csv_row['date_begin'], 'end': csv_row['date_end'],
                                'date_type': csv_row['date_type'], 'label': csv_row['date_label']}],
                    'extents': [{'jsonmodel_type': 'extent', 'portion': csv_row['extent_portion'], 'number': csv_row['extent_number'],
                                'extent_type': csv_row['extent_type']}],
                    'parent': {'ref': csv_row['parent_uri']},
                    'resource': {'ref': csv_row['resource_uri']},
                    'repository': {'ref': csv_row['repo_uri']}}
        #if just an empty string delete the key, otherwise the job will fail. Better way to do this?
        if csv_row['extent_type'] == '':
            del new_ao['extents']
        if csv_row['date_type'] == '':
            del new_ao['dates']
        if csv_row['parent_uri'] == '':
            del new_ao['parent']
        endpoint = csv_row['repo_uri'] + '/archival_objects'
        return (new_ao, endpoint)


    def create_minimal_archival_objects(self, csv_row):
        '''Creates a child archival object record with just a title and level.

           Parameters:
            csv_row['parent_uri']: The URI of the parent archival object.
            csv_row['resource_uri']: The URI of the parent resource.
            csv_row['repo_uri']: The URI of the parent repository.
            csv_row['title']: The archival object title
            csv_row['level']: The archival object level, i.e. 'file'

           Returns:
            tuple: The JSON structure and the API endpoint.
        '''
        new_ao = {'jsonmodel_type': 'archival_object', 'title': csv_row['title'], 'level': csv_row['level'], 'publish': True,
                    'parent': {'ref': csv_row['parent_uri']},
                    'resource': {'ref': csv_row['resource_uri']},
                    'repository': {'ref': csv_row['repo_uri']}}
        endpoint = csv_row['repo_uri'] + '/archival_objects'
        return (new_ao, endpoint)

    #@atl.as_tools_logger(logger)
    def create_accessions(self, csv_row):
        '''Creates an accession record.

           Parameters:
            csv_row['repo_uri']: The URI of the parent repository.
            csv_row['identifier']: The accession identifier.
            csv_row['title']: The accession title.
            csv_row['accession_date']: The accession date. Format YYYY-MM-DD

           Returns:
            tuple: The JSON structure and the API endpoint.
        '''
        new_accession = {'id_0': csv_row['identifier'], 'title': csv_row['title'], 'accession_date': csv_row['accession_date'], 'repository': {'ref': csv_row['repo_uri']},
                         'jsonmodel_type': 'accession'}
        endpoint = csv_row['repo_uri'] + '/accessions'
        return (new_accession, endpoint)

    #@atl.as_tools_logger(logger)
    def create_resources(self, csv_row):
        '''Creates a resource record.

           Parameters:
            csv_row['repo_uri']: The URI of the parent repository.
            csv_row['identifier']: The identifier for the resource.
            csv_row['title']: The title of the resource.
            csv_row['language']: The language code of the resource, i.e eng.
            csv_row['level']: The level of the resource, i.e. collection.
            csv_row['date_begin']: The begin date of the resource.
            csv_row['date_end']: The end date of the resource.
            csv_row['date_type']: The date type of the resource, i.e. inclusive, single.
            csv_row['date_label']: The date label of the resource, i.e. creation.
            csv_row['extent_type']: The extent type of the resource, i.e. photograph.
            csv_row['extent_portion']: The extent portion of the resource, i.e. whole, part.
            csv_row['extent_number']: The extent number of the resource, i.e. 1.
            csv_row['container_summary']: The container summary of the resource.

           Returns:
            tuple: The JSON structure and the API endpoint.

           Todo:
            Make some of these optional, add options for notes, etc.
            Make date end optional; what about multiple extents, etc?
        '''
        new_resource = {'id_0': csv_row['identifier'], 'title': csv_row['title'], 'language': csv_row['language'], 'level': csv_row['level'],
                        'dates' : [{'begin': csv_row['begin_date'], 'end': csv_row['end_date'], 'date_type': csv_row['date_type'], 'label': csv_row['date_label'],
                                    'jsonmodel_type': 'date'}],
                        'extents': [{'extent_type': csv_row['extent_type'], 'portion': csv_row['extent_portion'], 'number': csv_row['extent_number'],
                                     'container_summary': csv_row['container_summary'], 'jsonmodel_type': 'extent'}],
                        'repository': {'ref': csv_row['repo_uri']}, 'jsonmodel_type': 'resource'}
        endpoint = csv_row['repo_uri'] + '/resources'
        return (new_resource, endpoint)

    #@atl.as_tools_logger(logger)
    def create_classification(self, csv_row):
        '''Creates a classification record.

           Parameters:
            csv_row['repo_uri']: The URI of the parent repository.
            csv_row['identifier']: The identifier of the classification.
            csv_row['title']: The title of the classification.
            csv_row['description']: The description of the classification.

           Returns:
            tuple: The JSON structure and the API endpoint.
        '''
        new_classification = {'jsonmodel_type': 'classification', 'identifier': csv_row['identifier'],
                              'title': csv_row['title'], 'description': csv_row['description'], 'repository': {'ref': csv_row['repo_uri']}}
        endpoint = csv_row['repo_uri'] + '/classifications'
        return (new_classification, endpoint)

    #@atl.as_tools_logger(logger)
    def create_classification_term(self, csv_row):
        '''Creates a classification term with or without a classification term parent.

           Parameters:
            csv_row['parent_classification_uri']: The URI of the parent classification.
            csv_row['repo_uri']: The URI of the parent repository.
            csv_row['title']: The title of the classification term.
            csv_row['description']: The description of the classification term

           Other Parameters:
            csv_row['parent_classification_term_uri']: The URI of the parent classification term.

           Returns:
            tuple: The JSON structure and the API endpoint.
        '''
        new_classification_term = {'jsonmodel_type': 'classification_term', 'identifier': csv_row['identifier'],
                                   'title': csv_row['title'], 'description': csv_row['description'], 'classification': {'ref': csv_row['parent_classification_uri']},
                                   'repository': {'ref': csv_row['repo_uri']}}
        if csv_row['parent_classification_term_uri'] != '':
            new_classification_term['parent'] = {'ref': csv_row['parent_classification_term_uri']}
        endpoint = csv_row['repo_uri'] + '/classification_terms'
        return (new_classification_term, endpoint)

    #@atl.as_tools_logger(logger)
    def create_classification_scheme(self, csv_row):
        '''Combines the create_classification and create_classification_term functions to create a multi-level
           classifcation scheme.

           Parameters:
            csv_row
        '''

    #@atl.as_tools_logger(logger)
    def create_digital_objects(self, csv_row):
        #I am surprised that a repo URI is not required here...
        '''Creates a digital object record.

           Parameters:
            csv_row['archival_object_uri']: The URI of the linked archival object.
            csv_row['dig_lib_url']: The URL of the digital library item.
            csv_row['thumbnail_url']: The URL of the thumbnail image.
            csv_row['dig_object_id']: The digital object identifier.
            csv_row['dig_object_title']: The digital object title.
            csv_row['repo_uri']: The URI of the parent repository.

           Returns:
            tuple: The JSON structure and the API endpoint.

           Todo:
            Change variable names to something more abstract.
        '''
        new_digital_object = {'jsonmodel_type': 'digital_object',
                              'publish': True,
                              'file_versions': [{'file_uri': csv_row['dig_lib_url'], 'jsonmodel_type': 'file_version',
                                                 'xlink_show_attribute': 'new', 'publish': True},
                                                 {'file_uri': csv_row['thumbnail_url'], 'jsonmodel_type': 'file_version',
                                                                                  'xlink_show_attribute': 'embed', 'publish': True}],
                              'digital_object_id': csv_row['dig_object_id'],
                              'title': csv_row['dig_object_title']}
        endpoint = csv_row['repo_uri'] + '/digital_objects'
        return (new_digital_object, endpoint)

    #@atl.as_tools_logger(logger)
    def create_digital_object_component(self, csv_row):
        '''Creates a digital object component record.

           Parameters:
            csv_row['repo_uri']: The URI of the parent repository.
            csv_row['parent_uri']: The URI of the digital object parent.
            csv_row['component_id']: The identifier of the digital object component.
            csv_row['title']: The title of the digital object component.

           Returns:
            tuple: The JSON structure and the API endpoint.
        '''
        new_doc = {'component_id': csv_row['component_id'], 'title': csv_row['title'], 'parent': {'ref': csv_row['parent_uri']},
                   'repository': {'ref': csv_row['repo_uri']}, 'jsonmodel_type': 'digital_object_component'}
        endpoint = csv_row['repo_uri'] + '/digital_object_components'
        return (new_doc, endpoint)

    #@atl.as_tools_logger(logger)
    def create_child(self, csv_row):
        '''Creates a minimal child archival object record.

           Parameters:
            csv_row['parent_uri']: The URI of the parent archival object.
            csv_row['resource_uri']: The URI of the parent resource.
            csv_row['repo_uri']: The URI of the parent repository.
            csv_row['title']: The title of the archival object.
            csv_row['level']: The level of description of the archival object, i.e. file.

           Returns:
            tuple: The JSON structure and the API endpoint.
        '''
        new_ao = {'jsonmodel_type': 'archival_object', 'title': csv_row['title'],
                    'level': csv_row['level'], 'parent': {'ref': csv_row['parent_uri']},
                    'resource': {'ref': csv_row['resource_uri']}, 'repository': {'ref': csv_row['repo_uri']},
                    'publish': True}
        endpoint = csv_row['repo_uri'] + '/archival_objects'
        return (new_ao, endpoint)

    def create_subseries(self, csv_row):
        '''Creates a subseries record.

           Parameters:
            csv_row['name']: The title of the archival object.
            csv_row['resource_uri']: The URI of the parent resource.
            csv_row['repo_uri']: The URI of the parent repository.
            csv_row['parent_uri']: The URI of the parent archival object.

           Returns:
            tuple: The JSON structure and the API endpoint.
        '''
        new_ao = {'jsonmodel_type': 'archival_object', 'title': csv_row['name'],
                    'level': 'subseries', 'parent': {'ref': csv_row['parent_uri']},
                    'resource': {'ref': csv_row['resource_uri']}, 'repository': {'ref': csv_row['repo_uri']},
                    'publish': True}
        endpoint = csv_row['repo_uri'] + '/archival_objects'
        return (new_ao, endpoint)

    #@atl.as_tools_logger(logger)
    def create_location_profiles(self, csv_row):
        '''Creates a location profile record.

           Parameters:
            csv_row['name']: The name of the location profile.
            csv_row['dimension_units']: The dimension units of the location profile.
            csv_row['depth']: The depth of the location profile.
            csv_row['height']: The height of the location profile.
            csv_row['width']: The width of the location profile.

           Returns:
            tuple: The JSON structure and the API endpoint.
        '''
        new_location_profile = {'jsonmodel_type': 'location_profile', 'name': csv_row['name'],
                                  'dimension_units': csv_row['dimension_units'], 'depth': csv_row['depth'],
                                  'height': csv_row['height'], 'width': csv_row['width']
                                }
        return (new_location_profile, '/location_profiles')

    #@atl.as_tools_logger(logger)
    def create_digital_object_instances(self, record_json, csv_row):
        '''Creates a instance of a digital object linked to an archival object record.

           Parameters:
            record_json: The JSON representation of the archival object.
            csv_row['archival_object_uri']: The URI of the archival object record.
            csv_row['new_instance_uri']: The URI of the digital object to link.

           Returns:
            tuple: The JSON structure and the API endpoint.
        '''
        #is there a publish option for this??
        new_ao_instance = {'jsonmodel_type': 'instance', 'instance_type': 'digital_object',
                           'digital_object': {'ref': csv_row['new_instance_uri']}}
        record_json['instances'].append(new_ao_instance)
        return record_json

    #@atl.as_tools_logger(logger)
    def create_locations(self, csv_row):
        '''Creates a full location record.

           Parameters:
            csv_row['barcode']: The barcode of the location.
            csv_row['building']: The building of the location.
            csv_row['room']: The room of the location.
            csv_row['coordinate_1_label']: The label for coordinate_1, i.e. range.
            csv_row['coordinate_1_indicator']: The indicator for coordinate_1, i.e. 1.
            csv_row['coordinate_2_label']: The label for coordinate_2, i.e. section.
            csv_row['coordinate_2_indicator']: The indicator for coordinate_2, i.e. A.
            csv_row['coordinate_3_label']: The label for coordinate_3, i.e. shelf.
            csv_row['coordinate_3_indicator']: The indicator for coordinate_3, i.e. 4.
            csv_row['location_profile']: The URI of the location profile.
            csv_row['repo_owner']: The URI of the parent repository.

           Returns:
            tuple: The JSON structure and the API endpoint.
        '''
        #make the location profile optional??
        new_location = {'jsonmodel_type': 'location', 'barcode': csv_row['barcode'],
                        'building': csv_row['building'], 'room': csv_row['room'],
                        'coordinate_1_label': csv_row['coordinate_1_label'],
                        'coordinate_1_indicator': csv_row['coordinate_1_indicator'],
                        'coordinate_2_label': csv_row['coordinate_2_label'],
                        'coordinate_2_indicator': csv_row['coordinate_2_indicator'],
                        'coordinate_3_label': csv_row['coordinate_3_label'],
                        'coordinate_3_indicator': csv_row['coordinate_3_indicator'],
                        'location_profile': {'ref': csv_row['location_profile']},
                        'owner_repo': {'ref': csv_row['repo_owner']}}
        return (new_location, '/locations')

    #@atl.as_tools_logger(logger)
    def create_dates(self, record_json, csv_row):
        '''Creates a date record.

           Parameters:
            csv_row['date_type']: The date type (i.e. inclusive, single)
            csv_row['date_label']: The date label (i.e. creation, broadcast)
            csv_row['begin']: The begin date (YYYY-MM-DD)
            csv_row['end']: The end date (YYYY-MM-DD)

           Returns:
            dict: The JSON structure.
        '''
        for date in record_json['dates']:
            #want to check and see if there's already a matching date
            if date.get('date_type') == 'single':
                if date.get('begin') == csv_row['begin']:
                    return record_json
            elif date.get('date_type') == 'inclusive':
                if (date.get('begin') == csv_row['begin'] and date.get('end') == csv_row['end']):
                    return record_json
        #this should only happen if the other conditions aren't met
        new_date = {'jsonmodel_type': 'date', 'begin': csv_row['begin'],
                     'date_type': csv_row['date_type'], 'label': csv_row['date_label']}
        if csv_row['end'] != '':
            new_date['end'] = csv_row['end']
        record_json['dates'].append(new_date)
        return record_json

    def create_extents(self, record_json, csv_row):
        '''Creates an extent record.

           Parameters:
            csv_row['extent_type']: The extent type (i.e. linear_feet)
            csv_row['extent_portion']: Whole or part
            csv_row['extent_number']: The quantity

           Returns:
            dict: The JSON structure.
        '''
        new_extent = {'jsonmodel_type': 'extent', 'portion': csv_row['extent_portion'], 'number': csv_row['extent_number'],
            'extent_type': csv_row['extent_type']}
        record_json['extents'].append(new_extent)
        return record_json

    #@atl.as_tools_logger(logger)
    def create_events(self, csv_row):
        '''Creates an event record.

           Parameters:
            csv_row['event_type']: The event type.
            csv_row['outcome']: The event outcome.
            csv_row['date_begin']: The begin date of the event.
            csv_row['repo_uri']: The URI of the parent repository
            csv_row['record_link']: The URI of the record to link.
            csv_row['agent']: The URI of the agent authorizer.

           Other Parameters:
            csv_row['external_doc_title']: The title of the external document.
            csv_row['external_doc_location']: The location of the external document.

           Returns:
            tuple: The JSON structure and the API endpoint.

           Todo:
            check if this works'''
        new_event = {'jsonmodel_type': 'event', 'event_type': csv_row['event_type'], 'outcome': csv_row['outcome'],
                    'date': {'begin': csv_row['date_begin'], 'date_type': 'single',
                            'jsonmodel_type': 'date', 'label': csv_row['date_label']},
                    'repository': {'ref': csv_row['repo_uri']},
                    'linked_records': [{'ref': csv_row['record_link'], 'role': csv_row['record_role']}],
                    'linked_agents': [{'role': csv_row['agent_role'], 'ref': csv_row['agent_uri']}],
                    'external_documents': []}
        # if csv_row.get('external_doc_title') != '':
        #     external_document = {'jsonmodel_type': 'external_document', 'location': csv_row['external_doc_location'],
        #                             'title': csv_row['external_doc_title']}
        #     new_event['external_documents'].append(external_document)
        #double check if events are scoped to repositories
        return (new_event, csv_row['repo_uri'] + '/events')

    ##@atl.as_tools_logger(logger)
    def create_top_containers(self, csv_row):
        '''Creates a top container record.

           Parameters:
            csv_row['indicator']: The indicator for the top container (i.e. box number).
            csv_row['repo_uri']: The URI of the parent repository.

           Other Parameters:
            csv_row['type']: The top container type.
            csv_row['barcode']: The top container barcode.
            csv_row['container_profile_uri']: The URI of the top container container profile.
            csv_row['location_uri']: The URI of the container location.
            csv_row['start_date']: The date when the top container was added to the location.

           Returns:
            tuple: The JSON structure and the API endpoint.

           Todo:
            make sure that sub-containers can only be added to instance records, not anywhere within a container record. Almost certain this is this case.
        '''
        new_top_container = {'jsonmodel_type': 'top_container', 'indicator': csv_row['indicator'],
                             'repository': {'ref': csv_row['repo_uri']}}
        if csv_row['type'] != '':
            new_top_container['type'] = csv_row['type']
        if csv_row['barcode'] != '':
            new_top_container['barcode'] = csv_row['barcode']
        if csv_row['container_profile_uri'] != '':
            #eventually add way to search by container profile name
            #container_profile_uri = crud.search_container_profiles()
            new_top_container['container_profile'] = {'ref': csv_row['container_profile_uri']}
        if csv_row['location_uri'] != '':
            new_location = [{'jsonmodel_type': 'container_location',
                                     'status': 'current', 'ref': csv_row['location_uri'],
                                     'start_date': csv_row['start_date']}]
            new_top_container['container_locations'] = new_location
        endpoint = csv_row['repo_uri'] + '/top_containers'
        return (new_top_container, endpoint)

    def update_instance_by_uri(self, record_json, csv_row):
        '''Updates an instance subrecord with sub_container data.

           Parameters:
            record_json: The JSON representation of the archival object.
            csv_row['uri']: The URI of the archival object record.
            csv_row['tc_uri']: The URI of the top container.
            csv_row['type_2']: The sub_container type, i.e. folder.
            csv_row['indicator_2']: The sub_container number, i.e. 1.

           Returns:
            dict: The JSON structure.
        '''
        for instance in record_json['instances']:
            if instance['sub_container']['top_container']['ref'] == csv_row['tc_uri']:
                instance['sub_container']['type_2'] = csv_row['type_2']
                instance['sub_container']['indicator_2'] = csv_row['indicator_2']
        return record_json

    def update_indicator_2(self, record_json, csv_row):
        '''Updates an instance subrecord with a new indicator_2.

           Parameters:
            record_json: The JSON representation of the archival object.
            csv_row['uri']: The URI of the archival object record.
            csv_row['tc_uri']: The URI of the top container.
            csv_row['indicator_2']: The sub_container number, i.e. 1.

           Returns:
            dict: The JSON structure.
        '''
        for instance in record_json['instances']:
            if instance['sub_container']['top_container']['ref'] == csv_row['tc_uri']:
                    instance['sub_container']['indicator_2'] = csv_row['indicator_2']
        return record_json

    #@atl.as_tools_logger(logger)
    def create_instances(self, record_json, csv_row):
        '''Creates an instance of a top container and links to an archival object record.

           Parameters:
            record_json: The JSON representation of the archival object.
            csv_row['uri']: The URI of the archival object record.
            csv_row['tc_uri']: The URI of the top container.
            csv_row['instance_type']: The instance type, i.e. mixed materials.

           Other Parameters:
            csv_row['child_type']: The child type, i.e. Folder.
            csv_row['child_indicator']: The child indicator, i.e. 25.
            csv_row['grandchild_type']: The grandchild type, i.e. item.
            csv_row['grandchild_indicator']: The grandchild indicator, i.e 78.

           Returns:
            dict: The JSON structure.
        '''
        new_instance = {'jsonmodel_type': 'instance', 'instance_type': csv_row['instance_type'],
                        'sub_container': {'jsonmodel_type': 'sub_container',
                                          'top_container': {'ref': csv_row['tc_uri']}}}
        #CHANGE THIS TO if 'child_type' in csv_row!!!!!!!!! Change for others too
        if csv_row['child_type'] != '':
            new_instance['sub_container']['type_2'] = csv_row['child_type']
            new_instance['sub_container']['indicator_2'] = csv_row['child_indicator']
        if csv_row['grandchild_type'] != '':
            new_instance['sub_container']['type_3'] = csv_row['grandchild_type']
            new_instance['sub_container']['indicator_3'] = csv_row['grandchild_indicator']
        record_json['instances'].append(new_instance)
        return record_json

# def create_ordered_list(self, record_json, csv_row):
#     '''Creates a ordered list note and links it to a descriptive record.
#
#        Parameters:
#         record_json: The JSON representation of the parent record.
#         csv_row['record_uri']: The URI of the parent record.
#         csv_row['note_string']: The note text.
#         csv_row['note_type']: The note type, i.e. accessrestrict
#
#        Returns:
#         dict: The JSON structure.
#     '''
# 	return {'jsonmodel_type': 'note_multipart',
# 			'label': label_text,
# 			'type': 'odd',
# 			'publish': True,
# 			'subnotes': [{'items': index_list,
# 						'jsonmodel_type': 'note_orderedlist',
# 						'publish': True}]}

    #@atl.as_tools_logger(logger)
    def create_multipart_note(self, record_json, csv_row):
        '''Creates a multipart note and links it to a descriptive record.

           Parameters:
            record_json: The JSON representation of the parent record.
            csv_row['record_uri']: The URI of the parent record.
            csv_row['note_string']: The note text.
            csv_row['note_type']: The note type, i.e. accessrestrict

           Returns:
            dict: The JSON structure.
        '''
        new_note = {'jsonmodel_type': 'note_multipart',
                    'publish': True,
                    'subnotes': [{'content': csv_row['note_string'],
                              'jsonmodel_type': 'note_text',
                              'publish': True}],
                'type': csv_row['note_type']}
        record_json['notes'].append(new_note)
        return record_json

    def create_glad_scope_note(self, record_json, csv_row):
        '''Creates a multipart scope and content note and links it to a descriptive record.

           Parameters:
            record_json: The JSON representation of the parent record.
            csv_row['record_uri']: The URI of the parent record.
            csv_row['note']: The note text.

           Returns:
            dict: The JSON structure.
        '''
        if csv_row['note'] != '':
            new_note = f"Includes the following resource files:\n {csv_row['note']}"
            scope_note = {'jsonmodel_type': 'note_multipart',
                        'publish': True,
                        'subnotes': [{'content': new_note,
                                  'jsonmodel_type': 'note_text',
                                  'publish': True}],
                    'type': 'scopecontent'}
            record_json['notes'].append(scope_note)
            return record_json

    # def update_glad_wp_access_notes(self, record_json, csv_row):
    #     '''Updates a multipart access note, removing the free text.
    #
    #        Parameters:
    #         record_json: The JSON representation of the parent record.
    #         csv_row['uri']: The URI of the parent record.
    #         csv_row['persistent_id']: The persistent ID of the existing note
    #
    #        Returns:
    #         dict: The JSON structure.
    #     '''
    #     for note in record_json['notes']:
    #         if note['persistent_id'] == csv_row['persistent_id']:
    #             note['subnotes'][0]['content'] = ""


    def update_glad_scope_note(self, record_json, csv_row):
        '''Updates a multipart scope and content note, changing the subnote type
           from note_text to note_definedlist. Replaces an entire set of existing
           subnotes.

           Parameters:
            record_json: The JSON representation of the parent record.
            csv_row['uri']: The URI of the parent record.
            csv_row['persistent_id']: The persistent ID of the existing note
            csv_row['items']: A string representation of the list of items

           Returns:
            dict: The JSON structure.
        '''
        #could try to make a list out of the existing notes...this will be harder
        #for the CRP resource files
        from ast import literal_eval
        itemlist = literal_eval(csv_row['items'])
        for note in record_json['notes']:
            if note['persistent_id'] == csv_row['persistent_id']:
                new_subnote = [{'items': itemlist,
                          'title': 'Includes the following resource files:',
                          'jsonmodel_type': 'note_definedlist',
                          'publish': True}]
                note['subnotes'] = new_subnote
        return record_json

    #@atl.as_tools_logger(logger)
    def create_container_profiles(self, csv_row):
        '''Creates a container profile record.

           Parameters:
            csv_row['name']: The name of the container profile.
            csv_row['extent_dimension']: The extent dimension of the container profile, i.e. width.
            csv_row['height']: The height of the container profile.
            csv_row['width']: The width of the container profile.
            csv_row['depth']: The depth of the container profile.
            csv_row['dimension_units']: The dimension units of the container profile.

           Returns:
            tuple: The JSON structure and the API endpoint.
        '''
        new_container_profile = {'jsonmodel_type': 'container_profile', 'name': csv_row['name'],
                                 'extent_dimension': csv_row['extent_dimension'], 'height': csv_row['height'],
                                 'width': csv_row['width'], 'depth': csv_row['depth'], 'dimension_units': csv_row['dimension_units']}
        return (new_container_profile, '/container_profiles')

    #@atl.as_tools_logger(logger)
    def create_hm_external_ids(self, record_json, csv_row):
        '''Creates an external ID subrecord and links it to a descriptive record.

           Parameters:
            record_json: The JSON representation of the parent record.
            csv_row['uri']: The URI of the parent record.
            csv_row['hm_number']: The external ID value.

           Returns:
            dict: The JSON structure.
        '''
        new_external_id = {'jsonmodel_type': 'external_id',
                            'external_id': csv_row['hm_number'],
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
        #record_json = add_access_notes(record_json, csv_row)
        return record_json

    def update_file_version_format(self, record_json, csv_row):
        '''Updates a file version record with a file format type.

           Parameters:
            record_json: The JSON representation of the digital object record.
            csv_row['uri']L The URI of the digital object record.
            csv_row['file_uri']: The url of the file version subrecord.
            csv_row['file_format_name']: The file format name (database value)

           Returns:
            dict: The JSON structure.
        '''
        for file_version in record_json['file_versions']:
            if file_version.get('file_uri') == csv_row['file_uri']:
                file_version['file_format_name'] = csv_row['file_format_name']
        return record_json

    def create_digital_content_file_version(self, record_json, csv_row):
        '''Creates a single file version record and adds it to a digital object record.

           Parameters:
            record_json: The JSON representation of the digital object record.
            csv_row['uri']: The URI of the digital object record.
            csv_row['file_version_url']: The URL of the file version subrecord.
            csv_row['xlink_show_attribute']: The xlink show attribute of the file version, i.e. embed

           Returns:
            dict: The JSON structure.
        '''
        new_file_version = {'jsonmodel_type': 'file_version', 'file_uri': csv_row['file_version_url'],
                            'file_format_name': csv_row['file_format_name'],
                            'publish': False, 'xlink_show_attribute': 'new', 'xlink_actuate_attribute': 'onRequest'}
        if csv_row['file_size_bytes'] != "":
            new_file_version['file_size_bytes'] = int(csv_row['file_size_bytes'])
        record_json['file_versions'].append(new_file_version)
        return record_json

    #@atl.as_tools_logger(logger)
    def create_file_version(self, record_json, csv_row):
        '''Creates a single file version record and adds it to a digital object record.

           Parameters:
            record_json: The JSON representation of the digital object record.
            csv_row['uri']: The URI of the digital object record.
            csv_row['file_version_url']: The URL of the file version subrecord.
            csv_row['xlink_show_attribute']: The xlink show attribute of the file version, i.e. embed

           Returns:
            dict: The JSON structure.
        '''
        new_file_version = {'jsonmodel_type': 'file_version', 'file_uri': csv_row['file_version_url'],
                            'publish': True, 'xlink_show_attribute': csv_row['xlink_show_attribute']}
        record_json['file_versions'].append(new_file_version)
        return record_json

    #@atl.as_tools_logger(logger)
    def create_file_versions(self, record_json, csv_row):
        '''Creates multiple file versions and adds them to a digital object record.

           Parameters:
            record_json: The JSON representation of the digital object record.
            csv_row['uri']: The URI of the digital object record.
            csv_row['file_version_url_01']: The URL of the first file version subrecord.
            csv_row['file_version_url_02']: The URL of the second file version subrecord.
            csv_row['digital_object_id']: The digital object identifier.

           Returns:
            dict: The JSON structure.

           Todo:
            This is basically an abstraction of the dig lib function - can I get rid of that one?
        '''
        record_json['publish'] = True
        record_json['digital_object_id'] = csv_row['digital_object_id']
        #digital library link
        file_version_01 = {'file_uri': csv_row['file_version_url_01'], 'jsonmodel_type': 'file_version',
                                       'xlink_show_attribute': 'new', 'publish': True}
        #thumbnail link
        file_version_02 = {'file_uri': csv_row['file_version_url_02'], 'jsonmodel_type': 'file_version',
                                      'xlink_show_attribute': 'embed', 'publish': True}
        record_json['file_versions'].extend([file_version_01, file_version_02])
        return record_json

    def create_timebound_access_restriction(self, record_json, csv_row):
        '''Creates an accessrestrict note with a timebound restriction.

           Parameters:
            record_json: The JSON representation of the descriptive record.
            csv_row['uri']: The URI of the descriptive record.
            csv_row['note']: The free-text access note.
            csv_row['end_date']: The date the restriction expires.

           Returns:
            dict: The JSON structure.
        '''
        new_note = {'jsonmodel_type': 'note_multipart',
                    'publish': True,
                    'subnotes': [{'content': csv_row['note'],
                              'jsonmodel_type': 'note_text',
                              'publish': True}],
                    'type': 'accessrestrict',
                    'rights_restriction': {"jsonmodel_type":"rights_restriction",
                                            'end': csv_row['end_date']}}
        record_json['notes'].append(new_note)
        return record_json

    def update_notes_titles(self, record_json, csv_row):
        '''Updates a subnote record and a title

           Parameters:
            record_json: The JSON representation of the descriptive record.
            csv_row['uri']: The URI of the descriptive record.
            csv_row['persistent_id']: The persistent ID of the note to update.
            csv_row['title']: The new title of the descriptive record
            csv_row['subnotes']: The new subnote

           Returns:
            dict: The JSON structure.
        '''
        record_json['title'] = csv_row['title']
        for note in record_json['notes']:
            import ast
            if note['persistent_id'] == csv_row['persistent_id']:
                subnotes = ast.literal_eval(csv_row['subnotes'])
                note['subnotes'] = subnotes
        return record_json

    #change this - just applies to UseSurrogate right now
    #@atl.as_tools_logger(logger)
    def create_use_surrogate_access_notes(self, record_json, csv_row):
        '''Creates an accessrestrict note for HM microfilm surrogates and
           links it to a descriptive record.

           Parameters:
            record_json: The JSON representation of the descriptive record.
            csv_row['uri']: The URI of the descriptive record.
            csv_row['external_id']: The external ID of the descriptive record.

           Returns:
            dict: The JSON structure.
        '''
        note_text = f"This material has been microfilmed. Patrons must use {csv_row['external_id']} instead of the originals."
        new_note = {'jsonmodel_type': 'note_multipart',
                    'publish': True,
                    'subnotes': [{'content': note_text,
                              'jsonmodel_type': 'note_text',
                              'publish': True}],
                    'type': 'accessrestrict',
                    'rights_restriction': {'local_access_restriction_type': ['UseSurrogate']}}
        record_json['notes'].append(new_note)
        return record_json

    #@atl.as_tools_logger(logger)
    def create_local_access_restriction(self, record_json, csv_row):
        '''Creates a local access restriction type and links it to an existing note in a
           descriptive record.

           Parameters:
            record_json: The JSON representation of the descriptive record.
            csv_row['uri']: The URI of the descriptive record.
            csv_row['persistent_id']: The persistent ID of the parent note.
            csv_row['local_type']: The local access restriction type.

           Returns:
            dict: The JSON structure.
        '''
        for note in record_json['notes']:
            if note['persistent_id'] == csv_row['persistent_id']:
                if 'rights_restriction' in note:
                    note['rights_restriction']['local_access_restriction_type'].append(csv_row['local_type'])
                else:
                    note['rights_restriction'] = {'local_access_restriction_type': [csv_row['local_type']]}
        return record_json

    #@atl.as_tools_logger(logger)
    def create_timebound_restriction(self, record_json, csv_row):
        '''Creates a timebound restriction type and links it to a note in a descriptive
           record.

           Parameters:
            record_json: The JSON representation of the descriptive record.
            csv_row['uri']: The URI of the descriptive record.
            csv_row['persistent_id']: The persistent ID of the parent note.
            csv_row['begin']: The begin date of the restriction. Format YYYY-MM-DD required.
            csv_row['end']: The end date of the restriction. Format YYYY-MM-DD required.

           Returns:
            dict: The JSON structure.
        '''
        for note in record_json['notes']:
            if note['persistent_id'] == csv_row['persistent_id']:
                #this might not work for some of the older records which
                #don't have the rights restriction dictionary
                note['rights_restriction']['begin'] = csv_row['begin']
                note['rights_restriction']['end'] = csv_row['end']
        return record_json

    #@atl.as_tools_logger(logger)
    def update_identifiers(self, record_json, csv_row):
        '''Moves resource identifiers which are split across multiple fields into a
           single field.

           Parameters:
            record_json: The JSON representation of the parent record.
            csv_row['uri']: The URI of the parent record.
            csv_row['identifier']: The new identifier.

           Returns:
            dict: The JSON structure.
        '''
        record_json['id_0'] = csv_row['identifier']
        if 'id_1' in record_json:
            del record_json['id_1']
        if 'id_2' in record_json:
            del record_json['id_2']
        if 'id_3' in record_json:
            del record_json['id_3']
        return record_json

    #@atl.as_tools_logger(logger)
    def update_container_type(self, record_json, csv_row):
        '''Updates the container type of a top container record.

           Parameters:
            record_json: The JSON representation of the top container record.
            csv_row['uri']: The URI of the top container record.
            csv_row['container_type']: The new container type.

           Returns:
            dict: The JSON structure.
        '''
        record_json['type'] = container_type
        return record_json

    #@atl.as_tools_logger(logger)
    def link_agent_to_record(self, record_json, csv_row):
        '''Links an agent record to a descriptive record.

           Parameters:
            record_json: The JSON representation of the descriptive record.
            csv_row['agent_uri']: The URI of the agent record.
            csv_row['record_uri']: The URI of the descriptive record.

           Returns:
            dict: The JSON structure.
        '''
        record_json['linked_agents'].append({'ref': csv_row['agent_uri']})
        return record_json

    #@atl.as_tools_logger(logger)
    def link_event_to_record(self, record_json, csv_row):
        '''Links an event record to a descriptive record.

           Parameters:
            record_json: The JSON representation of the descriptive record.
            csv_row['record_uri']: The URI of the descriptive record.
            csv_row['event_uri']: The URI of the event record.

           Returns:
            dict: The JSON structure.
        '''
        record_json['linked_events'].append({'ref': csv_row['event_uri']})
        return record_json

    #@atl.as_tools_logger(logger)
    def link_record_to_classification(self, record_json, csv_row):
        '''Links a record to a classification or classification term.

           Parameters:
            record_json: The JSON representation of the descriptive record.
            csv_row['classification_uri']: The URI of the classification term
            csv_row['record_uri']: The URI of the record to link.

           Returns:
            dict: The JSON structure.

           Todo:
            check if possible to link records to other types of
            records such as agents
        '''
        record_json['linked_records'].append({'ref': csv_row['record_uri']})
        return record_json

    def update_eng_finding_aid_language(self, record_json, csv_row):
        '''Updates a finding aid language value to English (before v 2.8)

           Parameters:
            record_json: The JSON representation of the descriptive record.
            csv_row['uri']: The URI of the descriptive record.
            csv_row['finding_aid_language']: The new finding aid language value

           Returns:
            duct: The JSON structure.

        '''
        record_json['finding_aid_language'] = "Finding aid written in <language langcode=\"eng\" scriptcode=\"Latn\">English</language>."
        return record_json

    def update_indicators(self, record_json, csv_row):
        '''Updates a top container record with a new indicator.

           Parameters:
            record_json: The JSON representation of the top container record.
            csv_row['uri']: The URI of the top container record.
            csv_row['indicator']: The barcode of the top container.

           Returns:
            dict: The JSON structure.
        '''
        record_json['indicator'] = csv_row['indicator']
        return record_json

    def update_barcodes(self, record_json, csv_row):
        '''Updates a top container record with barcode.

           Parameters:
            record_json: The JSON representation of the top container record.
            csv_row['uri']: The URI of the top container record.
            csv_row['barcode']: The barcode of the top container.

           Returns:
            dict: The JSON structure.
        '''
        record_json['barcode'] = csv_row['barcode']
        return record_json

    def update_barcodes_indicators(self, record_json, csv_row):
        '''Updates a top container record with barcode and indicator.

           Parameters:
            record_json: The JSON representation of the top container record.
            csv_row['uri']: The URI of the top container record.
            csv_row['barcode']: The barcode of the top container.
            csv_row['indicator']: The indicator (box number) of the top container.

           Returns:
            dict: The JSON structure.
        '''
        record_json['barcode'] = csv_row['barcode']
        record_json['indicator'] = csv_row['indicator']
        return record_json

    #abstract
    #@atl.as_tools_logger(logger)
    def update_top_containers(self, record_json, csv_row):
        '''Updates a top container record with barcode and adds a type value of 'Box'
           to the record. Also adds LSF as the location.

           Parameters:
            record_json: The JSON representation of the top container record.
            csv_row['tc_uri']: The URI of the top container record.
            csv_row['barcode']: The barcode of the top container.

           Returns:
            dict: The JSON structure.
        '''
        record_json['barcode'] = csv_row['barcode']
        record_json['type'] = 'Box'
        new_location = {'jsonmodel_type': 'container_location', 'ref': '/locations/9', 'status': 'current', 'start_date': '2017-03-01'}
        record_json['container_locations'].append(new_location)
        return record_json

    def update_container_location(self, record_json, csv_row):
        '''Updates a top container record with a location

           Parameters:
            record_json: The JSON representation of the top container record.
            csv_row['uri']: The URI of the top container record.
            csv_row['location_uri']: The barcode of the top container.

           Returns:
            dict: The JSON structure.
        '''
        new_location = {'jsonmodel_type': 'container_location', 'ref': csv_row['location_uri'], 'status': 'current', 'start_date': '2017-03-01'}
        record_json['container_locations'].append(new_location)
        return record_json

    def update_title(self, record_json, csv_row):
        '''Updates a record title.

           Parameters:
            record_json: The JSON representation of the top container record.
            csv_row['uri']: The URI of the top container record.
            csv_row['title']: The new title.

           Returns:
            dict: The JSON structure.
        '''
        record_json['title'] = csv_row['title']
        return record_json

    def update_container_type(self, record_json, csv_row):
        '''Updates a container record with a type value of 'Box'.

           Parameters:
            record_json: The JSON representation of the top container record.
            csv_row['uri']: The URI of the top container record.

           Returns:
            dict: The JSON structure.
        '''
        record_json['type'] = 'Box'
        return record_json

    #@atl.as_tools_logger(logger)
    def update_dates(self, record_json, csv_row):
        '''Updates date subrecords.

           Parameters:
            record_json: The JSON representation of the parent record.

           Returns:
            dict: The JSON structure.
        '''
        for date in record_json['dates']:
            date['begin'] = csv_row['begin']
        return record_json

    #@atl.as_tools_logger(logger)
    def update_date_type(self, record_json, csv_row):
        '''Checks whether a date lacks end value, or whether the begin and end values
          and if either are true changes the date type to 'single'

          Parameters:
           record_json: The JSON representation of the descriptive record.
           csv_row['uri']: The URI of the descriptive record.

           Returns:
            dict: The JSON structure.
        '''
        for date in record_json['dates']:
            if 'end' not in date:
                date['date_type'] = 'single'
            elif date['end'] == date['begin']:
                date['date_type'] = 'single'
        return record_json


    def update_box_numbers(self, record_json, csv_row):
        '''Updates indicator numbers in top container records.

           Parameters:
            record_json: The JSON representation of the top container record.
            csv_row['uri']: The URI of the top container record.
            csv_row['old_box']: The old box number.
            csv_row['new_box']: The new box number.

           Returns:
            dict: The JSON structure.
        '''
        if record_json['indicator'] == csv_row['old_box']:
            record_json['indicator'] = csv_row['new_box']
        return record_json


    #@atl.as_tools_logger(logger)
    def update_folder_numbers(self, record_json, csv_row):
        '''Updates indicator numbers in instance subrecords.

           Parameters:
            record_json: The JSON representation of the descriptive record.
            csv_row['uri']: The URI of the descriptive record.
            csv_row['old_folder']: The old folder number.
            csv_row['new_folder']: The new folder number.

           Returns:
            dict: The JSON structure.
        '''
        for instance in record_json['instances']:
            if instance['indicator_2'] == csv_row['old_folder']:
                instance['indicator_2'] = csv_row['new_folder']
        return record_json

    #@atl.as_tools_logger(logger)
    def update_revision_statements(self, record_json, csv_row):
        '''Updates a revision statement.

           Parameters:
            record_json: The JSON representation of the resource record.
            csv_row['uri']: The URI of the resource record.
            csv_row['revision_date']: The revision date of the resource record.
            csv_row['old_text']: The old revision statement.
            csv_row['new_text']: The new revision statement.

           Returns:
            dict: The JSON structure.
        '''
        for revision_statement in record_json['revision_statements']:
            if revision_statement['description'] == csv_row['old_text']:
                revision_statement['description'] = csv_row['new_text']
        return record_json

    #@atl.as_tools_logger(logger)
    def update_notes(self, record_json, csv_row):
        '''Updates singlepart or multipart notes.

           Parameters:
            record_json: The JSON representation of the parent record.
            csv_row['uri']: The URI of the parent record.
            csv_row['persistent_id']: The persistent ID of the parent note.
            csv_row['note_text']: The new note text.

           Returns:
            dict: The JSON structure.
        '''
        for note in record_json['notes']:
            if note['jsonmodel_type'] == 'note_multipart':
                if note['persistent_id'] == csv_row['persistent_id']:
                    note['subnotes'][0]['content'] = csv_row['note_text']
            elif note['jsonmodel_type'] == 'note_singlepart':
                if note['persistent_id'] == csv_row['persistent_id']:
                    note['content'] = [csv_row['note_text']]
        return record_json

    #@atl.as_tools_logger(logger)
    def update_access_notes(self, record_json, csv_row):
        '''Updates existing accessrestrict notes for HM films.

           Parameters:
            record_json: The JSON representation of the parent record.
            csv_row['uri']: The URI of the parent record.
            csv_row['persistent_id']: The persistent ID of the parent note.
            csv_row['external_id']: The external ID of the parent record.

           Returns:
            dict: The JSON structure.
        '''
        note_text = f"This material has been microfilmed. Patrons must use {external_id} instead of the originals"
        for note in record_json['notes']:
            if note.get('persistent_id') == csv_row['persistent_id']:
                note['subnotes'][0]['content'] = csv_row['note_text']
                note['rights_restriction'] = {'local_access_restriction_type': ['UseSurrogate']}
        return record_json


    def update_external_document_location(self, record_json, csv_row):
        '''Updates the file location of an external document subrecord.

           Parameters:
            record_json: The JSON representation of the top-level record.
            csv_row['uri']: The URI of the top-level record.
            csv_row['old_link']: The "old" file location of the external document
            csv_row['new_link']: The file location of the updated external document

           Returns:
            dict: The JSON structure.
        '''
        for external_document in record_json['external_documents']:
            if external_document.get('location') == csv_row['old_link']:
                external_document['location'] = csv_row['new_link']
        return record_json

    #@atl.as_tools_logger(logger)
    def update_date_expressions(self, record_json, csv_row):
        '''Adds a date expression to a date record.

           Parameters:
            record_json: The JSON representation of the top-level record.
            csv_row['uri']: The URI of the top-level record.
            csv_row['expression']: The date expression to be added.
            csv_row['begin']: The structured begin date to match the against the date JSON.
            csv_row['end']: The structured end date to match against the date JSON.

           Returns:
            dict: The JSON structure.
        '''
        if record_json['jsonmodel_type'].startswith('agent'):
            key = 'dates_of_existence'
        else:
            key = 'dates'
        for date in record_json[key]:
            if csv_row['end'] != '':
                if (date['begin'] == csv_row['begin']) and (date['end'] == csv_row['end']):
                    date['expression'] = csv_row['expression']
            elif csv_row['end'] == '':
                if date['begin'] == csv_row['begin']:
                    date['expression'] = csv_row['expression']
        return record_json

    #@atl.as_tools_logger(logger)
    def update_locations(self, record_json, csv_row):
        '''Updates location records with barcodes, location profiles, repositories,
           and, optionally, coordinate 1 indicator.

           Parameters:
            record_json: The JSON representation of the location record.
            csv_row['uri']: The URI of the location record.
            csv_row['barcode']: The barcode of the location record.
            csv_row['location_profile']: The URI of the location profile.
            csv_row['owner_repo']: The URI of the parent repository.

           Other Parameters:
            coordinate_2_indicator: The indicator of location coordinate_2.

           Returns:
            dict: The JSON structure.
        '''
        record_json['barcode'] = csv_row['barcode']
        record_json['location_profile'] = {'ref': csv_row['location_profile']}
        record_json['owner_repo'] = {'ref': csv_row['owner_repo']}
        if csv_row['coordinate_2_indicator'] != '':
            record_json['coordinate_2_indicator'] = csv_row['coordinate_2_indicator']
        return record_json

    #@atl.as_tools_logger(logger)
    def update_location_coordinates(self, record_json, csv_row):
        '''Updates location labels and indicators.

           Parameters:
            record_json: The JSON representation of the location record.
            csv_row['csv_row['uri']: The URI of the location record.
            csv_row['coordinate_1_label']: The label of location coordinate_1.
            csv_row['coordinate_1_indicator']: The indicator of location coordinate_1.
            csv_row['coordinate_2_label']: The label of location coordinate_2.
            csv_row['coordinate_2_indicator']: The indicator of location coordinate_2.
            csv_row['coordinate_3_label']: The label of location coordinate_3.
            csv_row['coordinate_3_indicator']: The indicator of location coordinate_3.

           Returns:
            dict: The JSON structure.
        '''
        record_json['coordinate_1_indicator'] = csv_row['coordinate_1_indicator']
        record_json['coordinate_1_label'] = csv_row['coordinate_1_label']
        record_json['coordinate_2_indicator'] = csv_row['coordinate_2_indicator']
        record_json['coordinate_2_label'] = csv_row['coordinate_2_label']
        record_json['coordinate_3_indicator'] = csv_row['coordinate_3_indicator']
        record_json['coordinate_3_label'] = csv_row['coordinate_3_label']
        return record_json

    #@atl.as_tools_logger(logger)
    def update_record_component(self, record_json, csv_row):
        '''Updates a non-nested field in a top-level record.

           Parameters:
            record_json: The JSON representation of the record.
            csv_row['record_uri']: The URI of the record.
            csv_row['updated_text']: The new value.
            component: The component to update.

           Returns:
            dict: The JSON structure.

           Todo:
            Changed the valued to title for testing purposes; need to add a
            component type argument
        '''
        record_json['title'] = csv_row['updated_text']
        return record_json

    #@atl.as_tools_logger(logger)
    def update_record_components(self, record_json, csv_row):
        '''Updates non-nested fields in a top-level record.

           Parameters:
            record_json: The JSON representation of the record.
            csv_row['uri']: The URI of the record.
            fields: The fields, indicated by column headers.
            values: The values, indicated by column values.

           Returns:
            dict: The JSON structure.

           Note:
            Fields must match JSON keys in ArchivesSpace JSON response.
        '''
        for field, value in csv_row.items():
            if field != 'uri':
                record_json[field] = value
        return record_json

    #also need to define the subrecord here.
    #@atl.as_tools_logger(logger)
    def update_subrecord_component(self, record_json, csv_row):
        '''Updates a nested field in a top-level record.

           Parameters:
            record_json: The JSON representation of the record.
            csv_row['uri']: The URI of the record.
            csv_row['updated_text']: The updated value.
            subrecord: The subrecord type.
            component: The subrecord component type.

           Returns:
            dict: The JSON structure.

           Todo:
            is this even necessary? If so add subrecord stuff to args
        '''
        for item in record_json[subrecord]:
                item[component] = csv_row['updated_text']
        return record_json

    #also need to define the subrecord here...
    #@atl.as_tools_logger(logger)
    def update_subrecord_components(self, record_json, csv_row):
        '''Updates nested fields in a top-level record.

           Parameters:
            record_json: The JSON representation of the record.
            csv_row['uri']: The URI of the record.
            fields: The fields, indicated by column headers.
            values: The values, indicated by column values.

           Returns:
            dict: The JSON structure.

           Note:
            Fields must match JSON keys in ArchivesSpace JSON response.

           Todo:
            See if this works? Might need to specify component type.
        '''
        for field, value in csv_row.items():
            if field != 'uri':
                for item in record_json[subrecord]:
                    item[field] = value
        return record_json

    #@atl.as_tools_logger(logger)
    def update_record_pub_status(self, record_json, csv_row):
        '''Updates publication status of top-level record.

           Parameters:
            record_json: The JSON representation of the record.
            csv_row['uri']: The URI of the record.
            csv_row['updated_status']: The updated publication status, '1' for publish, '0' for unpublish.

           Returns:
            dict: The JSON structure.
        '''
        if csv_row['updated_status'] == '1':
            record_json['publish'] = True
        elif csv_row['updated_status'] == '0':
            record_json['publish'] = False
        return record_json

    #@atl.as_tools_logger(logger)
    def update_subrecord_pub_status(self, record_json, csv_row):
        '''Updates publication status of subrecord.

           Parameters:
            record_json: The JSON representation of the parent record.
            csv_row['uri']: The URI of the parent record.
            csv_row['updated_status']: The updated publication status, '1' for publish, '0' for unpublish.
            subrecord: The subrecord type.

            Todo:
             Need to add an arg here?
        '''
        pass

    #if the subnote is also unpublished will need to fix that as well
    #@atl.as_tools_logger(logger)
    def update_note_pub_status(self, record_json, csv_row):
        '''Updates publication status of a note.

           Parameters:
            record_json: The JSOn representation of the parent record.
            csv_row['uri']: The URI of the parent record.
            csv_row['persistent_id']: The persistent ID of the note.
            csv_row['updated_status']: The updated status. '1' is publish, '0' is unpublish

           Returns:
            dict: The JSON structure.

           Todo:
            also need to change pub status of sub-notes...
        '''
        for note in record_json['notes']:
            if note['persistent_id'] == csv_row['persistent_id']:
                if csv_row['updated_status'] == '1':
                    note['publish'] = True
                elif csv_row['updated_status'] == '0':
                    note['publish'] = False
        return record_json

    def update_authority_id(self, record_json, csv_row):
        '''Updates a name record with a new authority ID

           Parameters:
            record_json: The JSON representation of the agent record.
            csv_row['uri']: The URI of the agent_record
            csv_row['authority_id']: The authority ID to add to the agent record.

           Returns:
            dict: The JSON structure.
        '''
        for name in record_json['names']:
            if name.get('is_display_name') == True:
                name['authority_id'] = csv_row['authority_id']
        return record_json

    #@atl.as_tools_logger(logger)
    def update_names(self, record_json, csv_row):
        '''Updates name records to fix improper field usages.

           Parameters:
            record_json: The JSON representation of the agent record.
            csv_row['uri']: The URI of the agent record.
            csv_row['sort_name']: The sort name of the agent record.
            csv_row['primary_name']: The primary name of the agent record display name.
            csv_row['rest_of_name']: The rest of name of the agent record display name.
            csv_row['dates']: The dates of the agent record display name.
            csv_row['prefix']: The prefix of the agent record display name.
            csv_row['suffix']: The suffix of the agent record display name.
            csv_row['title']: The title of the agent record display name.
            csv_row['qualifier']: The qualifier of the agent record display name.
            csv_row['name_order']: The name order of the agent record display name.

           Returns:
            dict: The JSON structure.
        '''
        for name in record_json['names']:
            if 'is_display_name' in name:
                if name['is_display_name']:
                    if name['sort_name'] == csv_row['sort_name']:
                        name['primary_name'] = csv_row['primary_name']
                        name['rest_of_name'] = csv_row['rest_of_name']
                        name['dates'] = csv_row['dates']
                        name['prefix'] = csv_row['prefix']
                        name['suffix'] = csv_row['suffix']
                        name['title'] = csv_row['title']
                        name['qualifier'] = csv_row['qualifier']
                        name['name_order'] = csv_row['name_order']
        return record_json

    #@atl.as_tools_logger(logger)
    def update_sources_auth_ids(self, record_json, csv_row):
        '''Updates an agent record with a source value of 'local' and removes vendor-added
           authority ID codes. Used for agents and subjects remediation project.

           Parameters:
            record_json: The JSON representation of the record.
            csv_row['uri']: The URI of the agent record.

           Returns:
            dict: The JSON structure.
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
        return record_json

    #so, for some reason I was able to do this - but deleting the whole instance will not work
    #@atl.as_tools_logger(logger)
    def delete_subcontainers(self, record_json, csv_row):
        '''Deletes a sub_container subrecord in an instance subrecord.

           Parameters:
            record_json: The JSON representation of the parent record.
            csv_row['uri']: The URI of the parent record.

           Returns:
            dict: The JSON structure.
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

    #@atl.as_tools_logger(logger)
    def delete_notes(self, record_json, csv_row):
        '''Deletes a note subrecord in a descriptive record.

           Parameters:
            record_json: The JSON representation of the parent record.
            csv_row['uri']: The URI of the parent record.
            csv_row['persistent_id']: The persistent ID of the note to delete.

           Returns:
            dict: The JSON structure.
        '''
        for note in record_json['notes']:
            if note.get('persistent_id') == csv_row['persistent_id']:
                note.clear()
        return record_json

    def delete_external_document(self, record_json, csv_row):
        '''Deletes an external document subrecord.

           Parameters:
            record_json: The JSON representation of the parent record.
            csv_row['uri']: The URI of the parent record.
            csv_row['link_to_delete']: The file location of the external document to delete

           Returns:
            dict: The JSON structure.
        '''
        for external_document in record_json['external_documents']:
            if external_document.get('location') == csv_row['link_to_delete']:
                external_document.clear()
        return record_json

    #@atl.as_tools_logger(logger)
    def delete_rights_restriction(self, record_json, csv_row):
        '''Deletes a local access restriction in an accessrestrict note.

           Parameters:
            record_json: The JSON representation of the parent record.
            csv_row['uri']: The URI of the parent record.
            csv_row['persistent_id']: The persistent ID of the parent accessrestrict note.

           Returns:
            dict: The JSON structure.
        '''
        for note in record_json['notes']:
            if note['persistent_id'] == csv_row['persistent_id']:
                if 'rights_restriction' in note:
                    del note['rights_restriction']
        return record_json

    #@atl.as_tools_logger(logger)
    def delete_instances(self, record_json, csv_row):
        '''Deletes an instance.

           Parameters:
            record_json: The JSON representation of the parent record.
            csv_row['uri']: The URI of the parent record.

           Returns:
            dict: The JSON structure.

           Todo:
            check if this can be extracted to all subrecords. Make sure to use the .clear() method
        '''

    def delete_enumeration_value(self):
        '''Suppresses an enumeration value.

           Parameters:
            csv_row['uri']: The URI of the enumeration value

           Returns:
            dict: The JSON structure.
        '''

    # def add_access_notes(record_json, csv_row):
    #     exists = 0
    #     if len(record_json['notes']) > 0:
    #         for note in record_json['notes']:
    #             if note['type'] == 'accessrestrict':
    #                 if 'This material has been microfilmed' in note['subnotes'][0]['content']:
    #                     print('Note exists!')
    #                     exists = 1
    #     if exists == 0:
    #         record_json = new_use_surrogate_notes.create_access_note(record_json, csv_row)
    #     return record_json

    #@atl.as_tools_logger(logger)
    def get_series(self, record_json, csv_row):
        '''Gets a list of series-level ancestors for a list of URIs.

           Parameters:
            record_json: the JSON representation of the record.
            csv_row['uri']: The URI of the record to search
        '''
        for ancestor in record_json['ancestors']:
            if ancestor['level'] == 'series':
                csv_row.append(ancestor['ref'])
        return (csv_row, record_json)

    #@atl.as_tools_logger(logger)
    def get_agents(self, agent_json, csv_row):
        '''Retrieves data about agents.

           Parameters:
            agent_json: The JSON representation of the agent rexcord.
            csv_row['uri']: The URI of the agent to search.
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

    #@atl.as_tools_logger(logger)
    def get_subjects(self, subject_json, csv_row):
        '''Retrieves data about subjects.

           Parameters:
            subject_json: The JSON representation of the subject record.
            csv_row['uri']: The URI of the subject to search.
        '''
        terms = []
        if 'title' in subject_json:
            csv_row.append(subject_json['title'])
        else:
            csv_row.append('NO_VALUE')
        if 'authority_id' in subject_json:
            csv_row.append(subject_json['authority_id'])
        else:
            csv_row.append('NO_VALUE')
        if 'source' in subject_json:
            csv_row.append(subject_json['source'])
        else:
            csv_row.append('NO_VALUE')
        if 'is_linked_to_published_record' in subject_json:
            csv_row.append(subject_json['is_linked_to_published_record'])
        else:
            csv_row.append('NO_VALUE')
        if 'terms' in subject_json:
            for term in subject_json['terms']:
                terms.append([term['term'], term['term_type']])
            csv_row.append(terms)
        else:
            csv_row.append('NO_VALUE')
        if 'used_within_repositories' in subject_json:
            csv_row.append(subject_json['used_within_repositories'])
        else:
            csv_row.append('NO_VALUE')
        if 'created_by' in subject_json:
            csv_row.append(subject_json['created_by'])
        else:
            csv_row.append('NO_VALUE')
        return csv_row
