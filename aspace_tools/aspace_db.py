#!/usr/bin/python3
#~/anaconda3/bin/python

import sys
from pathlib import Path

#local package import
from utilities import utilities as u
from utilities import dbssh

#imports from aspace-tools
from . import queries
from . import aspace_run
from . import aspace_tools_logging as atl

logger = atl.logging.getLogger(__name__)

@atl.as_tools_logger(logger)
def main(result=None):
    '''This is the primary interface for interacting with the ArchivesSpace database via
       aspace_tools.

       Todo:
        add argument for run_db_query vs. run_db_queries???
    '''
    home_dir = str(Path.home())
    config_file = u.get_config(cfg=home_dir + '/as_tools_config.yml')
    dirpath = u.setdirectory(config_file['backup_directory'])
    #what if just using the regular queries without f string functions?? Do like a csvfile=None variable?
    header_row, csvfile = u.opencsv(config_file['input_csv'])
    try:
        dbconn = dbssh.DBConn()
        if len(sys.argv) > 1:
            result = aspace_run.run_db_queries(dbconn, csvfile, getattr(queries, sys.argv[1]))
        else:
            print('Error! Expected two arguments and got zero.')
    finally:
        dbconn.close_conn()
        return result

if __name__ == "__main__":
    main()
