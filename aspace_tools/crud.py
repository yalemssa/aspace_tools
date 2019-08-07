#!/usr/bin/python3
#~/anaconda3/bin/python

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

Todo:
    also need to make sure that merge_data variables like record type are accounted for in the main interface; right now it
    might be interpreted as a json_data variable which it is not; implement asnake.
'''

import json
import traceback
import requests
#import pandas as pd
#from asnake.client import ASnakeClient

from utilities import utilities as u #, dbssh
import aspace_tools_logging as atl

# client = ASnakeClient()
# auth = client.authorize()

#LOGGING
#INTERFACE TO SET VARIABLES FOR MAIN PROGRAM
#FOLDER FOR IMPLEMENTATIONS


# def write_output(result_data, output_file):
#     pass

logger = atl.logging.getLogger(__name__)

@atl.as_tools_logger(logger)
def update_data(api_url, headers, row, dirpath, json_data):
    '''Updates data via the ArchivesSpace API.

       Parameters:
        api_url: URL to the ArchivesSpace API
        headers: Authentication data returned by login function
        row['uri']: The URI of the record to update.
        dirpath: Path to the backup directory. Defined in as_tools_config.yml
        json_data: The json structure to use in the update.

       Returns:
        dict: The JSON response from the ArchivesSpace API.
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
    '''Updates the archival object parent and position of an archival object record.

       Parameters:
        api_url: URL to the ArchivesSpace API.
        headers: Authentication data returned by login function.
        row['child_uri']: The URI of the record to update.
        row['parent_uri']: The URI of the new parent.
        row['position']: The new position value.
        dirpath: Path to the backup directory. Defined in as_tools_config.yml

       Returns:
        dict: The JSON response from the ArchivesSpace API.
    '''
    record_json = requests.get(api_url + row['child_uri'], headers=headers).json()
    u.create_backups(dirpath, row['child_uri'], record_json)
    record_post = requests.post(api_url + row['child_uri'] + '/parent?parent=' + row['parent_uri'] + '&position=' + str(row['position']), headers=headers).json()
    return record_post

#double check this - not sure if I need to GET first - I didn't think so; also need to make sure that 'config' is part of the enum uri
@atl.as_tools_logger(logger)
def update_enum_position(api_url, headers, row):
    '''Updates the position of an enumeration value.

       Parameters:
        api_url: URL to the ArchivesSpace API.
        headers: Authentication data returned by login function.
        row['enum_uri']: The URI of the enumeration value to update.
        row['position']: The new position value.

       Returns:
        dict: The JSON response from the ArchivesSpace API.
    '''
    record_post = requests.post(api_url + row['enum_uri'] + '/position?position=' + row['position'], headers=headers.json())
    return record_post

