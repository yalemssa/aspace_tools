#!/usr/bin/python3
#~/anaconda3/bin/python

import re
import json
import pprint
import csv
import requests
from utilities import utilities as u

from . import aspace_tools_logging as atl

'''
A class for creating JSON and CSV templates from the ArchivesSpace schema.

Todo:
    -Go back through the few weird types that I skipped
    -What about the abstract stuff, inheritance, and the collection management fields?? ALSO double check notes
    -Also want to check in about the duplicate fields - i.e external id in the external id schema
    -Want to remove certain subrecords from top-level records which cannot be edited within the top level record - i.e. collection management
    -DONE: Make sure all editable fields are there and all read-only fields are not
    -DONE: Exclude the _ things
    -DONE: Maybe add True/False as the option for booleans
    -DONE: Put all of this back into a class so that I can re-use the variables without having to pass them to every single function
    -DONE: Isolate all the things that would cause infinite recursion (this is in the 'exclusions' list)
    -DONE: Make sure to add a proper type for the 'jsonmodel_type' field
    -DONE: Reorganize functions
'''

logger = atl.logging.getLogger(__name__)

class ASTemplates():
    def __init__(self):
        self.api_url, self.headers = u.login(url="https://devarchivesspace.library.yale.edu/api", username="amd243", password="FFmIjc5xLw")
        self.schemas = self.get_schemas()
        self.all_enumerations = self.get_dynamic_enums()
        self.schema_exclusions = [line.strip('\n') for line in open('/files/schema_exclusions.csv', encoding='utf-8')]
        self.property_exclusions = [line.strip('\n') for line in open('/files/property_exclusions.csv', encoding='utf-8')]
        self.jsonmodel_pattern = re.compile('(JSONModel)(\(:.*?\)\s)(uri|object|uri_or_object)')

    def get_schemas(self):
        schemas = requests.get(self.api_url + '/schemas', headers=self.headers).json()
        return schemas

    def get_schema(self, schema):
        schema = requests.get(self.api_url + '/schemas/' + schema, headers=self.headers).json()
        return schema

    def get_dynamic_enums(self):
        enums = requests.get(self.api_url + '/config/enumerations', headers=self.headers).json()
        return enums

    #be careful with the is vs == thing here...
    #can I write separate functions for each of the types??
    #will still need to deal with the things that are named the same...
    def parse_schema(self, schema_name, schema_definition):
        template_dict = {}
        #these are the recursion exclusions - currently hardcoded
        recursion_exclusions = ['classification_tree: children', 'digital_object_tree: children', 'resource_tree: children',
        'note_outline_level: create_time', 'note_outline_level: created_by', 'note_outline_level: items']
        for property_name, property_value in schema_definition['properties'].items():
            if property_name not in self.property_exclusions:
                #print('Working on: ' + str(schema_name + ': ' + str(property_name)))
                schema_name_field_name = schema_name + ': ' + property_name
                if schema_name_field_name in recursion_exclusions:
                    print(property_name)
                    print('In exclusion list')
                    continue
                if type(property_value['type']) is list:
                    #there are a few weird types here...deal with them later...these have more
                    #than one property type. Usually lock version but I think there are some others.
                    continue
                else:
                    #JSONMODELS
                    if self.jsonmodel_pattern.match(property_value['type']):
                        template_dict = self.process_jsonmodels(property_name, property_value, template_dict)
                    #SUBRECORDS - right??
                    elif property_value['type'] == 'array':
                        template_dict = self.process_arrays(schema_name, property_name, property_value, template_dict)
                    #USUALLY refs, plus some others
                    elif property_value['type'] == 'object':
                        template_dict = self.process_objects(property_name, property_value, template_dict)
                    elif property_value['type'] == 'string':
                        template_dict = self.process_strings(schema_name, property_name, property_value, template_dict)
                    #these are all dealt with in the same way I think
                    elif property_value['type'] in ['integer', 'boolean', 'date', 'date-time', 'number']:
                        template_dict = self.process_others(property_name, property_value, template_dict)
                    else:
                        print('Error! Value is not a recognized type.')
            else:
                print(schema_name, property_name)
        return template_dict

    def parse_schemas(self):
        #Don't need templates for these schemas, so skipping them.
        temp_dict = {}
        for schema_name, schema_definition in self.schemas.items():
            #check for a parent - but one that isn't "abstract" because those fields are the same
            # if 'parent' in schema_def:
            #     continue
            if schema_name not in self.schema_exclusions:
                template = self.parse_schema(schema_name, schema_definition)
                temp_dict[schema_name] = template
        return temp_dict

    def process_jsonmodels(self, property_name, property_value, template_dict):
        '''Can be either an object or URI. Refers to another schema or a reference
        to another object. i.e. date subrecords, location URIs. This should generally
        be working.'''
        if 'readonly' in property_value:
            '''These seem mostly to be things like 'representative image', 'display_name' fields'. I don't think
            for the most part these need to be part of the template, as they can't be updated. Should also check
            if there really are any things with subtype in the property value'''
            if 'subtype' in property_value:
                if property_value['subtype'] == 'ref':
                    #why is this here...why isn't this a parse refs function?? Is it because that's the same??
                    template_dict[property_name] = self.parse_jsonmodel(property_value['type'])
            else:
                pass
                #so it seems like there's maybe a fair amount of this???s
        else:
            '''This includes both objects and URI references'''
            template_dict[property_name] = self.parse_jsonmodel(property_value['type'])
        return template_dict

    def process_arrays(self, schema_name, property_name, property_value, template_dict):
        '''This is by far the most complicated part, as each of the other parts can be
        contained within it.'''
        #if there is more than one type...
        if type(property_value['items']['type']) is list:
            '''This includes: notes, related accessions, and related agents. For the most part
            the various types in the list are jsonmodel things. The exception is the note_outline_level,
            which is both an object and a string....interesting. I wonder if it would make more sense
            to treat that separately...I kind of already am.'''
            template_dict[property_name] = []
            #loop through each of the types and run the jsonmodel function.
            for property_type in property_value['items']['type']:
                '''WORK ON THIS - or really, fix the parse_jsonmodel function'''
                if self.jsonmodel_pattern.match(property_type['type']):
                    parsed_json = self.parse_jsonmodel(property_type['type'])
                    template_dict[property_name].append(parsed_json)
        else:
            #changed this to '=='
            if property_value['items']['type'] == 'object':
                #the first two variables should be different
                template_dict = self.process_objects(property_name, property_value['items'], template_dict)
            if property_value['items']['type'] == 'string':
                template_dict = self.process_strings(schema_name, property_name, property_value['items'], template_dict)
            #if it matches the object pattern
            '''WORK ON THIS - or really, fix the parse_jsonmodel function'''
            if self.jsonmodel_pattern.match(property_value['items']['type']):
                parsed_json = self.parse_jsonmodel(property_value['items']['type'])
                #again, can I just move this to the parse_jsonmodel function???
                template_dict[property_name] = [parsed_json]
        return template_dict

    def process_objects(self, property_name, property_value, template_dict):
        '''This function parses the properties of an ArchivesSpace schema which are of the
        type "object". These are typically refs, but not always. For now the only action
        that happens here is the assignment of references. This should work for both the top-level
        objects and the objects that are in the 'items' dictionary key of an array type object'''
        if 'properties' in property_value:
            if 'subtype' in property_value:
                #these are all refs I think
                template_dict[property_name] = self.parse_refs(property_name, property_value)
            else:
                '''Objects without subtype in the property value: location_batch:coordinate_1_range,
                location_batch:coordinate_2_range, location_batch:coordinate_3_range, note_citation:xlink

                I don't think I really need a template for location_batch, since the create locations
                function does the same thing. So can ignore those. But the xlink in the note note_citation
                is imortant. BUT I may need a whole other function just to deal with notes at some point,
                so for now may just pass on this and return later.
                '''
                pass
        else:
            '''Objects without properties: things like _resolved, permissions, etc. I think
            that these do not need to be included in any template. Most are explicity read only'''
            pass
        return template_dict

    def process_strings(self, schema_name, property_name, property_value, template_dict):
        '''This should work for both the top-level objects and the objects that are in the
        'items' dictionary key of an array type object
        '''
        if property_name == 'jsonmodel_type':
            template_dict[property_name] = schema_name
        #Do not want to include any read only fields in template
        else:
            if 'readonly' not in property_value:
                if 'enum' in property_value:
                    template_dict[property_name] = property_value['enum']
                if 'dynamic_enum' in property_value:
                    template_dict[property_name] = self.parse_enumerations(property_value['dynamic_enum'])
                else:
                    #these will be just regular top-level stringfields
                    template_dict[property_name] = None
        return template_dict

    def process_others(self, property_name, property_value, template_dict):
        '''This processes all the integers, dates, etc. There are no weird or nested
        structures here. Only including properties that are editable in the templates.'''
        #make sure this is correct, as in not missing something that should be there
        if 'readonly' not in property_value:
            if property_value['type'] == 'boolean':
                template_dict[property_name] = (True, False)
            else:
                template_dict[property_name] = None
        return template_dict

    def parse_jsonmodel(self, jsonmodel_type):
        '''Parses some JSONModels. May need more work, I dunno'''
        schema_name = jsonmodel_type[jsonmodel_type.find("(")+1:jsonmodel_type.find(")")][1:]
        if schema_name == 'repository':
            parsed_json = {'ref': '/repositories/:repo_id'}
        else:
            jsonmodel_schema = self.schemas[schema_name]
            if ') uri' in jsonmodel_type:
                parsed_json = {'ref': jsonmodel_schema['uri']}
            elif ') object' in jsonmodel_type:
                parsed_json = self.parse_schema(schema_name, jsonmodel_schema)
        return parsed_json

    def parse_refs(self, property_name, property_value):
        '''This seems like it also needs work. These references are ONLY found (and thus this function
        is only called) on properties with the type "object"'''
        #is this redundant?
        parsed_ref = None
        if 'ref' in property_value['properties']:
            if type(property_value['properties']['ref']['type']) is list:
                ref_list = []
                for ref in property_value['properties']['ref']['type']:
                    if type(ref) is str:
                        print('STRING CHECK')
                        print(ref)
                    else:
                        parsed_ref = self.parse_jsonmodel(ref['type'])
                        ref_list.append(parsed_ref)
                return ref_list
            else:
                if self.jsonmodel_pattern.match(property_value['properties']['ref']['type']):
                    parsed_ref = self.parse_jsonmodel(property_value['properties']['ref']['type'])
        else:
            if self.jsonmodel_pattern.match(property_value['ref']['type']):
                parsed_ref = self.parse_jsonmodel(property_value['ref']['type'])
        #seems like there is another option here that I am missing...
        return parsed_ref

    #this should be fine
    #but what about the static enums????
    def parse_enumerations(self, enumeration_name):
        enumeration_list = []
        for enumeration in self.all_enumerations:
            if enumeration['name'] == enumeration_name:
                for enumeration_value in enumeration['enumeration_values']:
                    enumeration_list.append(enumeration_value['value'])
        return enumeration_list

    def download_csv_template(self, jsontemplatedict):
        '''
        Goal is to create the JSON templates, and then convert those to CSV file that can
        be used to create either full finding aids/top level records, or to update subrecords
        in bulk

        Should really re-do this
        '''
        fileob = open('templates/' + jsontemplatedict['jsonmodel_type'] + '.csv', 'a', encoding='utf-8', newline='')
        csvout = csv.writer(fileob)
        subfield_list = []
        for key, value in jsontemplatedict.items():
            if type(value) is list:
                if len(value) > 0:
                    #should I just check the first one instead of looping through all?
                    if type(value[0]) is dict:
                        for item in value:
                            for k in item.keys():
                                subfield_list.append(key + '-' + k)
                    #only two options for lists, correct?
                    if type(value[0]) is not dict:
                        #this means that it's just a list of enums probably - right?? No other list formats
                        #do I need the check now that I removed the loop?
                        #check = jsontemplatedict['jsonmodel_type'] + '_' + key
                        if key not in subfield_list:
                            subfield_list.append(key)
                else:
                    print(key, value)
            else:
                subfield_list.append(key)
        csvout.writerow(subfield_list)
        fileob.close()
        return subfield_list

    #Wrapper loop to create all templates
    #Want to remove the schema name from the template header
    #also remove the jsonmodel type
    def download_csv_templates(self, jsontemplates):
        for template_key, template_value in jsontemplates.items():
            self.download_csv_template(template_value)

    #this downloads the JSON version of the template
    def download_json_templates(self, jsontemplates):
        for template_key, template_value in jsontemplates.items():
            outfile = open(str(template_key) + '.json', 'w', encoding='utf-8')
            json.dump(template_value, outfile, sort_keys = True, indent = 4)

@atl.as_tools_logger(logger)
def main():
    t = ASTemplates()
    as_templates = t.parse_schemas()
    #template_func = t.parse_schema('archival_object', t.schemas['archival_object'])
    #pprint.pprint(template_func)
    #pprint.pprint(as_templates)
    t.download_csv_templates(as_templates)

# if __name__ == "__main__":
#     main()
