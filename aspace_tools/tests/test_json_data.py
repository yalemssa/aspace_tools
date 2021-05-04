#!/usr/bin/python3

#import pytest
import json
import os
from collections import defaultdict

'''Test suite for aspace-tools

1.) Create your inputs
2.) Execute the code, capturing the output
3.) Compare the output with an expected result

Make a folder called 'fixtures' and store some test data - should have an example
for most top-level objects. Try isolating all possible GET requests in API docs
and call each of those to get some sample data.
'''


# this is where the validations live: https://github.com/archivesspace/archivesspace/blob/ae5c60ca9376d9ee83ad0d561a5bcfbdd2467894/common/validations.rb
#will eventually need to convert some of the ruby remnants - i.e. JSONModel(:boolean_query) object
#i have a reg ex which retrieves all of those in the templates.py file
#this should help me get a required fields thing going too....

#@pytest.fixture - will use this eventually
def aspace_schema():
    #this only works if I'm in the tests directory when running this
    return json.load(open(os.path.join(os.path.dirname(os.getcwd()), 'fixtures/schemas.json'), 'r', encoding='utf-8'))

def aspace_json_checker(schema):
    '''This function returns a list of required properties for the given schema
    To-Do: add type-checking for required fields
           add checks for required fields in subrecords - this could be done by
           checking if the dicts with ifmissing keys and type 'object' or 'array'
           (ref or subrecord)
    '''
    return {property: value['type'] for property, value in schema['properties'].items() if 'ifmissing' in value}

#this should also be a fixture
def compile_validations(schemas):
    validation_checks = {}
    for schema_name, schema_value in schemas.items():
        validations = None
        required_fields_dict = aspace_json_checker(schema_value)
        if 'validations' in schema_value:
            validations = schema_value['validations']
        validation_checks[schema_name] = {'required_fields': required_fields_dict, 'validations': validations}
    return validation_checks


def aspace_type_checker(schema):
    '''This function will test the type of each entry'''
    pass

def test_create_objects(test_object, validations):
    '''TODO: take the validation checker and parse it into an actual validation'''
    #check if the keys of the ao_validations['required_fields']
    missing_fields = [key for key in ao_validations.keys() if key not in test_object]
    if validations['validations'] is not None:
        for validation in validations['validations']:
            pass