@atl.as_tools_logger(logger)
def merge_data(api_url, headers, row, dirpath, record_type):
    '''Merges two records.

       NOTE: need to add another sys.argv value for this so can specify record type outside of CSV

       Parameters:
        api_url: URL to the ArchivesSpace API.
        headers: Authentication data returned by login function.
        row['target_uri']: The URI of the record to keep.
        row['victim_uri']: The URI of the record to merge.
        dirpath: Path to the backup directory. Defined in as_tools_config.yml
        record_type: The type of record to be merged.

       Returns:
        dict: The JSON response from the ArchivesSpace API.
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
    '''Performs a search via the ArchivesSpace API

       Parameters:
        api_url: URL to the ArchivesSpace API.
        headers: Authentication data returned by login function.
        search_string: The search to perform.

       Returns:
        dict: The JSON response from the ArchivesSpace API.
    '''
    pass

@atl.as_tools_logger(logger)
def search_container_profiles(api_url, headers, row):
    '''Searches container profiles by name. NOTE: make sure that I added the container lookup function that stores all containers.

       Parameters:
        api_url: URL to the ArchivesSpace API.
        headers: Authentication data returned by login function.
        row['container_profile']: The name of the container profile to search.

       Returns:
        dict: The JSON response from the ArchivesSpace API.
    '''
    search = requests.get(api_url + '/search?page=1&page_size=500&type[]=container_profile&q=title:' + row['container_profile'], headers=headers).json()
    return search

@atl.as_tools_logger(logger)
def create_data(api_url, headers, row, _, json_data):
    '''Creates new records via the ArchivesSpace API.

       Parameters:
        api_url: URL to the ArchivesSpace API.
        headers: Authentication data returned by login function.
        row: A row of a CSV file containing record creation data. Passed in via aspace_tools.py
        json_data: The json structure to use in the record creation process.

       Returns:
        dict: The JSON response from the ArchivesSpace API.
    '''
    record_json, endpoint = json_data(row)
    record_post = requests.post(api_url + endpoint, headers=headers, json=record_json).json()
    return record_post

@atl.as_tools_logger(logger)
def delete_data(api_url, headers, row, dirpath):
    '''Deletes records via the ArchivesSpace API.

       Parameters:
        api_url: URL to the ArchivesSpace API.
        headers: Authentication data returned by login function.
        row['uri']: The URI of the record to delete.
        dirpath: Path to the backup directory. Defined in as_tools_config.yml

       Returns:
        dict: The JSON response from the ArchivesSpace API.
    '''
    record_json = requests.get(api_url + row['uri'], headers=headers).json()
    u.create_backups(dirpath, row['uri'], record_json)
    record_delete = requests.delete(api_url + row['uri'], headers=headers).json()
    return record_delete

@atl.as_tools_logger(logger)
def get_nodes(api_url, headers, row):
    '''Gets a list of child URIs for an archival object record

       Parameters:
        api_url: URL to the ArchivesSpace API.
        headers: Authentication data returned by login function.
        row['resource_uri']: The URI of the parent resource
        row['ao_node_uri']: The URI of the parent archival object

       Returns:
        list: A list of child URIs, titles, and parent IDs.
    '''
    record_children = requests.get(api_url + row['resource_uri'] + '/tree/node?node_uri=' + row['ao_node_uri'], headers=headers).json()
    #this will return a list of child dicts - move this out to make more modules
    children = record_children['precomputed_waypoints'][row['ao_node_uri']]['0']
    child_list = [[child['uri'], child['title'], child['parent_id']]
                  for child in children]
    return child_list

@atl.as_tools_logger(logger)
def get_tree(api_url, headers, row):
    '''Gets a tree for a record.

       Parameters:
        api_url: URL to the ArchivesSpace API.
        headers: Authentication data returned by login function.
        row['uri']: The URI of the record.

       Returns:
        dict: The JSON response from the ArchivesSpace API.
    '''
    tree = requests.get(api_url + row['uri'] + '/tree', headers=headers).json()
    return tree

@atl.as_tools_logger(logger)
def get_extents(api_url, headers, row):
    '''Calculates extents for a set of resource records.

       Parameters:
        api_url: URL to the ArchivesSpace API.
        headers: Authentication data returned by login function.
        row['uri']: The URI of the resource to calculate.

       Returns:
        list: A list of record URIs, total extents, and extent units.
    '''
    extent_calculator = requests.get(api_url + '/extent_calculator?record_uri=' + row['uri'], headers=headers).json()
    extent_data = [row['uri'], extent_calculator['total_extent'], extent_calulator['units']]
    return extent_data

@atl.as_tools_logger(logger)
def get_data(api_url, headers, row):
    '''Retrieves JSON data from the ArchivesSpace API. NOTE: Want to flatten this to CSV with the pandas module (can flatten nested JSON)

       Parameters:
        api_url: URL to the ArchivesSpace API.
        headers: Authentication data returned by login function.
        row['uri']: The URI of the record to retrieve

       Returns:
        dict: The JSON response from the ArchivesSpace API.
    '''
    record_json = requests.get(api_url + uri, headers=headers).json()
    #add functions here to get particular data from JSON - see get_nodes
    #can add the different variations to the data structs file or create another one
    return record_json

@atl.as_tools_logger(logger)
def api_login(url=None, username=None, password=None):
    '''Logs into the ArchivesSpace API.

       Parameters:
        url: The URL to the ArchivesSpace API.
        username: The user's username.
        password: The user's password.

       Returns:
        dict: The JSON response from the ArchivesSpace API.
    '''
    try:
        if url is None and username is None and password is None:
            url = input('Please enter the ArchivesSpace API URL: ')
            username = input('Please enter your username: ')
            password = input('Please enter your password: ')
        auth = requests.post(url+'/users/'+username+'/login?password='+password).json()
        #if session object is returned then login was successful; if not it failed.
        if 'session' in auth:
            session = auth["session"]
            h = {'X-ArchivesSpace-Session':session, 'Content_Type': 'application/json'}
            print('Login successful!')
            logging.debug('Success!')
            return (url, h)
        else:
            print('Login failed! Check credentials and try again.')
            logging.debug('Login failed')
            logging.debug(auth.get('error'))
            #try again
            u, heads = login()
            return u, heads
    except:
        print('Login failed! Check credentials and try again!')
        logging.exception('Error: ')
        u, heads = login()
        return u, heads
