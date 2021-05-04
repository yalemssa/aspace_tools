#!/usr/bin/python3
#~/anaconda3/bin/python

import sys
import argparse
from pathlib import Path

#local package import
from utilities import utilities as u

#imports from aspace-tools
import json_data as jd
import crud as c
from aspace_run import ASpaceRun, as_session

import aspace_tools_logging as atl

'''This is the main interface for setting program parameters and running functions that act on the ArchivesSpace API.

Todo:
    LOOK INTO OPTIONAL ARGUMENTS (are these positional, though?) Star arguments.
    NEED TO FIX THE ARGUMENTS TO MATCH WHAT IS IN THE README - the functions which don't have a json data as an arg
    won't work - DONE
    Want to do a command-line interface with the following arguments: csvfile OR csvdictfile; dirpath (optional, or set via the config file?)
    Need to be able to set option based on whether running DB queries or api updates.
    Probably need these in a separate function
    Can I do better than having to input api or db?
    ./main.py api update_data  update_record_component
    ./main.py db get_expiring_restrictions
    Ultimately want to change all of the json_data functions to use CSV dicts. Have
    already distinguished between the two in the db_or_api function, but have to
    implement in JSON data still...
    Will probably want an output csv option for the run queries stuff.
    Maybe have 2 main files, one for DB and one for api, then don’t have to have that extra argument
    -could also extract the update or create from .startswith on the first part of the argument
    -change the crud names from update_data to update, etc
    Can also add the sub record and record types as args for use in update sub record funcs
    Goal:
    ./aspace-api.py update_multipart note
    ./aspace-api.py update_subrecord_component date expression
    ./aspace-db.py get_access_notes
'''

logger = atl.logging.getLogger(__name__)

#this doesn't actually work right now
def get_crud(arg1):
    if arg1.startswith('update_'):
        pass
    #problem here though is that some of the creation things are subrecords, which don't use the same endpoint...
    if arg1.startswith('create_'):
        pass

@atl.as_tools_logger(logger)
def main(result=None):
    '''This is the primary command-line interface for interacting with the ArchivesSpace API via aspace_tools'''
    parser = argparse.ArgumentParser(description='Run ArchivesSpace API scripts from the command line')
    parser.add_argument('crud_func')
    parser.add_argument('--j', '--json_data')
    parser.add_argument('--s', '--session')
    parser.add_argument('--a', '--agent-type')
    options = parser.parse_args()
    if options.session is not None:
        as_run = ASpaceRun(sesh=options.session)
    else:
        as_run = ASpaceRun()
    print(f'Connected to: {as_run.api_url}')
    if options.agent_type is not None:
        if options.crud_func == 'merge_data':
            #need to change this so it will accept a record type as an argument.
            #result = as_run.call_api_looper()
            pass
        else:
            result = as_run.call_api_looper(crud_func=options.crud_func)
    #is this right?
    if options.json_data:
        #may need to instantiate json_data in aspace_run, and then pass it
        result = as_run.call_api_looper(crud_func=options.crud_func, json_func=options.json_data)
    else:
        #so for some reason main still ends up here at the end of the process. Not sure what I should do here...
        print(f"Error! Expected 1 or 2 arguments and got {len(sys.argv)}")
        print(sys.argv)
        print(len(sys.argv))
        #what to do here - this is masking errors and causing some problems - like when it finishes...
    print('Finished')
    return result

if __name__ == "__main__":
    main()
