#!/usr/bin/python3
#~/anaconda3/bin/python

'''Test suite for aspace-tools

1.) Create your inputs
2.) Execute the code, capturing the output
3.) Compare the output with an expected result


Make a folder called 'fixtures' and store some test data - should have an example
for most top-level objects. Try isolating all possible GET requests in API docs
and call each of those to get some sample data.
'''

import sys

import requests
import responses

import crud
import json_data
import queries

import aspace_tools_logging as atl

sample_data_path = 'fixtures'

def test_():
    pass

logger = atl.logging.getLogger(__name__)
