#!/usr/bin/python3
#~/anaconda3/bin/python

import json
import traceback
import requests
#import pandas as pd
#from asnake.client import ASnakeClient

from utilities import utilities as u #, dbssh

import aspace_tools_logging as atl
logger = atl.logging.getLogger(__name__)


# client = ASnakeClient()
# auth = client.authorize()

#LOGGING
#INTERFACE TO SET VARIABLES FOR MAIN PROGRAM
#FOLDER FOR IMPLEMENTATIONS


# def write_output(result_data, output_file):
#     pass

'''
These functions represent various types of create, read, update, and delete actions
possible in the ArchivesSpace API. Some are generalized - i.e. the update_data, create_data,
and delete_data functions can all be used to perform said actions on any record.

The create_data and update_data functions call other functions which are stored in json_data.py
to formulate the JSON which is required for API data transmission.

All of the CRUD functions are themselves called by the functions in aspace_tools.py

Other functions are scoped to specific endpoints that are formatted somewhat differently or take
different parameters than the generalized functions. These include updating the parent and position
of an archival object and updating the position of an enumeration value, among others.

TODO: also need to make sure that merge_data variables like record type are accounted for in the main interface; right now it
might be interpreted as a json_data variable which it is not
'''
@atl.as_tools_logger(logger)
def update_data(api_url, headers, row, dirpath, json_data):
    '''Updates data via the ArchivesSpace API

       Parameters: uri
    '''
    #gets the JSON to update
    record_json = requests.get(api_url + row['uri'], headers=headers).json()
    #creates a backup of the original file
    u.create_backups(dirpath, row['uri'], record_json)
    #this modifies the JSON based on a particular JSON data structure defined by the user
    record_json = json_data(record_json, row)
    #this posts the JSON
    record_post = requests.post(api_url + row['uri'], headers=headers, json=record_json).json()
    return record_post

@atl.as_tools_logger(logger)
def update_parent(api_url, headers, row, dirpath):
    '''Updates the archival object parent and position of an archival object record

       Parameters: child_uri, parent_uri, position
    '''
    record_json = requests.get(api_url + row['child_uri'], headers=headers).json()
    u.create_backups(dirpath, row['child_uri'], record_json)
    record_post = requests.post(api_url + row['child_uri'] + '/parent?parent=' + row['parent_uri'] + '&position=' + str(row['position']), headers=headers).json()
    return record_post

#double check this - not sure if I need to GET first - I didn't think so; also need to make sure that 'config' is part of the enum uri
@atl.as_tools_logger(logger)
def update_enum_position(api_url, headers, row):
    '''Updates the position of an enumeration value

       Parameters: enum_uri, position
    '''
    record_post = requests.post(api_url + row['enum_uri'] + '/position?position=' + row['position'], headers=headers.json())
    return record_post

@atl.as_tools_logger(logger)
def merge_data(api_url, headers, row, dirpath, record_type):
    '''Merges two records

       Parameters: target_uri, victim_uri

       NOTE: need to add another sys.argv value for this so can specify record type outside of CSV
    '''
    victim_backup = requests.get(api_url + row['victim_uri'], headers=headers).json()
    u.create_backups(dirpath, row['victim_uri'], victim_backup)
    #I want to add a check here to make sure contact info, etc. is not present...check merge_records.py for ex
    merge_json = {'target': {'ref': row['target_uri']},
                  'victims': [{'ref': row['victim_uri']}],
                  'jsonmodel_type': 'merge_request'}
    merge_request = requests.post(api_url + '/merge_requests/' + str(record_type), headers=headers, json=merge_json).json()
    return merge_request

@atl.as_tools_logger(logger)
def search_data(api_url, headers, row):
    '''Performs a search via the ArchivesSpace API'''
    pass

@atl.as_tools_logger(logger)
def search_container_profiles(api_url, headers, row):
    '''Searches container profiles by name

       Parameters: container_profile

       NOTE: make sure that I added the container lookup function that stores all containers.
    '''
    search = requests.get(api_url + '/search?page=1&page_size=500&type[]=container_profile&q=title:' + row['container_profile'], headers=headers).json()
    return search

@atl.as_tools_logger(logger)
def create_data(api_url, headers, row, _, json_data):
    '''Creates new records via the ArchivesSpace API

       NOTE: The _ is a throwaway variable, but is necessary because it is used in the api_call function, where
       some CRUD actions use the dirpath variable'''
    record_json, endpoint = json_data(row)
    record_post = requests.post(api_url + endpoint, headers=headers, json=record_json).json()
    return record_post

@atl.as_tools_logger(logger)
def delete_data(api_url, headers, row, dirpath):
    '''Deletes records via the ArchivesSpace API'''
    record_json = requests.get(api_url + row['uri'], headers=headers).json()
    u.create_backups(dirpath, row['uri'], record_json)
    record_delete = requests.delete(api_url + row['uri'], headers=headers).json()
    return record_delete

@atl.as_tools_logger(logger)
def get_nodes(api_url, headers, row):
    '''Gets a list of child URIs for an archival object record

       Parameters: resource_uri, ao_node_uri
    '''
    record_children = requests.get(api_url + row['resource_uri'] + '/tree/node?node_uri=' + row['ao_node_uri'], headers=headers).json()
    #this will return a list of child dicts - move this out to make more modules
    children = record_children['precomputed_waypoints'][row['ao_node_uri']]['0']
    child_list = [[child['uri'], child['title'], child['parent_id']]
                  for child in children]
    return child_list

@atl.as_tools_logger(logger)
def get_tree(api_url, headers, row):
    '''Gets a tree for a record

       Parameters: uri
    '''
    tree = requests.get(api_url + row['uri'] + '/tree', headers=headers).json()
    return tree

@atl.as_tools_logger(logger)
def get_extents(api_url, headers, row):
    '''Calculates extents for a set of resource records

       Parameters: uri
    '''
    extent_calculator = requests.get(api_url + '/extent_calculator?record_uri=' + row['uri'], headers=headers).json()
    extent_data = [row['uri'], extent_calculator['total_extent'], extent_calulator['units']]
    return extent_data

@atl.as_tools_logger(logger)
def get_data(api_url, headers, row):
    '''Retrieves JSON data from the ArchivesSpace API

       Parameters: uri

       NOTE: Want to flatten this to CSV with the pandas module
    '''
    record_json = requests.get(api_url + uri, headers=headers).json()
    #add functions here to get particular data from JSON - see get_nodes
    #can add the different variations to the data structs file or create another one
    return record_json

@atl.as_tools_logger(logger)
def api_login():
    '''Logs in to the ArchivesSpace API

       Parameters: url, username, password
    '''
    try:
        url = input('Please enter the ArchivesSpace API URL: ')
        username = input('Please enter your username: ')
        password = input('Please enter your password: ')
        auth = requests.post(url+'/users/'+username+'/login?password='+password).json()
        #if session object is returned then login was successful; if not it failed.
        if 'session' in auth:
            session = auth["session"]
            h = {'X-ArchivesSpace-Session':session, 'Content_Type': 'application/json'}
            print('Login successful!')
            return (url, h)
        else:
            print('Login failed! Check credentials and try again')
            u, heads = login()
            return u, heads
    except:
        print('Login failed! Check credentials and try again!')
        u, heads = login()
        return u, heads
