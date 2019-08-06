#!/usr/bin/python3
#~/anaconda3/bin/python

import traceback

from utilities import dbssh
from utilities import utilities as u

import json_data as jd
import queries as qs
import crud as c

import aspace_tools_logging as atl
logger = atl.logging.getLogger(__name__)

'''
TO-DO:

Command line interface in main.py (rename??) - in progress
Add variables to doc sctrings in json data, queries, etc. - in progress


This is the primary interface for the new apispace package. The two main functions for interacting with the database
and API are stored in this file. CRUD actions which are called by the call_api function are stored in the crud.py
file. CRUD functions include create_data, update_data, etc.

I have been thinking about using the .apply function in conjunction with
the json functionality of pandas for this
use something to flatten the nested JSON
use an error logging function to wrap the try/except
-integrate update_microfilm.py into this process

Do I need to import the login function here. Can I just import that function?

'''

@atl.as_tools_logger(logger)
def run_db_queries(dbconn, csvfile, query_func):
    '''This works as it should. Formulates the f-string query and runs it, returning a generator
    of lists (right?). From here can process the output in any way you like - can write to output file or do any additional processing

    Also need to determine whether running the run_query_list function  is the best approach.

    NOTE: to run a single query string from the queries.py file, just use the DBConn class in utilities.dbssh
    '''
    return (dbconn.run_query_list(query_func(row)) for row in csvfile)

#add a decorator for error handling here and remove the try/except statement
@atl.as_tools_logger(logger)
def call_api(api_url, headers, csvfile, dirpath=None, crud=None, json_data=None):
    '''This is the basic boilerplate loop structure for processing CSV files for use
    in ArchivesSpace API calls. Both the crud and json_data variables should be
    populated by functions from the json_data.py and crud.py files.

    To-Do: implement factory method?
    '''
    record_set = []
    for i, row in enumerate(csvfile, 1):
        try:
            if json_data != None:
                record_json = crud(api_url, headers, row, dirpath, json_data)
                #dNeed to fix the CSV dict business now that everything is one...
                #if crud.__name__ == 'create_data':
                #    if 'uri' in record_json:
                        #what happens when this is a CSV dict?? It breaks...
                #        row.append(record_json['uri'])
                #        record_set.append(row)
                print(record_json)
            else:
                record_json = crud(api_url, headers, row, dirpath)
                print(record_json)
                if crud.__name__ == 'get_data':
                    #only want this if getting data
                    record_set.append(record_json)
            #this applies to everything - though actually not necessary since printing everything to console anyway; but this will change
            if 'error' in record_json:
                print(f'Error on row {i}')
                print(record_json.get('error'))
                logger.error(f'Error on row {i}')
                logger.error(record_json.get('error'))
        except Exception as exc:
            print(f'Error on row {i}')
            print(traceback.format_exc())
            logger.error(f'Error on row {i}')
            logger.exception('Error')
    if record_set:
        return record_set
