#!/usr/bin/python3
#~/anaconda3/bin/python

import sys
from pathlib import Path

#local package import
from utilities import utilities as u

#imports from aspace-tools
from aspace_tools import json_data as jd
from aspace_tools import crud as c
from aspace_tools import aspace_run

from aspace_tools import aspace_tools_logging as atl

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

def get_crud(arg1):
    if arg1.startswith('update_'):
        pass
    #problem here though is that some of the creation things are subrecords, which don't use the same endpoint...
    if arg1.startswith('create_'):
        pass

@atl.as_tools_logger(logger)
def main(result=None):
    '''This is the primary interface for interacting with the ArchivesSpace API via aspace-tools'''
    home_dir = str(Path.home())
    config_file = u.get_config(cfg=home_dir + '/as_tools_config.yml')
    dirpath = u.setdirectory(config_file['backup_directory'])
    csvfile = u.opencsvdict(config_file['input_csv'])
    api_url, headers = u.login(url=config_file['api_url'], username=config_file['api_username'], password=config_file['api_password'])
    print(f'Connected to: {api_url}')
    if len(sys.argv) == 2:
        if sys.argv[1] == 'merge_data':
            pass
        else:
            result = aspace_tools.call_api(api_url, headers, csvfile, dirpath=dirpath, crud=getattr(c, sys.argv[1]))
    if len(sys.argv) == 3:
        result = aspace_tools.call_api(api_url, headers, csvfile, dirpath=dirpath, crud=getattr(c, sys.argv[1]), json_data=getattr(jd, sys.argv[2]))
    else:
        print(f"Error! Expected 1 or 2 arguments and got {len(sys.argv)}")
    return result

if __name__ == "__main__":
    main()
