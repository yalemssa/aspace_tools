#!/usr/bin/python3
#~/anaconda3/bin/python

'''This is the main interface for setting program parameters and running functions that act on the ArchivesSpace API.

Todo:
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

import sys
from pathlib import Path

#local package import
from utilities import utilities as u

#imports from aspace-tools
import json_data as jd
import crud as c
import aspace_run

import aspace_tools_logging as atl

logger = atl.logging.getLogger(__name__)

@atl.as_tools_logger(logger)
def main(result=None):
    '''This is the primary interface for interacting with the ArchivesSpace API via aspace-tools'''
    home_dir = str(Path.home())
    config_file = u.get_config(cfg=home_dir + '/as_tools_config.yml')
    dirpath = u.setdirectory(config_file['backup_directory'])
    csvfile = u.opencsvdict(config_file['input_csv'])
    if len(sys.argv) > 1:
        #action_selection = sys.argv[1]
        #do a .startswith('update_') here to find which CRUD function should be run? Would have to rename
        #some of the functions I think - since there are more than one updates
        api_url, headers = u.login(url=config_file['api_url'], username=config_file['api_username'], password=config_file['api_password'])
        print(f'Connected to: {api_url}')
        result = aspace_tools.call_api(api_url, headers, csvfile, dirpath=dirpath, crud=getattr(c, sys.argv[1]), json_data=getattr(jd, sys.argv[2]))
    else:
        print('Error! Expected two arguments and got zero.')
    return result

if __name__ == "__main__":
    main()
