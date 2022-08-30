#!/usr/bin/python3
#~/anaconda3/bin/python

'''
JSON template functions for creating or updating ArchivesSpace records.
'''

import csv
from functools import wraps
import json
import pprint
import traceback

import requests

from aspace_run import ASpaceConnection, ASpaceCrud, _api_caller


class ASpaceRequests():

    def __init__(self, aspace_conn):
        self.cfg = aspace_conn

    @_api_caller(ASpaceCrud.reader)
    def search_all(csv_row: dict) -> str:
        '''Search all published records across repositories.

           Parameters:
            csv_row['search_string']: The search to perform.

           Usage
            ::

              >>> csv_row = {'search_string': 'MS 150'}
              >>> uri = search_all(csv_row)
              >>> print(uri)
              '/search?q=MS 150'
        '''
        return f"/search?q={csv_row.get('search_string')}"

    @_api_caller(ASpaceCrud.reader)
    def search_linked_top_containers(csv_row: dict) -> str:
        '''Search containers linked to a published resource and its children.

           Parameters:
            row['uri']: The URI of the record to retrieve

           Usage
            ::

              >>> csv_row = {'uri': '/repositories/2/resources/5'}
              >>> uri = search_linked_top_containers(csv_row)
              >>> print(uri)
              '/repositories/2/resources/5/top_containers'
        '''
        print(f"{csv_row.get('uri')}/top_containers")
        return f"{csv_row.get('uri')}/top_containers"

    @_api_caller(ASpaceCrud.reader)
    def search_container_profiles(csv_row: dict) -> str:
        '''Search container profiles by name.

           Parameters:
            csv_row['container_profile']: The name of the container profile to search.

           Usage
            ::

              >>> csv_row = {'container_profile': 'archive_letter'}
              >>> uri = search_container_profiles(csv_row)
              >>> print(uri)
              '/search?page=1&page_size=500&type[]=container_profile&q=title:archive letter}'
        '''
        return f"/search?page=1&page_size=500&type[]=container_profile&q=title:{csv_row.get('container_profile')}"

    @_api_caller(ASpaceCrud.reader)
    def get_nodes(csv_row: dict) -> str:
        '''Gets a list of child URIs for an archival object record

           Parameters:
            row['uri']: The URI of the parent resource
            row['node_uri']: The URI of the parent archival object

           Usage
            ::

              >>> csv_row = {'uri': '/repositories/2/resources/1', 'node_uri': '/repositories/2/archival_objects/5'}
              >>> uri = get(nodes(csv_row))
              >>> print(uri)
              '/repositories/2/resources/1/tree/node?node_uri=/repositories/2/archival_objects/5'
        '''
        return f"{csv_row.get('uri')}/tree/node?node_uri={csv_row.get('node_uri')}"

    @_api_caller(ASpaceCrud.reader)
    def get_tree(csv_row: dict) -> str:
        '''Gets a tree for a record.

           Parameters:
            row['uri']: The URI of the record.

           Usage
            ::

              >>> csv_row = {'uri': '/repositories/2/resources/1'}
              >>> uri = get_tree(csv_row)
              >>> print(uri)
              '/repositories/2/resources/1/tree'
        '''
        return f"{csv_row.get('uri')}/tree"

    @_api_caller(ASpaceCrud.reader)
    def get_node_from_root(csv_row: dict) -> str:
        '''Gets a tree path from the root record to archival objects.

           Parameters:
            row['uri']: The URI of the resource record.
            row['node_id']: The id of the archival object node

           Usage
            ::

              >>> csv_row = {'uri': '/repositories/2/resources/1', 'note_id' = '5'}
              >>> uri = get_node_from_root(csv_row)
              >>> print(uri)
              '/repositories/2/resources/1/tree/node_from_root?node_ids=5'
        '''
        return f"{csv_row.get('uri')}/tree/node_from_root?node_ids={int(csv_row.get('node_id'))}"

    @_api_caller(ASpaceCrud.reader)
    def get_extents(csv_row: dict) -> str:
        '''Calculates the total extent for a resource record and its children. Uses container profile measurements to make the calculation.

           Parameters:
            row['uri']: The URI of the resource to calculate.

           Usage
            ::

              >>> csv_row = {'uri': '/repositories/2/resources/1'}
              >>> uri = get_extents(csv_row)
              >>> print(uri)
              '/extent_calculator?record_uri=/repositories/2/resources/1'
        '''
        return f"/extent_calculator?record_uri={csv_row.get('uri')}"

    @_api_caller(ASpaceCrud.reader)
    def get_required_fields(csv_row: dict) -> str:
        '''Retrieves required fields for a record type.

           Parameters:
            row['uri']: The URI of the repository
            row['record_type']: The type of the record to retrieve

           Usage
            ::

              >>> csv_row = {'uri': '/repositories/2', 'record_type': 'archival_object'}
              >>> uri = get_required_fields(csv_row)
              >>> print(uri)
              '/repositories/2/required_fields/archival_object'
        '''
        return f"{csv_row.get('uri')}/required_fields/{csv_row.get('record_type')}"

    #double check this - not sure if I need to GET first - I didn't think so; also need to make sure that 'config' is part of the enum uri
    @_api_caller(ASpaceCrud.updater)
    def reposition_enumeration(csv_row: dict) -> str:
        '''Updates the position of an enumeration value.

           Parameters:
            csv_row['uri']: The URI of the enumeration value to update.
            csv_row['position']: The new position value.

           Usage
            ::

              >>> csv_row = {'uri': '/repositories/2/archival_objects/5' 'position': '14'}
              >>> uri = reposition_enumeration(csv_row)
              >>> print(uri)
              '/enumeration_value/5/position?position=14'
        '''
        return f"{csv_row.get('uri')}/position?position={csv_row.get('position')}"

    @_api_caller(ASpaceCrud.updater)
    def suppress_record(csv_row: dict) -> str:
        '''Suppresses a record.

           Parameters:
            csv_row['uri']: The URI of the record to suppress

           Usage
            ::

              >>> csv_row = {'uri': '/repositories/2/archival_objects/5'}
              >>> uri = suppress_record(csv_row)
              >>> print(uri)
              '/repositories/2/archival_objects/5/suppressed?suppressed=true'
        '''
        return f"{csv_row.get('uri')}/suppressed?suppressed=true"

    @_api_caller(ASpaceCrud.updater)
    def set_parent_reposition_archival_object(csv_row: dict) -> str:
        '''Updates the archival object parent and position of an archival object record.

           Parameters:
            csv_row['child_uri']: The URI of the record to update.
            csv_row['parent_uri']: The URI of the new parent.
            csv_row['position']: The new position value.

           Usage
            ::

              >>> csv_row = {'child_uri': '/repositories/2/archival_objects/5', 'parent_uri': '/repositories/2/archival_objects/6', 'position': '14'}
              >>> uri = set_parent_reposition_archival_object(csv_row)
              >>> print(uri)
              '/repositories/2/archival_objects/5/parent?parent=/repositories/2/archival_objects/6&position=15'
        '''
        return f"{csv_row.get('child_uri')}/parent?parent={csv_row.get('parent_uri')}&position={csv_row.get('position')}"

    @_api_caller(ASpaceCrud.updater)
    def merge_data(csv_row: dict) -> tuple[dict, str]:
        '''Merges two records.

           Parameters:
            csv_row['target_uri']: The URI of the record to keep.
            csv_row['victim_uri']: The URI of the record to merge.
            csv_row['record_type']: The type of record to be merged.

           Usage
            ::

              >>> csv_row = {'target_uri': '/agents/people/402', 'victim_uri': '/agents/people/3153', 'record_type': 'agent_person'}
              >>> record_json, uri = merge_data(csv_row)
              >>> print(uri)
              '/merge_requests/agent_person'
              >>> print(record_json)
              {'target': {'ref': '/agents/people/402'},
                          'victims': [{'ref': '/agents/people/3153'}],
                          'jsonmodel_type': 'merge_request'}
        '''
        merge_json = {'target': {'ref': csv_row.get('target_uri')},
                      'victims': [{'ref': csv_row.get('victim_uri')}],
                      'jsonmodel_type': 'merge_request'}
        return merge_json, f"/merge_requests/{csv_row.get('record_type')}"

    @_api_caller(ASpaceCrud.updater)
    def migrate_enumerations(csv_row: dict) -> tuple[dict, str]:
        '''Merges controlled values.

           Parameters:
            record_json = The JSON representation of the record
            csv_row['enum_uri']: The URI of the parent enumeration
            csv_row['from']: The name of the enumeration value to merge
            csv_row['to']: The name of the enumeration value to merge into

           Usage
            :: 

              >>> csv_row = {'enum_uri': '/config/enumerations/14', 'from': 'potographs', 'to': 'photographs'}
              >>> record_json, uri = migrate_enumerations(csv_row)
              >>> print(uri)
              '/config/enumerations/migration'
              >>> print(record_json)
              {'enum_uri': '/config/enumerations/14',
                        'from': 'potographs',
                        'to': 'photographs',
                        'jsonmodel_type': 'enumeration_migration'}
        '''
        merge_json = {'enum_uri': csv_row.get('enum_uri'),
                        'from': csv_row.get('from'),
                        'to': csv_row.get('to'),
                        'jsonmodel_type': 'enumeration_migration'}
        return merge_json, "/config/enumerations/migration"

    @_api_caller(ASpaceCrud.creator)
    def create_repositories(csv_row: dict) -> tuple[dict, str]:
        '''Creates a repository record.

           Parameters:
            csv_row['repo_name']: The name of the repository

           Usage
            ::

              >>> csv_row = {'repo_name': 'New Repo'}
              >>> record_json, uri = create_repositories(csv_row)
              >>> print(uri)
              '/repositories'
              >>> print(record_json)
              {'jsonmodel_type': 'repository', 'name': 'New Repo'}
        '''
        new_repo = {'jsonmodel_type': 'repository', 'name': csv_row.get('repo_name')}
        return new_repo, '/repositories'

    @_api_caller(ASpaceCrud.creator)
    def create_archival_objects(csv_row: dict) -> tuple[dict, str]:
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

           TODO: 
            - add instances

           Usage
            ::

              >>> csv_row = {'title': 'Correspondence', 'begin': '1958', 'end': '1999', 'date_type': 'inclusive', 'date_label': 'creation', 'extent_portion': 'whole', 'extent_number': '5', 'extent_type': 'items', 'parent': '/repositories/2/archival_objects/5', 'resource': '/repositories/2/resources/1', 'repository': '/repositories/2'}
              >>> record_json, uri = create_archival_objects(csv_row)
              >>> print(uri)
              '/repositories/2/archival_objects'
              >>> print(record_json)
              {'jsonmodel_type': 'archival_object', 'title': 'Correspondence', 'level': 'file', 'publish': True,
                    'dates': [{'jsonmodel_type': 'date', 'begin': '1958', 'end': '1999', 'date_type': 'inclusive', 'label': 'creation'}],
                    'extents': [{'jsonmodel_type': 'extent', 'portion': 'whole', 'number': '5', 'extent_type': 'items'}],
                    'parent': {'ref': '/repositories/2/archival_objects/5'},
                    'resource': {'ref': '/repositories/2/resources/1'},
                    'repository': {'ref': '/repositories/2'}}
        '''
        new_ao = {'jsonmodel_type': 'archival_object', 'title': csv_row.get('title'), 'level': 'file', 'publish': True,
                    'dates': [{'jsonmodel_type': 'date', 'begin': csv_row.get('date_begin'), 'end': csv_row.get('date_end'),
                                'date_type': csv_row.get('date_type'), 'label': csv_row.get('date_label')}],
                    'extents': [{'jsonmodel_type': 'extent', 'portion': csv_row.get('extent_portion'), 'number': csv_row.get('extent_number'),
                                'extent_type': csv_row.get('extent_type')}],
                    'parent': {'ref': csv_row.get('parent_uri')},
                    'resource': {'ref': csv_row.get('resource_uri')},
                    'repository': {'ref': csv_row.get('repo_uri')}}
        if csv_row.get('extent_type') in ('', None):
            del new_ao['extents']
        if csv_row.get('date_type') in ('', None):
            del new_ao['dates']
        if csv_row.get('parent_uri') in ('', None):
            del new_ao['parent']
        return new_ao, f"{csv_row.get('repo_uri')}/archival_objects"

    @_api_caller(ASpaceCrud.creator)
    def create_minimal_archival_objects(csv_row: dict) -> tuple[dict, str]:
        '''Creates a child archival object record with just a title and level.

           Parameters:
            csv_row['parent_uri']: The URI of the parent archival object.
            csv_row['resource_uri']: The URI of the parent resource.
            csv_row['repo_uri']: The URI of the parent repository.
            csv_row['title']: The archival object title
            csv_row['level']: The archival object level, i.e. 'file'

           Usage
            ::

              >>> csv_row = {'parent_uri': '/repositories/2/archival_objects/5', 'resource_uri': '/repositories/2/resources/1', 'repo_uri': '/repositories/2', 'title': 'Correspondence', 'level': 'file'}
              >>> record_json, uri = create_minimal_archival_objects(csv_row)
              >>> print(uri)
              '/repositories/2/archival_objects'
              >>> print(record_json)
              {'jsonmodel_type': 'archival_object', 'title': 'Correspondence', 'level': 'file', 'publish': True, 'parent': {'ref': '/repositories/2/archival_objects/5'}, 'resource': {'ref': '/repositories/2/resources/1'}, 'repository': {'ref': '/repositories/2'}}
        '''
        new_ao = {'jsonmodel_type': 'archival_object', 'title': csv_row.get('title'), 'level': csv_row.get('level'), 'publish': True,
                    'parent': {'ref': csv_row.get('parent_uri')},
                    'resource': {'ref': csv_row.get('resource_uri')},
                    'repository': {'ref': csv_row.get('repo_uri')}}
        return new_ao, f"{csv_row.get('repo_uri')}/archival_objects"

    @_api_caller(ASpaceCrud.creator)
    def create_accessions(csv_row: dict) -> tuple[dict, str]:
        '''Creates an accession record.

           Parameters:
            csv_row['repo_uri']: The URI of the parent repository.
            csv_row['identifier']: The accession identifier.
            csv_row['title']: The accession title.
            csv_row['accession_date']: The accession date. Format YYYY-MM-DD

           Usage
            ::

              >>> csv_row = {'repo_uri': '/repositories/2', 'identifier': '2022-M-0001', 'title': 'Swim team records', 'accession_date': '2022-01-02'}
              >>> record_json, uri = create_accessions(csv_row)
              >>> print(uri)
              '/repositories/2/accessions'
              >>> print(record_json)
              {'id_0': '2022-M-0001, 'title': 'Swim team records', 'accession_date': '2022-01-02', 'repository': {'ref': '/repositories/2'}, 'jsonmodel_type': 'accession'}
        '''
        new_accession = {'id_0': csv_row.get('identifier'), 'title': csv_row.get('title'), 'accession_date': csv_row.get('accession_date'), 'repository': {'ref': csv_row.get('repo_uri')},
                         'jsonmodel_type': 'accession'}
        return new_accession, f"{csv_row.get('repo_uri')}/accessions"

    @_api_caller(ASpaceCrud.creator)
    def create_resources(csv_row: dict) -> tuple[dict, str]:
        '''Creates a resource record.

           Parameters:
            csv_row['repo_uri']: The URI of the parent repository.
            csv_row['identifier']: The identifier for the resource.
            csv_row['title']: The title of the resource.
            csv_row['language']: The language code of the resource, i.e eng.
            csv_row['date_begin']: The begin date of the resource.
            csv_row['date_end']: The end date of the resource.
            csv_row['date_type']: The date type of the resource, i.e. inclusive, single.
            csv_row['date_label']: The date label of the resource, i.e. creation.
            csv_row['extent_type']: The extent type of the resource, i.e. photograph.
            csv_row['extent_portion']: The extent portion of the resource, i.e. whole, part.
            csv_row['extent_number']: The extent number of the resource, i.e. 1.
            csv_row['container_summary']: The container summary of the resource.

           Usage
            ::

              >>> csv_row = {'repo_uri': '/repositories/2', 'identifier': 'MS 150', 'title': 'John Smith Papers', 'date_begin': '1958', 'date_end': '1999', 'date_type': 'inclusive', 'date_label': 'creation, 'extent_type': 'linear_feet', 'extent_portion': 'whole', 'extent_number': '6', 'container_summary': '5 boxes'
              'language': 'eng'}
              >>> record_json, uri = create_resources(csv_row)
              >>> print(uri)
              '/repositories/2/resources'
              >>> print(record_json)
              {'id_0': 'MS 150', 'title': 'John Smith Papers', 'level': 'collection',
                        'dates' : [{'begin': '1958', 'end': '1999', 'date_type': 'inclusive', 'label': 'creation',
                                    'jsonmodel_type': 'date'}], 
                        'extents': [{'extent_type': 'linear_feet, 'portion': 'whole', 'number': '6',
                                     'container_summary': '5 boxes', 'jsonmodel_type': 'extent'}],
                        'lang_materials': [{'jsonmodel_type': 'lang_material', 'language_and_script': {'jsonmodel_type': 'language_and_script', 'language': 'eng'}}],
                        'repository': {'ref': '/repositories/2'}, 'jsonmodel_type': 'resource'}
        '''
        new_resource = {'id_0': csv_row.get('identifier'), 'title': csv_row.get('title'), 'level': 'collection',
                        'dates' : [{'begin': csv_row.get('date_begin'), 'end': csv_row.get('date_end'), 'date_type': csv_row.get('date_type'), 'label': csv_row.get('date_label'),
                                    'jsonmodel_type': 'date'}],
                        'extents': [{'extent_type': csv_row.get('extent_type'), 'portion': csv_row.get('extent_portion'), 'number': csv_row.get('extent_number'),
                                     'container_summary': csv_row.get('container_summary'), 'jsonmodel_type': 'extent'}],
                        'lang_materials': [{'jsonmodel_type': 'lang_material', 'language_and_script': {'jsonmodel_type': 'language_and_script', 'language': csv_row.get('language')}}],
                        'repository': {'ref': csv_row.get('repo_uri')}, 'jsonmodel_type': 'resource'}
        return new_resource, f"{csv_row.get('repo_uri')}/resources"

    @_api_caller(ASpaceCrud.creator)
    def create_classification(csv_row: dict) -> tuple[dict, str]:
        '''Creates a classification record.

           Parameters:
            csv_row['repo_uri']: The URI of the parent repository.
            csv_row['identifier']: The identifier of the classification.
            csv_row['title']: The title of the classification.
            csv_row['description']: The description of the classification.

           Usage
            ::

              >>> csv_row = {'repo_uri': '/repositories/2', 'identifier', 'YRG 01', 'title': 'Yale Record Group Classification', 'description': 'Classifications for University Archives Records'}
              >>> record_json, uri = create_classification(csv_row)
              >>> print(uri)
              '/repositories/2/classicifications'
              >>> print(record_json)
              {'jsonmodel_type': 'classification', 'identifier': 'YRG 01',
                              'title': 'Yale Record Group Classification', 'description': 'Classifications for University Archives Records', 'repository': {'ref': '/repositories/2'}}
        '''
        new_classification = {'jsonmodel_type': 'classification', 'identifier': csv_row.get('identifier'),
                              'title': csv_row.get('title'), 'description': csv_row.get('description'), 'repository': {'ref': csv_row.get('repo_uri')}}
        return new_classification, f"{csv_row.get('repo_uri')}/classifications"

    @_api_caller(ASpaceCrud.creator)
    def create_classification_term(csv_row: dict) -> tuple[dict, str]:
        '''Creates a classification term with or without a classification term parent.

           Parameters:
            csv_row['parent_classification_uri']: The URI of the parent classification.
            csv_row['repo_uri']: The URI of the parent repository.
            csv_row['title']: The title of the classification term.
            csv_row['description']: The description of the classification term

           Other Parameters:
            csv_row['parent_classification_term_uri']: The URI of the parent classification term.

           Usage
            ::

              >>> csv_row = {'identifier': 'YRG 001 002', 'title': 'Records of academic departments', 'description': 'Records relating to academic departments', 'parent_classification_uri': '/repositories/2/classification_terms/2', 'repo_uri': '/repositories/2'}
              >>> record_json, uri = create_classification_term(csv_row)
              >>> print(uri)
              '/repositories/2/classification_terms'
              >>> print(record_json)
              {'jsonmodel_type': 'classification_term', 'identifier': 'YRG 001 002',
                                   'title': 'Records of academic departments', 'description': 'Records relating to academic departments', 'classification': {'ref': '/repositories/2/classification_terms/2'},
                                   'repository': {'ref': '/repositories/2'}}
        '''
        new_classification_term = {'jsonmodel_type': 'classification_term', 'identifier': csv_row.get('identifier'),
                                   'title': csv_row.get('title'), 'description': csv_row.get('description'), 'classification': {'ref': csv_row.get('parent_classification_uri')},
                                   'repository': {'ref': csv_row.get('repo_uri')}}
        if csv_row.get('parent_classification_term_uri') not in  ('', None):
            new_classification_term['parent'] = {'ref': csv_row.get('parent_classification_term_uri')}
        return new_classification_term, f"{csv_row.get('repo_uri')}/classification_terms"

    @_api_caller(ASpaceCrud.creator)
    def create_digital_objects(csv_row: dict) -> tuple[dict, str]:
        '''Creates a digital object record with two file versions.

           Parameters:
            csv_row['uri']: The URI of the linked archival object.
            csv_row['url_1']: The URL of the digital library item.
            csv_row['url_2']: The URL of the thumbnail image.
            csv_row['digital_object_id']: The digital object identifier.
            csv_row['digital_object_title']: The digital object title.
            csv_row['repo_uri']: The URI of the parent repository.
        '''
        new_digital_object = {'jsonmodel_type': 'digital_object',
                              'publish': True,
                              'file_versions': [{'file_uri': csv_row.get('url_1'), 'jsonmodel_type': 'file_version',
                                                 'xlink_show_attribute': 'new', 'publish': True},
                                                 {'file_uri': csv_row('url_2'), 'jsonmodel_type': 'file_version',
                                                                                  'xlink_show_attribute': 'embed', 'publish': True}],
                              'digital_object_id': csv_row.get('digital_object_id'),
                              'title': csv_row.get('dig_object_title')}
        return new_digital_object, f"{csv_row.get('repo_uri')}/digital_objects"

    @_api_caller(ASpaceCrud.creator)
    def create_digital_object_component(csv_row: dict) -> tuple[dict, str]:
        '''Creates a digital object component record.

           Parameters:
            csv_row['repo_uri']: The URI of the parent repository.
            csv_row['parent_uri']: The URI of the digital object parent.
            csv_row['component_id']: The identifier of the digital object component.
            csv_row['title']: The title of the digital object component.
        '''
        new_doc = {'component_id': csv_row['component_id'], 'title': csv_row['title'], 'parent': {'ref': csv_row['parent_uri']},
                   'repository': {'ref': csv_row['repo_uri']}, 'jsonmodel_type': 'digital_object_component'}
        return new_doc, f"{csv_row['repo_uri']}/digital_object_components"

    @_api_caller(ASpaceCrud.creator)
    def create_child(csv_row: dict) -> tuple[dict, str]:
        '''Creates a minimal child archival object record.

           Parameters:
            csv_row['parent_uri']: The URI of the parent archival object.
            csv_row['resource_uri']: The URI of the parent resource.
            csv_row['repo_uri']: The URI of the parent repository.
            csv_row['title']: The title of the archival object.
            csv_row['level']: The level of description of the archival object, i.e. file.
        '''
        new_ao = {'jsonmodel_type': 'archival_object', 'title': csv_row['title'],
                    'level': csv_row['level'], 'parent': {'ref': csv_row['parent_uri']},
                    'resource': {'ref': csv_row['resource_uri']}, 'repository': {'ref': csv_row['repo_uri']},
                    'publish': True}
        return new_ao, f"{csv_row['repo_uri']}/archival_objects"

    @_api_caller(ASpaceCrud.creator)
    def create_subseries(csv_row: dict) -> tuple[dict, str]:
        '''Creates a subseries record.

           Parameters:
            csv_row['name']: The title of the archival object.
            csv_row['resource_uri']: The URI of the parent resource.
            csv_row['repo_uri']: The URI of the parent repository.
            csv_row['parent_uri']: The URI of the parent archival object.
        '''
        new_ao = {'jsonmodel_type': 'archival_object', 'title': csv_row['name'],
                    'level': 'subseries', 'parent': {'ref': csv_row['parent_uri']},
                    'resource': {'ref': csv_row['resource_uri']}, 'repository': {'ref': csv_row['repo_uri']},
                    'publish': True}
        return new_ao, f"{csv_row['repo_uri']}/archival_objects"

    @_api_caller(ASpaceCrud.creator)
    def create_location_profiles(csv_row: dict) -> tuple[dict, str]:
        '''Creates a location profile record.

           Parameters:
            csv_row['name']: The name of the location profile.
            csv_row['dimension_units']: The dimension units of the location profile.
            csv_row['depth']: The depth of the location profile.
            csv_row['height']: The height of the location profile.
            csv_row['width']: The width of the location profile.

           Usage
            ::

              >>> csv_row = {'name': 'Short shelf', 'dimension_units': 'inches', 'depth': '12', 'height': '13', 'width': '14'}
              >>> record_json, uri = create_location_profiles(csv_row)
              >>> print(uri)
              '/location_profiles'
              >>> print(record_json)
              {'jsonmodel_type': 'location_profile', 'name': 'Short shelf',
                                  'dimension_units': 'inches', 'depth': '12',
                                  'height': '13', 'width': '14'
                                }
        '''
        csv_row['jsonmodel_type'] = 'location_profile'
        return csv_row, '/location_profiles'

    @_api_caller(ASpaceCrud.updater)
    def create_digital_object_instances(record_json: dict, csv_row: dict) -> tuple[dict, str]:
        '''Creates a instance of a digital object linked to an archival object record.

           Parameters:
            record_json: The JSON representation of the archival object.
            csv_row['uri']: The URI of the archival object record.
            csv_row['new_instance_uri']: The URI of the digital object to link.

           Usage
            ::

              >>> csv_row = {'uri': '/repositories/2/archival_objects/5', 'new_instance_uri': '/repositories/2/digital_objects/1'}
              >>> record_json, uri = create_digital_object_instances(record_json, csv_row)
              >>> print(uri)
              '/repositories/2/archival_objects/5'
              >>> print(record_json)
              {}
        '''
        new_ao_instance = {'jsonmodel_type': 'instance', 'instance_type': 'digital_object',
                           'digital_object': {'ref': csv_row.get('new_instance_uri')}}
        record_json['instances'].append(new_ao_instance)
        return record_json, csv_row.get('uri')

    def create_locations(csv_row: dict) -> tuple[dict, str]:
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
            csv_row['repo_owner']: The URI of the parent repository.

           Other Parameters:
            csv_row['location_profile']: The URI of the location profile.

           Usage
            ::

              >>> csv_row = {'barcode', '93012', 'building': 'SML', 'room': B50, 'coordinate_1_label': 'aisle', 'coordinate_1_indicator': '1', 'coordinate_2_label': 'bay', 'coordinate_2_indicator': '2', 'coordinate_3_label': 'shelf', 'coordinate_3_indicator': '3', 'location_profile': '/location_profiles/4', 'repo_owner': '/repositories/2'}
              >>> record_json, uri = create_locations(csv_row)
              >>> print(uri)
              '/locations'
              >>> print(record_json)
              {'jsonmodel_type': 'location', 'barcode': '93102,
                        'building': 'SML', 'room': 'B50',
                        'coordinate_1_label': 'aisle',
                        'coordinate_1_indicator': 1,
                        'coordinate_2_label': 'bay',
                        'coordinate_2_indicator': ',
                        'coordinate_3_label': 'shelf',
                        'coordinate_3_indicator': '3',
                        'location_profile': {'ref': '/location_profiles/4'},
                        'owner_repo': {'ref': '/repositories/2'}}
        '''
        csv_row['jsonmodel_type'] = 'location'
        if csv_row.get('location_profile') in ('', None):
            del new_location['location_profile']
        return csv_row, '/locations'

    def create_dates(record_json: dict, csv_row: dict) -> tuple[dict, str]:
        '''Creates a date record.

           Parameters:
            csv_row['date_type']: The date type (i.e. inclusive, single)
            csv_row['date_label']: The date label (i.e. creation, broadcast)
            csv_row['begin']: The begin date (YYYY-MM-DD)
            csv_row['end']: The end date (YYYY-MM-DD)
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
        if csv_row.get('end') not in ('', None):
            new_date['end'] = csv_row['end']
        record_json['dates'].append(new_date)
        return record_json, csv_row['uri']

    def create_extent_remove_physdesc(record_json: dict, csv_row: dict) -> tuple[dict, str]:
        '''Creates an extent record, removes a physdesc record.

           Parameters:
            csv_row['extent_type']: The extent type (i.e. linear_feet)
            csv_row['extent_portion']: Whole or part
            csv_row['extent_number']: The quantity
            csv_row['container_summary']: The container summary
            csv_row['persistent_id']: The persistent ID of the physdesc record
        '''
        if len(record_json['extents']) == 0:
            new_extent = {'jsonmodel_type': 'extent', 'portion': csv_row['extent_portion'], 'number': csv_row['number'],
                                    'extent_type': csv_row['extent_type']}
            if container_summary != '':
                new_extent['container_summary'] = container_summary
            record_json['extents'].append(new_extent)
            for note in record_json['notes']:
                if note['persistent_id'] == persistent_id:
                    note.clear()
        return record_json, csv_row['uri']

    def create_extents(record_json: dict, csv_row: dict) -> tuple[dict, str]:
        '''Creates an extent record.

           Parameters:
            csv_row['extent_type']: The extent type (i.e. linear_feet)
            csv_row['extent_portion']: Whole or part
            csv_row['extent_number']: The quantity
        '''
        new_extent = {'jsonmodel_type': 'extent', 'portion': csv_row['extent_portion'], 'number': csv_row['extent_number'],
            'extent_type': csv_row['extent_type']}
        record_json['extents'].append(new_extent)
        return record_json, csv_row['uri']

    def create_events(csv_row: dict) -> tuple[dict, str]:
        '''Creates an event record.

           Parameters:
            csv_row['event_type']: The event type.
            csv_row['outcome']: The event outcome.
            csv_row['date_begin']: The begin date of the event.
            csv_row['date_end']: The end date of the event.
            csv_row['date_type']: The date type (inclusive, single)
            csv_row['date_label']: The date label (digitization)
            csv_row['repo_uri']: The URI of the parent repository
            csv_row['record_link']: The URI of the record to link.
            csv_row['agent']: The URI of the agent authorizer.

           Other Parameters:
            csv_row['external_doc_title']: The title of the external document.
            csv_row['external_doc_location']: The location of the external document.

           Todo:
            check if this works
        '''
        new_event = {'jsonmodel_type': 'event', 'event_type': csv_row['event_type'], 'outcome': csv_row['outcome'],
                    'date': {'begin': csv_row['date_begin'], 'date_type': csv_row['date_type'],
                            'jsonmodel_type': 'date', 'label': csv_row['date_label']},
                    'repository': {'ref': csv_row['repo_uri']},
                    'linked_records': [{'ref': csv_row['record_link'], 'role': csv_row['record_role']}],
                    'linked_agents': [{'role': csv_row['agent_role'], 'ref': csv_row['agent_uri']}],
                    'external_documents': []}
        if csv_row.get('date_end') not in ('', None):
            new_event['date']['end'] = csv_row['date_end']
        # if csv_row.get('external_doc_title') != '':
        #     external_document = {'jsonmodel_type': 'external_document', 'location': csv_row['external_doc_location'],
        #                             'title': csv_row['external_doc_title']}
        #     new_event['external_documents'].append(external_document)
        #double check if events are scoped to repositories
        return new_event, f"{csv_row['repo_uri']}/events"

    def create_top_containers(csv_row: dict) -> tuple[dict, str]:
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

           Todo:
            make sure that sub-containers can only be added to instance records, not anywhere within a container record. Almost certain this is this case.
        '''
        new_top_container = {'jsonmodel_type': 'top_container', 'indicator': csv_row['indicator'],
                             'repository': {'ref': csv_row['repo_uri']}}
        if csv_row.get('type') not in ('', None):
            new_top_container['type'] = csv_row['type']
        if csv_row.get('barcode') not in ('', None):
            new_top_container['barcode'] = csv_row['barcode']
        if csv_row.get('container_profile_uri') not in ('', None):
            #eventually add way to search by container profile name
            #container_profile_uri = crud.search_container_profiles()
            new_top_container['container_profile'] = {'ref': csv_row['container_profile_uri']}
        if csv_row.get('location_uri') not in ('', None):
            new_location = [{'jsonmodel_type': 'container_location',
                                     'status': 'current', 'ref': csv_row['location_uri'],
                                     'start_date': csv_row['start_date']}]
            new_top_container['container_locations'] = new_location
        return new_top_container, f"{csv_row['repo_uri']}/top_containers"

    def update_instance_by_uri(record_json: dict, csv_row: dict) -> tuple[dict, str]:
        '''Updates an instance subrecord with sub_container data.

           Parameters:
            record_json: The JSON representation of the archival object.
            csv_row['uri']: The URI of the archival object record.
            csv_row['tc_uri']: The URI of the top container.
            csv_row['type_2']: The sub_container type, i.e. folder.
            csv_row['indicator_2']: The sub_container number, i.e. 1.
        '''
        for instance in record_json['instances']:
            if instance['sub_container']['top_container']['ref'] == csv_row['tc_uri']:
                instance['sub_container']['type_2'] = csv_row['type_2']
                instance['sub_container']['indicator_2'] = csv_row['indicator_2']
        return record_json, csv_row['uri']

    def update_indicator_2(record_json: dict, csv_row: dict) -> tuple[dict, str]:
        '''Updates an instance subrecord with a new indicator_2.

           Parameters:
            record_json: The JSON representation of the archival object.
            csv_row['uri']: The URI of the archival object record.
            csv_row['tc_uri']: The URI of the top container.
            csv_row['indicator_2']: The sub_container number, i.e. 1.
        '''
        for instance in record_json['instances']:
            if instance['sub_container']['top_container']['ref'] == csv_row['tc_uri']:
                    instance['sub_container']['indicator_2'] = csv_row['indicator_2']
        return record_json, csv_row['uri']

    def update_instance_ref(record_json: dict, csv_row: dict) -> tuple[dict, str]:
        '''Updates an instance subrecord with a new top container URI. 
            Searches for and replaces a top container reference.

           Parameters:
            record_json: The JSON representation of the archival_object
            csv_row['uri']: The URI of the archival object record
            csv_row['old_top_container']: The URI of the top container to replace
            csv_row['new_top_container']: The URI of the new top container
        '''
        for instance in record_json['instances']:
            if instance.get('sub_container'):
                if instance['sub_container']['top_container']['ref'] == csv_row['old_top_container']:
                    instance['sub_container']['top_container']['ref'] = csv_row['new_top_container']
        return record_json, csv_row['uri']

    def create_subcontainer(record_json: dict, csv_row: dict) -> tuple[dict, str]:
        '''Updates the first instance subrecord with a new type_2 and indicator_2.

           Parameters:
            record_json: The JSON representation of the archival object
            csv_row['uri']: The URI of the archival object record
            csv_row['type_2']: The child type
            csv_row['indicator_2']: The child indicator
        '''
        if record_json.get('instances'):
            record_json['instances'][0]['sub_container']['type_2'] = csv_row['type_2']
            record_json['instances'][0]['sub_container']['indicator_2'] = csv_row['indicator_2']
        return record_json, csv_row['uri']

    def update_subcontainer(record_json: dict, csv_row: dict) -> tuple[dict, str]:
        '''Updates the top container ref, indicator 2, and type 2 fields of a subcontainer record.
           Assumes that there is just a single instance.

           Parameters:
            record_json: The JSON representation of the archival_object
            csv_row['uri']: The URI of the archival object record
            csv_row['type_2']: The child type
            csv_row['indicator_2']: The child indicator
            csv_row['tc_uri']: The top container URI
        '''
        if record_json.get('instances'):
            record_json['instances'][0]['sub_container']['type_2'] = csv_row['type_2']
            record_json['instances'][0]['sub_container']['indicator_2'] = csv_row['indicator_2']
            record_json['instances'][0]['sub_container']['top_container']['ref'] = csv_row['tc_uri']
        return record_json, csv_row['uri']

    def create_instances(record_json: dict, csv_row: dict) -> tuple[dict, str]:
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
            csv_row['grandchild_indicator']: The grandchild indicator, i.e 78
        '''
        new_instance = {'jsonmodel_type': 'instance', 'instance_type': csv_row['instance_type'],
                        'sub_container': {'jsonmodel_type': 'sub_container',
                                          'top_container': {'ref': csv_row['tc_uri']}}}
        if csv_row.get('child_type') not in ('', None):
            new_instance['sub_container']['type_2'] = csv_row['child_type']
            new_instance['sub_container']['indicator_2'] = csv_row['child_indicator']
        if csv_row.get('grandchild_type') not in ('', None):
            new_instance['sub_container']['type_3'] = csv_row['grandchild_type']
            new_instance['sub_container']['indicator_3'] = csv_row['grandchild_indicator']
        record_json['instances'].append(new_instance)
        return record_json, csv_row['uri']

    def create_multipart_note(record_json: dict, csv_row: dict) -> tuple[dict, str]:
        '''Creates a multipart note and links it to a descriptive record.

           Parameters:
            record_json: The JSON representation of the parent record.
            csv_row['uri']: The URI of the parent record.
            csv_row['note_string']: The note text.
            csv_row['note_type']: The note type, i.e. accessrestrict
        '''
        new_note = {'jsonmodel_type': 'note_multipart',
                    'publish': True,
                    'subnotes': [{'content': csv_row['note_string'],
                              'jsonmodel_type': 'note_text',
                              'publish': True}],
                'type': csv_row['note_type']}
        record_json['notes'].append(new_note)
        return record_json, csv_row['uri']

    def create_glad_scope_note(record_json: dict, csv_row: dict) -> tuple[dict, str]:
        '''Creates a multipart scope and content note and links it to a descriptive record.

           Parameters:
            record_json: The JSON representation of the parent record.
            csv_row['uri']: The URI of the parent record.
            csv_row['note']: The note text.
        '''
        if csv_row.get('note') not in ('', None):
            new_note = f"Includes the following resource files:\n {csv_row['note']}"
            scope_note = {'jsonmodel_type': 'note_multipart',
                        'publish': True,
                        'subnotes': [{'content': new_note,
                                  'jsonmodel_type': 'note_text',
                                  'publish': True}],
                    'type': 'scopecontent'}
            record_json['notes'].append(scope_note)
            return record_json, csv_row['uri']

    def update_glad_scope_note(record_json: dict, csv_row: dict) -> tuple[dict, str]:
        '''Updates a multipart scope and content note, changing the subnote type
           from note_text to note_definedlist. Replaces an entire set of existing
           subnotes.

           Parameters:
            record_json: The JSON representation of the parent record.
            csv_row['uri']: The URI of the parent record.
            csv_row['persistent_id']: The persistent ID of the existing note
            csv_row['items']: A string representation of the list of items
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
        return record_json, csv_row['uri']

    def create_container_profiles(csv_row: dict) -> tuple[dict, str]:
        '''Creates a container profile record.

           Parameters:
            csv_row['name']: The name of the container profile.
            csv_row['extent_dimension']: The extent dimension of the container profile, i.e. width.
            csv_row['height']: The height of the container profile.
            csv_row['width']: The width of the container profile.
            csv_row['depth']: The depth of the container profile.
            csv_row['dimension_units']: The dimension units of the container profile.
        '''
        new_container_profile = {'jsonmodel_type': 'container_profile', 'name': csv_row['name'],
                                 'extent_dimension': csv_row['extent_dimension'], 'height': csv_row['height'],
                                 'width': csv_row['width'], 'depth': csv_row['depth'], 'dimension_units': csv_row['dimension_units']}
        return new_container_profile, '/container_profiles'

    #@atl.as_tools_logger(logger)
    def create_hm_external_ids(record_json: dict, csv_row: dict) -> tuple[dict, str]:
        '''Creates an external ID subrecord and links it to a descriptive record.

           Parameters:
            record_json: The JSON representation of the parent record.
            csv_row['uri']: The URI of the parent record.
            csv_row['hm_number']: The external ID value.
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
        return record_json, csv_row['uri']

    def update_file_version_format(record_json: dict, csv_row: dict) -> tuple[dict, str]:
        '''Updates a file version record with a file format type.

           Parameters:
            record_json: The JSON representation of the digital object record.
            csv_row['uri']L The URI of the digital object record.
            csv_row['file_uri']: The url of the file version subrecord.
            csv_row['file_format_name']: The file format name (database value)
        '''
        for file_version in record_json['file_versions']:
            if file_version.get('file_uri') == csv_row['file_uri']:
                file_version['file_format_name'] = csv_row['file_format_name']
        return record_json, csv_row['uri']

    def create_digital_content_file_version(record_json: dict, csv_row: dict) -> tuple[dict, str]:
        '''Creates a single file version record and adds it to a digital object record.

           Parameters:
            record_json: The JSON representation of the digital object record.
            csv_row['uri']: The URI of the digital object record.
            csv_row['file_version_url']: The URL of the file version subrecord.
            csv_row['file_format_name']: The file format name (i.e. pdf)
            csv_row['file_size_bytes']: File size in bytes. Sometimes it is too big. Version 3 of AS corrects this
        '''
        new_file_version = {'jsonmodel_type': 'file_version', 'file_uri': csv_row['file_version_url'],
                            'file_format_name': csv_row['file_format_name'],
                            'publish': False, 'xlink_show_attribute': 'new', 'xlink_actuate_attribute': 'onRequest'}
        if csv_row['file_size_bytes'] != "":
            new_file_version['file_size_bytes'] = int(csv_row['file_size_bytes'])
        record_json['file_versions'].append(new_file_version)
        return record_json, csv_row['uri']

    def create_file_version(record_json: dict, csv_row: dict) -> tuple[dict, str]:
        '''Creates a single file version record and adds it to a digital object record.

           Parameters:
            record_json: The JSON representation of the digital object record.
            csv_row['uri']: The URI of the digital object record.
            csv_row['file_version_url']: The URL of the file version subrecord.
            csv_row['xlink_show_attribute']: The xlink show attribute of the file version, i.e. embed
        '''
        new_file_version = {'jsonmodel_type': 'file_version', 'file_uri': csv_row['file_version_url'],
                            'publish': True, 'xlink_show_attribute': csv_row['xlink_show_attribute']}
        record_json['file_versions'].append(new_file_version)
        return record_json, csv_row['uri']

    def create_file_versions(record_json: dict, csv_row: dict) -> tuple[dict, str]:
        '''Creates multiple file versions and adds them to a digital object record.

           Parameters:
            record_json: The JSON representation of the digital object record.
            csv_row['uri']: The URI of the digital object record.
            csv_row['file_version_url_01']: The URL of the first file version subrecord.
            csv_row['file_version_url_02']: The URL of the second file version subrecord.
            csv_row['digital_object_id']: The digital object identifier.

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
        return record_json, csv_row['uri']

    def create_timebound_access_restriction(record_json: dict, csv_row: dict) -> tuple[dict, str]:
        '''Creates an accessrestrict note with a timebound restriction.

           Parameters:
            record_json: The JSON representation of the descriptive record.
            csv_row['uri']: The URI of the descriptive record.
            csv_row['note']: The free-text access note.
            csv_row['end_date']: The date the restriction expires.
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
        return record_json, csv_row['uri']

    def update_notes_titles(record_json: dict, csv_row: dict) -> tuple[dict, str]:
        '''Updates a subnote record and a title

           Parameters:
            record_json: The JSON representation of the descriptive record.
            csv_row['uri']: The URI of the descriptive record.
            csv_row['persistent_id']: The persistent ID of the note to update.
            csv_row['title']: The new title of the descriptive record
            csv_row['subnotes']: The new subnote
        '''
        record_json['title'] = csv_row['title']
        for note in record_json['notes']:
            import ast
            if note['persistent_id'] == csv_row['persistent_id']:
                subnotes = ast.literal_eval(csv_row['subnotes'])
                note['subnotes'] = subnotes
        return record_json, csv_row['uri']

    def create_use_surrogate_access_notes(record_json: dict, csv_row: dict) -> tuple[dict, str]:
        '''Creates an accessrestrict note for HM microfilm surrogates and
           links it to a descriptive record.

           Parameters:
            record_json: The JSON representation of the descriptive record.
            csv_row['uri']: The URI of the descriptive record.
            csv_row['external_id']: The external ID of the descriptive record.
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
        return record_json, csv_row['uri']

    def check_for_access_note(note_data) -> list:
        return [note.get('persistent_id') for note in note_data if note.get('type') == 'accessrestrict']

    def check_for_matching_use_note_text(record_json: dict, csv_row: dict) -> tuple[dict, str]:
        '''Checks note subrecord for matching use note text.

           Parameters:
            record_json: The JSON representation of the descriptive record.
            csv_row['uri']: The URI for the descriptive record
            csv_row['original_note_text']
        '''
        for note in record_json.get('notes'):
            if note.get('type') == 'userestrict':
                note_text = note['subnotes'][0]['content']
                if note_text == csv_row['original_note_text']:
                    print('Use note matches')
                else:
                    print('Use note does not match')
        return record_json, csv_row['uri']

    def update_use_note(record_json: dict, csv_row: dict) -> tuple[dict, str]:
        '''Replaces a note with the type 'userestrict' with new text.

           Parameters:
            record_json: The JSON representation of the descriptive record.
            csv_row['uri']: The URI for the descriptive record
            csv_row['new_note_text']
        '''
        for note in record_json.get('notes'):
            if note.get('type') == 'userestrict':
                note['subnotes'][0]['content'] = csv_row['new_note_text'].strip()
        return record_json, csv_row['uri']

    def create_born_digital_access_note(record_json: dict, csv_row: dict) -> tuple[dict, str]:
        '''Creates an access note for BornDigital materials

           Parameters:
            record_json: The JSON representation of the descriptive record.
            csv_row['uri']: The URI of the descriptive record.
        '''
        note_text = "As a preservation measure, original computer files may not be used. Digital access copies must be provided for use."
        checks_notes = check_for_access_note(record_json.get('notes'))
        if checks_notes:
            persistent_id = checks_notes[0]
            for note in record_json.get('notes'):
                if note.get('persistent_id') == persistent_id:
                    if note['rights_restriction']:
                        note['rights_restriction']['local_access_restriction_type'].append('BornDigital')
                    else:
                        note['rights_restriction'] = {'local_access_restriction_type': ['BornDigital']}
        else:
            new_note = {'jsonmodel_type': 'note_multipart',
                        'publish': True,
                        'subnotes': [{'content': note_text,
                              'jsonmodel_type': 'note_text',
                              'publish': True}],
                        'type': 'accessrestrict',
                        'rights_restriction': {'local_access_restriction_type': ['BornDigital']}}
            record_json['notes'].append(new_note)
        return record_json, csv_row['uri']


    def create_local_access_restriction(record_json: dict, csv_row: dict) -> tuple[dict, str]:
        '''Creates a local access restriction type and links it to an existing note in a descriptive record.

           Parameters:
            record_json: The JSON representation of the descriptive record.
            csv_row['uri']: The URI of the descriptive record.
            csv_row['persistent_id']: The persistent ID of the parent note.
            csv_row['local_type']: The local access restriction type.
        '''
        for note in record_json['notes']:
            if note['persistent_id'] == csv_row['persistent_id']:
                if 'rights_restriction' in note:
                    note['rights_restriction']['local_access_restriction_type'].append(csv_row['local_type'])
                else:
                    note['rights_restriction'] = {'local_access_restriction_type': [csv_row['local_type']]}
        return record_json, csv_row['uri']

    def create_timebound_restriction(record_json: dict, csv_row: dict) -> tuple[dict, str]:
        '''Creates a timebound restriction type and links it to a note in a descriptive record.

           Parameters:
            record_json: The JSON representation of the descriptive record.
            csv_row['uri']: The URI of the descriptive record.
            csv_row['persistent_id']: The persistent ID of the parent note.
            csv_row['begin']: The begin date of the restriction. Format YYYY-MM-DD required.
            csv_row['end']: The end date of the restriction. Format YYYY-MM-DD required.

        '''
        for note in record_json['notes']:
            if note['persistent_id'] == csv_row['persistent_id']:
                #this might not work for some of the older records which
                #don't have the rights restriction dictionary
                note['rights_restriction']['begin'] = csv_row['begin']
                note['rights_restriction']['end'] = csv_row['end']
        return record_json, csv_row['uri']

    def update_identifiers(record_json: dict, csv_row: dict) -> tuple[dict, str]:
        '''Moves resource identifiers which are split across multiple fields into a
           single field.

           Parameters:
            record_json: The JSON representation of the parent record.
            csv_row['uri']: The URI of the parent record.
            csv_row['identifier']: The new identifier.
        '''
        record_json['id_0'] = csv_row['identifier']
        if 'id_1' in record_json:
            del record_json['id_1']
        if 'id_2' in record_json:
            del record_json['id_2']
        if 'id_3' in record_json:
            del record_json['id_3']
        return record_json, csv_row['uri']

    def update_container_type(record_json: dict, csv_row: dict) -> tuple[dict, str]:
        '''Updates the container type of a top container record.

           Parameters:
            record_json: The JSON representation of the top container record.
            csv_row['uri']: The URI of the top container record.
            csv_row['container_type']: The new container type


           Usage
              
        '''
        record_json['type'] = container_type
        return record_json, csv_row['uri']

    def link_agent_to_record(record_json: dict, csv_row: dict) -> tuple[dict, str]:
        '''Links an agent record to a descriptive record.

           Parameters:
            record_json: The JSON representation of the descriptive record.
            csv_row['agent_uri']: The URI of the agent record.
            csv_row['uri']: The URI of the descriptive record.

           Usage
            ::

              >>> csv_row = {'agent_uri': '/agents/people/5', 'uri': '/repositories/2/archival_objects/5'}
              >>> record_json, uri = link_agent_to_record(record_json, csv_row)
              >>> print(uri)
              '/repositories/2/archival_objects/5'
              >>> print(record_json)
              {}
        '''
        record_json['linked_agents'].append({'ref': csv_row['agent_uri']})
        return record_json, csv_row['uri']

    def link_event_to_record(record_json: dict, csv_row: dict) -> tuple[dict, str]:
        '''Links an event record to a descriptive record.

           Parameters:
            record_json: The JSON representation of the descriptive record.
            csv_row['uri']: The URI of the descriptive record.
            csv_row['event_uri']: The URI of the event record.

           Usage
            ::

               >>> csv_row = {'uri': '/repositories/2/archival_objects/5', 'event_uri': '/repositories/2/events/6'}
               >>> record_json, uri = link_event_to_record(record_json, csv_row)
               >>> print(uri)
               '/repositories/2/archival_objects/5'
               >>> print(record_json)
               {}
        '''
        record_json['linked_events'].append({'ref': csv_row['event_uri']})
        return record_json, csv_row['uri']

    def link_record_to_classification(record_json: dict, csv_row: dict) -> tuple[dict, str]:
        '''Links a record to a classification or classification term.

           Parameters:
            record_json: The JSON representation of the descriptive record.
            csv_row['classification_uri']: The URI of the classification term
            csv_row['uri']: The URI of the record to link.

           Usage
            ::

              >>> csv_row = {'uri': '/repositories/2/archival_objects/5'}

        '''
        record_json['linked_records'].append({'ref': csv_row['uri']})
        return record_json, csv_row['uri']

    def update_eng_finding_aid_language(record_json: dict, csv_row: dict) -> tuple[dict, str]:
        '''Updates a finding aid language value to English (before v 2.8)

           Parameters:
            record_json: The JSON representation of the descriptive record.
            csv_row['uri']: The URI of the descriptive record.
            csv_row['finding_aid_language']: The new finding aid language value
        '''
        record_json['finding_aid_language'] = "Finding aid written in <language langcode=\"eng\" scriptcode=\"Latn\">English</language>."
        return record_json, csv_row['uri']

    def update_indicators(record_json: dict, csv_row: dict) -> tuple[dict, str]:
        '''Updates a top container record with a new indicator.

           Parameters:
            record_json: The JSON representation of the top container record.
            csv_row['uri']: The URI of the top container record.
            csv_row['indicator']: The barcode of the top container.
        '''
        record_json['indicator'] = csv_row['indicator']
        return record_json, csv_row['uri']

    def update_barcodes(record_json: dict, csv_row: dict) -> tuple[dict, str]:
        '''Updates a top container record with barcode.

           Parameters:
            record_json: The JSON representation of the top container record.
            csv_row['uri']: The URI of the top container record.
            csv_row['barcode']: The barcode of the top container.
        '''
        record_json['barcode'] = csv_row['barcode']
        return record_json, csv_row['uri']

    def update_barcodes_indicators(record_json: dict, csv_row: dict) -> tuple[dict, str]:
        '''Updates a top container record with barcode and indicator.

           Parameters:
            record_json: The JSON representation of the top container record.
            csv_row['uri']: The URI of the top container record.
            csv_row['barcode']: The barcode of the top container.
            csv_row['indicator']: The indicator (box number) of the top container.
        '''
        record_json['barcode'] = csv_row['barcode']
        record_json['indicator'] = csv_row['indicator']
        return record_json, csv_row['uri']

    #abstract
    def update_top_containers(record_json: dict, csv_row: dict) -> tuple[dict, str]:
        '''Updates a top container record with barcode and adds a type value of 'Box'
           to the record. Also adds LSF as the location.

           Parameters:
            record_json: The JSON representation of the top container record.
            csv_row['tc_uri']: The URI of the top container record.
            csv_row['barcode']: The barcode of the top container.
        '''
        record_json['barcode'] = csv_row['barcode']
        record_json['type'] = 'Box'
        new_location = {'jsonmodel_type': 'container_location', 'ref': '/locations/9', 'status': 'current', 'start_date': '2017-03-01'}
        record_json['container_locations'].append(new_location)
        return record_json, csv_row['uri']

    def update_container_location(record_json: dict, csv_row: dict) -> tuple[dict, str]:
        '''Updates a top container record with a location

           Parameters:
            record_json: The JSON representation of the top container record.
            csv_row['uri']: The URI of the top container record.
            csv_row['location_uri']: The barcode of the top container.
        '''
        new_location = {'jsonmodel_type': 'container_location', 'ref': csv_row['location_uri'], 'status': 'current', 'start_date': '2017-03-01'}
        record_json['container_locations'].append(new_location)
        return record_json, csv_row['uri']

    def update_title(record_json: dict, csv_row: dict) -> tuple[dict, str]:
        '''Updates a record title.

           Parameters:
            record_json: The JSON representation of the top container record.
            csv_row['uri']: The URI of the top container record.
            csv_row['title']: The new title.
        '''
        record_json['title'] = csv_row['title']
        return record_json, csv_row['uri']

    def update_container_type_to_box(record_json: dict, csv_row: dict) -> tuple[dict, str]:
        '''Updates a container record with a type value of 'Box'.

           Parameters:
            record_json: The JSON representation of the top container record.
            csv_row['uri']: The URI of the top container record.
        '''
        record_json['type'] = 'Box'
        return record_json, csv_row['uri']

    def update_date_begin(record_json: dict, csv_row: dict) -> tuple[dict, str]:
        '''Updates date subrecords.

           Parameters:
            record_json: The JSON representation of the parent record.
        '''
        for date in record_json['dates']:
            date['begin'] = csv_row['begin']
        return record_json, csv_row['uri']

    def update_event_date(record_json: dict, csv_row: dict) -> tuple[dict, str]:
        '''Updates a date subrecord with new begin date, an end
            date if present, and a label

           Parameters:
            record_json: The JSON representation of the parent record.
            csv_row['uri']: The URI of the parent record
            csv_row['begin']: The begin date
            csv_row['end']: The end date
            csv_row['label']: The date label    
        '''
        record_json['date']['begin'] = csv_row['begin']
        if csv_row.get('date_type') not in ('', None):
            record_json['date']['date_type'] = csv_row['date_type']
        if csv_row.get('end') not in ('', None):
            record_json['date']['end'] = csv_row['end']
        return record_json, csv_row['uri']

    def update_date_type(record_json: dict, csv_row: dict) -> tuple[dict, str]:
        '''Checks whether a date lacks end value, or whether the begin and end values
          and if either are true changes the date type to 'single'

          Parameters:
           record_json: The JSON representation of the descriptive record.
           csv_row['uri']: The URI of the descriptive record.
        '''
        for date in record_json['dates']:
            if 'end' not in date:
                date['date_type'] = 'single'
            elif date['end'] == date['begin']:
                date['date_type'] = 'single'
        return record_json, csv_row['uri']

    def update_box_numbers(record_json: dict, csv_row: dict) -> tuple[dict, str]:
        '''Updates indicator numbers in top container records.

           Parameters:
            record_json: The JSON representation of the top container record.
            csv_row['uri']: The URI of the top container record.
            csv_row['old_box']: The old box number.
            csv_row['new_box']: The new box number.
        '''
        if record_json['indicator'] == csv_row['old_box']:
            record_json['indicator'] = csv_row['new_box']
        return record_json, csv_row['uri']

    def update_folder_numbers(record_json: dict, csv_row: dict) -> tuple[dict, str]:
        '''Updates indicator numbers in instance subrecords.

           Parameters:
            record_json: The JSON representation of the descriptive record.
            csv_row['uri']: The URI of the descriptive record.
            csv_row['old_folder']: The old folder number.
            csv_row['new_folder']: The new folder number.
        '''
        for instance in record_json['instances']:
            if instance['indicator_2'] == csv_row['old_folder']:
                instance['indicator_2'] = csv_row['new_folder']
        return record_json, csv_row['uri']

    def update_revision_statements(record_json: dict, csv_row: dict) -> tuple[dict, str]:
        '''Updates a revision statement.

           Parameters:
            record_json: The JSON representation of the resource record.
            csv_row['uri']: The URI of the resource record.
            csv_row['revision_date']: The revision date of the resource record.
            csv_row['old_text']: The old revision statement.
            csv_row['new_text']: The new revision statement
        '''
        for revision_statement in record_json['revision_statements']:
            if revision_statement['description'] == csv_row['old_text']:
                revision_statement['description'] = csv_row['new_text']
        return record_json, csv_row['uri']

    def update_notes(record_json: dict, csv_row: dict) -> tuple[dict, str]:
        '''Updates singlepart or multipart notes.

           Parameters:
            record_json: The JSON representation of the parent record.
            csv_row['uri']: The URI of the parent record.
            csv_row['persistent_id']: The persistent ID of the parent note.
            csv_row['note_text']: The new note text.
        '''
        for note in record_json['notes']:
            if note['jsonmodel_type'] == 'note_multipart':
                if note['persistent_id'] == csv_row['persistent_id']:
                    note['subnotes'][0]['content'] = csv_row['note_text']
            elif note['jsonmodel_type'] == 'note_singlepart':
                if note['persistent_id'] == csv_row['persistent_id']:
                    note['content'] = [csv_row['note_text']]
        return record_json, csv_row['uri']

    def update_access_notes(record_json: dict, csv_row: dict) -> tuple[dict, str]:
        '''Updates existing accessrestrict notes for HM films.

           Parameters:
            record_json: The JSON representation of the parent record.
            csv_row['uri']: The URI of the parent record.
            csv_row['persistent_id']: The persistent ID of the parent note.
            csv_row['external_id']: The external ID of the parent record.
        '''
        note_text = f"This material has been microfilmed. Patrons must use {external_id} instead of the originals"
        for note in record_json['notes']:
            if note.get('persistent_id') == csv_row['persistent_id']:
                note['subnotes'][0]['content'] = csv_row['note_text']
                note['rights_restriction'] = {'local_access_restriction_type': ['UseSurrogate']}
        return record_json, csv_row['uri']

    def update_external_document_location(record_json: dict, csv_row: dict) -> tuple[dict, str]:
        '''Updates the file location of an external document subrecord.

           Parameters:
            record_json: The JSON representation of the top-level record.
            csv_row['uri']: The URI of the top-level record.
            csv_row['old_link']: The "old" file location of the external document
            csv_row['new_link']: The file location of the updated external document


        '''
        for external_document in record_json['external_documents']:
            if external_document.get('location') == csv_row['old_link']:
                external_document['location'] = csv_row['new_link']
        return record_json, csv_row['uri']

    def update_date_expressions(record_json: dict, csv_row: dict) -> tuple[dict, str]:
        '''Adds a date expression to a date record.

           Parameters:
            record_json: The JSON representation of the top-level record.
            csv_row['uri']: The URI of the top-level record.
            csv_row['expression']: The date expression to be added.
            csv_row['begin']: The structured begin date to match the against the date JSON.
            csv_row['end']: The structured end date to match against the date JSON.
        '''
        if record_json['jsonmodel_type'].startswith('agent'):
            key = 'dates_of_existence'
        else:
            key = 'dates'
        for date in record_json[key]:
            if csv_row.get('end') not in ('', None):
                if (date['begin'] == csv_row['begin']) and (date['end'] == csv_row['end']):
                    date['expression'] = csv_row['expression']
            elif csv_row['end'] == '':
                if date['begin'] == csv_row['begin']:
                    date['expression'] = csv_row['expression']
        return record_json, csv_row['uri']

    def update_locations(record_json: dict, csv_row: dict) -> tuple[dict, str]:
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
        '''
        record_json['barcode'] = csv_row['barcode']
        record_json['location_profile'] = {'ref': csv_row['location_profile']}
        record_json['owner_repo'] = {'ref': csv_row['owner_repo']}
        if csv_row.get('coordinate_2_indicator') not in ('', None):
            record_json['coordinate_2_indicator'] = csv_row['coordinate_2_indicator']
        return record_json, csv_row['uri']

    def update_location_coordinates(record_json: dict, csv_row: dict) -> tuple[dict, str]:
        '''Updates location labels and indicators.

           Parameters:
            record_json: The JSON representation of the location record
            csv_row['uri']: The URI of the location record
            csv_row['coordinate_1_label']: The label of location coordinate_1
            csv_row['coordinate_1_indicator']: The indicator of location coordinate_1
            csv_row['coordinate_2_label']: The label of location coordinate_2
            csv_row['coordinate_2_indicator']: The indicator of location coordinate_2
            csv_row['coordinate_3_label']: The label of location coordinate_3
            csv_row['coordinate_3_indicator']: The indicator of location coordinate_3

           Usage
            ::

              >>> csv_row = {'uri': '/locations/5', 'coordinate_1_label': 'aisle', 'coordinate_1_indicator': '1', 'coordinate_2_label': 'bay', 'coordinate_2_indicator': 'a', 'coordinate_3_label': 'shelf', 'coordinate_3_indicator': 3}
              >>> record_json, uri = update_location_coordinates(record_json, csv_row)
              >>> print(uri)
              '/locations/5'
              >>> print(record_json)
              {}
        '''
        record_json['coordinate_1_indicator'] = csv_row.get('coordinate_1_indicator')
        record_json['coordinate_1_label'] = csv_row.get('coordinate_1_label')
        record_json['coordinate_2_indicator'] = csv_row.get('coordinate_2_indicator')
        record_json['coordinate_2_label'] = csv_row.get('coordinate_2_label')
        record_json['coordinate_3_indicator'] = csv_row.get('coordinate_3_indicator')
        record_json['coordinate_3_label'] = csv_row.get('coordinate_3_label')
        return record_json, csv_row.get('uri')

    def update_record_component(record_json: dict, csv_row: dict) -> tuple[dict, str]:
        '''Updates a non-nested field in a top-level record.

           Parameters:
            record_json: The JSON representation of the record.
            csv_row['uri']: The URI of the record.
            csv_row['updated_text']: The new value.
            csv_row['component']: The component to update.

           Usage
            ::

              >>> csv_row = {'uri': '/repositories/2/archival_objects/5', 'updated_text': 'Correspondence', 'component': 'title'}
              >>> record_json, uri = update_record_component(record_json, csv_row)
              >>> print(uri)
              '/repositories/2/archivaL_objects/5'
              >>> print(record_json)
              {}
        '''
        record_json[csv_row.get('component')] = csv_row.get('updated_text')
        return record_json, csv_row.get('uri')

    def update_record_components(record_json: dict, csv_row: dict) -> tuple[dict, str]:
        '''Updates non-nested fields in a top-level record.

           Parameters:
            record_json: The JSON representation of the record.
            csv_row['uri']: The URI of the record.
            fields: The fields, indicated by column headers.
            values: The values, indicated by column values.

           Note:
            Fields must match JSON keys in ArchivesSpace JSON response.
        '''
        for field, value in csv_row.items():
            if field != 'uri':
                record_json[field] = value
        return record_json, csv_row['uri']

    #also need to define the subrecord here.
    def update_subrecord_component(record_json: dict, csv_row: dict) -> tuple[dict, str]:
        '''Updates a nested field in a top-level record.

           Parameters:
            record_json: The JSON representation of the record.
            csv_row['uri']: The URI of the record.
            csv_row['updated_text']: The updated value.
            subrecord: The subrecord type.
            component: The subrecord component type.
        '''
        for item in record_json[subrecord]:
                item[component] = csv_row['updated_text']
        return record_json, csv_row['uri']

    #also need to define the subrecord here...
    def update_subrecord_components(record_json: dict, csv_row: dict) -> tuple[dict, str]:
        '''Updates nested fields in a top-level record.

           Parameters:
            record_json: The JSON representation of the record.
            csv_row['uri']: The URI of the record.
            fields: The fields, indicated by column headers.
            values: The values, indicated by column values.

           Note:
            Fields must match JSON keys in ArchivesSpace JSON response.

           Todo:
            See if this works? Might need to specify component type.
        '''
        for field, value in csv_row.items():
            if field != 'uri':
                for item in record_json[subrecord]:
                    item[field] = value
        return record_json, csv_row['uri']

    def update_record_pub_status(record_json: dict, csv_row: dict) -> tuple[dict, str]:
        '''Updates publication status of top-level record.

           Parameters:
            record_json: The JSON representation of the record.
            csv_row['uri']: The URI of the record.
            csv_row['updated_status']: The updated publication status, '1' for publish, '0' for unpublish.
        '''
        if csv_row['updated_status'] == '1':
            record_json['publish'] = True
        elif csv_row['updated_status'] == '0':
            record_json['publish'] = False
        return record_json, csv_row['uri']

    #if the subnote is also unpublished will need to fix that as well
    def update_note_pub_status(record_json: dict, csv_row: dict) -> tuple[dict, str]:
        '''Updates publication status of a note.

           Parameters:
            record_json: The JSOn representation of the parent record.
            csv_row['uri']: The URI of the parent record.
            csv_row['persistent_id']: The persistent ID of the note.
            csv_row['updated_status']: The updated status. '1' is publish, '0' is unpublish

           Todo:
            also need to change pub status of sub-notes...
        '''
        for note in record_json['notes']:
            if note['persistent_id'] == csv_row['persistent_id']:
                if csv_row['updated_status'] == '1':
                    note['publish'] = True
                elif csv_row['updated_status'] == '0':
                    note['publish'] = False
        return record_json, csv_row['uri']

    def update_authority_id(record_json: dict, csv_row: dict) -> tuple[dict, str]:
        '''Updates a name record with a new authority ID

           Parameters:
            record_json: The JSON representation of the agent record.
            csv_row['uri']: The URI of the agent_record
            csv_row['authority_id']: The authority ID to add to the agent record.
        '''
        for name in record_json['names']:
            if name.get('is_display_name') == True:
                name['authority_id'] = csv_row['authority_id']
        return record_json, csv_row['uri']

    def update_names(record_json: dict, csv_row: dict) -> tuple[dict, str]:
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
        return record_json, csv_row['uri']

    def update_sources_auth_ids(record_json: dict, csv_row: dict) -> tuple[dict, str]:
        '''Updates an agent record with a source value of 'local' and removes vendor-added
           authority ID codes. Used for agents and subjects remediation project.

           Parameters:
            record_json: The JSON representation of the record.
            csv_row['uri']: The URI of the agent record.
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
        return record_json, csv_row['uri']

    #so, for some reason I was able to do this - but deleting the whole instance will not work
    def delete_subcontainers(record_json: dict, csv_row: dict) -> tuple[dict, str]:
        '''Deletes a sub_container subrecord in an instance subrecord.

           Parameters:
            record_json: The JSON representation of the parent record.
            csv_row['uri']: The URI of the parent record.
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
        return record_json, csv_row['uri']

    def delete_notes(record_json: dict, csv_row: dict) -> tuple[dict, str]:
        '''Deletes a note subrecord in a descriptive record.

           Parameters:
            record_json: The JSON representation of the parent record.
            csv_row['uri']: The URI of the parent record.
            csv_row['persistent_id']: The persistent ID of the note to delete.
        '''
        for note in record_json['notes']:
            if note.get('persistent_id') == csv_row['persistent_id']:
                note.clear()
        return record_json, csv_row['uri']

    def delete_external_document(record_json: dict, csv_row: dict) -> tuple[dict, str]:
        '''Deletes an external document subrecord.

           Parameters:
            record_json: The JSON representation of the parent record.
            csv_row['uri']: The URI of the parent record.
            csv_row['link_to_delete']: The file location of the external document to delete
        '''
        for external_document in record_json['external_documents']:
            if external_document.get('location') == csv_row['link_to_delete']:
                external_document.clear()
        return record_json, csv_row['uri']

    def delete_rights_restriction(record_json: dict, csv_row: dict) -> tuple[dict, str]:
        '''Deletes a local access restriction in an accessrestrict note.

           Parameters:
            record_json: The JSON representation of the parent record.
            csv_row['uri']: The URI of the parent record.
            csv_row['persistent_id']: The persistent ID of the parent accessrestrict note.
        '''
        for note in record_json['notes']:
            if note['persistent_id'] == csv_row['persistent_id']:
                if 'rights_restriction' in note:
                    del note['rights_restriction']
        return record_json, csv_row['uri']

    def get_series(record_json: dict, csv_row: dict) -> tuple[dict, dict]:
        '''Gets a list of series-level ancestors for a list of URIs.

           Parameters:
            record_json: the JSON representation of the record.
            csv_row['uri']: The URI of the record to search
           
           Usage
            ::

              >>> csv_row = {'uri': '/repositories/2/archival_objects/5'}
              >>> record_json, csv_row = get_series(record_json, csv_row)
              >>> print(csv_row)
              {'uri': '/repositories/2/archival_objects/5', 'series': '/repositories/2/archival_objects/6'}
        '''
        for ancestor in record_json.get('ancestors'):
            if ancestor['level'] == 'series':
                csv_row.append(ancestor.get('ref'))
        return record_json, csv_row


    # -------------------------------------------------------------------------------------------------------------

    # Extras, unfinished, needs work

    #def update_subrecord_pub_status(record_json: dict, csv_row: dict) -> tuple[dict, str]:
    #     '''Updates publication status of subrecord.

    #        Parameters:
    #         record_json: The JSON representation of the parent record.
    #         csv_row['uri']: The URI of the parent record.
    #         csv_row['updated_status']: The updated publication status, '1' for publish, '0' for unpublish.
    #         subrecord: The subrecord type.

    #         Todo:
    #          Need to add an arg here?
    #     '''
    #     pass

    #def create_classification_scheme(csv_row: dict) -> tuple[dict, str]:
        '''Combines the create_classification and create_classification_term functions to create a multi-level
           classifcation scheme.

           Parameters:
            csv_row
        '''

    # def create_ordered_list(record_json, csv_row):
    #     '''Creates a ordered list note and links it to a descriptive record.
    #
    #        Parameters:
    #         record_json: The JSON representation of the parent record.
    #         csv_row['uri']: The URI of the parent record.
    #         csv_row['note_string']: The note text.
    #         csv_row['note_type']: The note type, i.e. accessrestrict
    #     '''
    #   return {'jsonmodel_type': 'note_multipart',
    #           'label': label_text,
    #           'type': 'odd',
    #           'publish': True,
    #           'subnotes': [{'items': index_list,
    #                       'jsonmodel_type': 'note_orderedlist',
    #                       'publish': True}]}

    # def create_ms_135_archival_objects(csv_row: dict) -> tuple[dict, str]:
        '''Creates archival object records for MS 135 reconciliation project

           Parameters:
            csv_row['tc_uri']: The URI of the linked container
            csv_row['type_2']: The child instance type (i.e. folder)
            csv_row['indicator_2']: The child indicator
            csv_row['title']: The archival_object title
            csv_row['date_expression']: The date expression
            csv_row['date_begin']: The begin date
            csv_row['date_end']: The end date
            csv_row['date_type']: The date type

           Other Parameters:
            csv_row['parent_uri']: The URI of the parent archival object

        '''
        # new_ao = {'jsonmodel_type': 'archival_object', 'title': csv_row['title'], 'level': 'file', 'publish': True,
        #             'dates': [{'jsonmodel_type': 'date', 'expression': csv_row['date_expression'],
        #                         'begin': csv_row['date_begin'], 'end': csv_row['date_end'],
        #                         'date_type': csv_row['date_type'], 'label': 'creation'}],
        #             'instances': [{'jsonmodel_type': 'instance', 'instance_type': 'mixed_materials',
        #                 'sub_container': {'jsonmodel_type': 'sub_container',
        #                                   'type_2': csv_row['type_2'],
        #                                   'indicator_2': csv_row['indicator_2'],
        #                                   'top_container': {'ref': csv_row['tc_uri']}}}],
        #             'parent': {'ref': csv_row['parent_uri']},
        #             'resource': {'ref': '/repositories/12/resources/4814'},
        #             'repository': {'ref': '/repositories/12'}}
        # #if just an empty string delete the key, otherwise the job will fail. Better way to do this?
        # if csv_row.get('parent_uri') in ('', None):
        #     del new_ao['parent']
        # return new_ao, '/repositories/12/archival_objects'

    # def update_glad_wp_access_notes(record_json, csv_row):
    #     '''Updates a multipart access note, removing the free text.
    #
    #        Parameters:
    #         record_json: The JSON representation of the parent record.
    #         csv_row['uri']: The URI of the parent record.
    #         csv_row['persistent_id']: The persistent ID of the existing note
    #     '''
    #     for note in record_json['notes']:
    #         if note['persistent_id'] == csv_row['persistent_id']:
    #             note['subnotes'][0]['content'] = ""

    #def delete_instances(record_json: dict, csv_row: dict) -> tuple[dict, str]:
        '''Deletes an instance.

           Parameters:
            record_json: The JSON representation of the parent record.
            csv_row['uri']: The URI of the parent record.

           Todo:
            check if this can be extracted to all subrecords. Make sure to use the .clear() method
        '''

    #def delete_enumeration_value():
        '''Suppresses an enumeration value.

           Parameters:
            csv_row['uri']: The URI of the enumeration value
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

    # def get_agents(agent_json, csv_row) -> tuple[dict, str]:
    #     '''Retrieves data about agents.

    #        Parameters:
    #         agent_json: The JSON representation of the agent rexcord.
    #         csv_row['uri']: The URI of the agent to search.
    #     '''
    #     data = []
    #     if 'agent_type' in agent_json:
    #         data.append(agent_json['agent_type'])
    #     else:
    #         data.append('no_agent_type')
    #     if 'create_time' in agent_json:
    #         data.append(agent_json['create_time'])
    #     else:
    #         data.append('no_create_time')
    #     if 'created_by' in agent_json:
    #         data.append(agent_json['created_by'])
    #     else:
    #         data.append('no_created_by')
    #     if 'display_name'in agent_json:
    #         if 'authority_id' in agent_json['display_name']:
    #             data.append(agent_json['display_name']['authority_id'])
    #         else:
    #             data.append('no_authority_id')
    #         if 'sort_name' in agent_json['display_name']:
    #             data.append(agent_json['display_name']['sort_name'])
    #             print(agent_json['display_name']['sort_name'])
    #         else:
    #             data.append('no_sort_name')
    #         if 'primary_name' in agent_json['display_name']:
    #             data.append(agent_json['display_name']['primary_name'])
    #         else:
    #             data.append('no_primary_name')
    #         if 'corporate_entities' in uri:
    #             if 'subordinate_name_1' in agent_json['display_name']:
    #                 data.append(agent_json['display_name']['subordinate_name_1'])
    #             else:
    #                 data.append('no_subordinate_name')
    #         if 'people' in uri:
    #             if 'rest_of_name' in agent_json['display_name']:
    #                 data.append(agent_json['display_name']['rest_of_name'])
    #             else:
    #                 data.append('no_rest_of_name')
    #         if 'families' in uri:
    #             data.append('family_name')
    #         if 'dates' in agent_json['display_name']:
    #             data.append(agent_json['display_name']['dates'])
    #         else:
    #             data.append('no_dates')
    #         if 'source' in agent_json['display_name']:
    #             data.append(agent_json['display_name']['source'])
    #         else:
    #             data.append('no_source')
    #         if 'qualifier' in agent_json['display_name']:
    #             data.append(agent_json['display_name']['qualifier'])
    #         else:
    #             data.append('no_qualifier')
    #     else:
    #         data.append('no_display_name_')
    #     if 'is_linked_to_published_record' in agent_json:
    #         data.append(agent_json['is_linked_to_published_record'])
    #     else:
    #         data.append('no_is_linked_to_pub_rec')
    #     if 'linked_agent_roles' in agent_json:
    #         data.append(agent_json['linked_agent_roles'])
    #     else:
    #         data.append('no_linked_agent_roles')
    #     if 'title' in agent_json:
    #         data.append(agent_json['title'])
    #     else:
    #         data.append('no_title')
    #     if 'is_linked_to_record' in agent_json:
    #         data.append(agent_json['is_linked_to_record'])
    #     else:
    #         data.append('no_link_to_record')
    #     if 'used_within_repositories' in agent_json:
    #         data.append(agent_json['used_within_repositories'])
    #     else:
    #         data.append('not_used_within_repos')
    #     if 'uri' in agent_json:
    #         data.append(agent_json['uri'])
    #     else:
    #         data.append('no_uri')
    #     if 'dates_of_existence' in agent_json:
    #         data.append(agent_json['dates_of_existence'])
    #     else:
    #         data.append('no_dates_of_existence')
    #     if 'agent_contacts' in agent_json:
    #         data.append(agent_json['agent_contacts'])
    #     else:
    #         data.append('no_contact_info')
    #     if 'notes' in agent_json:
    #         data.append(agent_json['notes'])
    #     else:
    #         data.append('no_notes')
    #     return data

    #def get_subjects(subject_json, csv_row) -> tuple[dict, str]:
        '''Retrieves data about subjects.

           Parameters:
            subject_json: The JSON representation of the subject record.
            csv_row['uri']: The URI of the subject to search.
        '''
        # terms = []
        # if 'title' in subject_json:
        #     csv_row.append(subject_json['title'])
        # else:
        #     csv_row.append('NO_VALUE')
        # if 'authority_id' in subject_json:
        #     csv_row.append(subject_json['authority_id'])
        # else:
        #     csv_row.append('NO_VALUE')
        # if 'source' in subject_json:
        #     csv_row.append(subject_json['source'])
        # else:
        #     csv_row.append('NO_VALUE')
        # if 'is_linked_to_published_record' in subject_json:
        #     csv_row.append(subject_json['is_linked_to_published_record'])
        # else:
        #     csv_row.append('NO_VALUE')
        # if 'terms' in subject_json:
        #     for term in subject_json['terms']:
        #         terms.append([term['term'], term['term_type']])
        #     csv_row.append(terms)
        # else:
        #     csv_row.append('NO_VALUE')
        # if 'used_within_repositories' in subject_json:
        #     csv_row.append(subject_json['used_within_repositories'])
        # else:
        #     csv_row.append('NO_VALUE')
        # if 'created_by' in subject_json:
        #     csv_row.append(subject_json['created_by'])
        # else:
        #     csv_row.append('NO_VALUE')
        # return csv_row

def main():
    aspace_conn = ASpaceConnection.from_dict('as_tools_config.yml')
    as_json = ASpaceRequests(aspace_conn)
    as_json.get_tree()

if __name__ == "__main__":
    main()
