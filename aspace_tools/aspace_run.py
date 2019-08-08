#!/usr/bin/python3
#~/anaconda3/bin/python

import traceback

from utilities import dbssh
from utilities import utilities as u

from . import json_data as jd
from . import queries as qs
from . import crud as c
from . import aspace_tools_logging as atl

'''
This file contains three functions which provide the scaffolding for interacting
with the ArchivesSpace API and MySQL database.

CRUD actions which are called by the call_api function are stored in the crud.py
file. CRUD functions include create_data, update_data, etc.

Todo:

    Add options for database query outputs - outfile, generator, list, DF, etc.

    Command line interface in main.py (rename??) - in progress
    Add variables to doc sctrings in json data, queries, etc. - in progress
    Do I need to import the login function here. Can I just import that function?
    I have been thinking about using the .apply function in conjunction with
    the json functionality of pandas for this
    use something to flatten the nested JSON
    use an error logging function to wrap the try/except
    -integrate update_microfilm.py into this process
'''

logger = atl.logging.getLogger(__name__)

@atl.as_tools_logger(logger)
def run_db_query(dbconn, query_func, outfile=None):
    '''Runs a single query against the ArchivesSpace database.

       Parameters:
        dbconn: The database connection
        query_func: The query to run.

       Todo:
        make sure that there is an outfile in the config file to store query data.
        Have the outfile be a default arg that can set if don't want to just return
        a generator or whatever.
    '''
    return (dbconn.run_query_list(query_func))

@atl.as_tools_logger(logger)
def run_db_queries(dbconn, csvfile, query_func):
    '''Runs multiple queries against the ArchivesSpace database.

       Parameters:
        dbconn: The database connection.
        csvfile: The CSV file containing query variables.
        query_func: The query to run. Passed in from queries.py

       Todo:
        Also need to determine whether running the run_query_list function  is the best approach.
        Add a thing so I can run a single query on the command line...
        This works as it should. Formulates the f-string query and runs it, returning a generator
        of lists (right?). From here can process the output in any way you like - can write to output file or do any additional processing
        MUST CLOSE THE DB CONNECTION!
    '''
    return (dbconn.run_query_list(query_func(row)) for row in csvfile)

@atl.as_tools_logger(logger)
def exception_handler(msg, type):
    print(f'Error on row {i}')
    print(msg)
    logger.error(f'Error on row {i}')
    if type == 'error':
        logger.error(record_json.get('error'))
    if type == 'exception':
        logger.exception('Error')

def append_uris_to_record_set(record_json):
    #Need to fix the CSV dict business now that everything is one...
    if 'uri' in record_json:
       pass
#        this don't work
#        Will also need to make sure that what's happening in this func is passed to record set - or do i need to return these things??
#        row.append(record_json['uri'])
#        record_set.append(row)


@atl.as_tools_logger(logger)
def call_api(api_url, headers, csvfile, dirpath=None, crud=None, json_data=None):
    '''This is the basic boilerplate loop structure for processing CSV files for use
       in ArchivesSpace API calls. Both the crud and json_data variables should be
       populated by functions from the json_data.py and crud.py files.

       Parameters:
        api_url: The URL for the ArchivesSpace API
        headers: ArchivesSpace authentication data
        csvfile: a CSV file in dictreader format
        dirpath: The path to the backup directory
        crud: The CRUD action to take. Populated by crud.py
        json_data: The JSON structure to formulate. Populated by json_data.py

       Todo:
        implement factory method?
    '''
    record_set = []
    for i, row in enumerate(csvfile, 1):
        try:
            if json_data != None:
                record_json = crud(api_url, headers, row, dirpath, json_data)
                if crud.__name__ == 'create_data':
                    append_uris_to_record_set(row, record_json, record_set)
                print(record_json)
            else:
                record_json = crud(api_url, headers, row, dirpath)
                print(record_json)
                if crud.__name__ == 'get_data':
                    record_set.append(record_json)
            if 'error' in record_json:
                exception_handler(record_json.get('error'), 'error')
        except Exception as exc:
            exception_handler(traceback.format_exc(), 'exception')
    if record_set:
        return record_set
