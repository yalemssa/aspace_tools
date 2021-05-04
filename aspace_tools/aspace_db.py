#!/usr/bin/python3
#~/anaconda3/bin/python

import sys
from pathlib import Path

#local package import
from utilities import utilities as u
from utilities import dbssh

from aspace_run import ASpaceDB
import aspace_tools_logging as atl

logger = atl.logging.getLogger(__name__)

@atl.as_tools_logger(logger)
def main(result=None):
    '''This is the primary command-line interface for interacting with the ArchivesSpace database via
       aspace_tools.

       Todo:
        add argument for run_db_query vs. run_db_queries???
    '''
    as_run = ASpaceDB()
    try:
        if len(sys.argv) > 1:
            result = as_run.run_db_queries(sys.argv[1])
        else:
            print('Error! Expected two arguments and got zero.')
    finally:
        as_run.dbconn.close_conn()
        return result

if __name__ == "__main__":
    main()
