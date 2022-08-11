#!/usr/bin/python3
#~/anaconda3/bin/python

import json
import traceback
import requests
import pprint
from pathlib import Path
import subprocess
from lxml import etree
from io import StringIO
import sys


import script_tools

import json_data


class ASCrud():

    def __init__(self, config_file, sesh):

        #self.config_file = get_config(cfg=str(Path.home()) + '/as_tools_config.yml')
        self.config_file = config_file
        self.api_url = self.config_file['api_url']
        self.username = self.config_file['api_username']
        self.password = config_file['api_password']
        self.dirpath = config_file['backup_directory']
        #use this to transform the original XML. Need to call Saxon 9 because lxml does not support XSLT 2.0 transformations
        self.ead_3_transformation = 'data/yale.aspace_v2_to_yale_ead3.xsl'
        #context manager?
        self.output_file = open(config_file['output_file'].strip(), 'a', encoding='utf8')
        #self.ead_3_transformation = requests.get("https://raw.githubusercontent.com/YaleArchivesSpace/EAD3-to-PDF-UA/master/xslt-to-update-the-ASpace-export/yale.aspace_v2_to_yale_ead3.xsl").text
        self.ead_3_schema = self.prep_schema_for_validation()
#        self.json_data = json_data
        self.sesh = sesh

    #@atl.as_tools_logger(logger)
    def update_data(self, row, json_func):
        '''Updates data via the ArchivesSpace API.

           Parameters:
            row['uri']: The URI of the record to update.
            dirpath: Path to the backup directory. Defined in as_tools_config.yml
            json_data: The json structure to use in the update.

           Returns:
            dict: The JSON response from the ArchivesSpace API.
        '''
        #gets the JSON to update
        record_json = self.sesh.get(self.api_url + row['uri']).json()
        #creates a backup of the original file
        script_tools.create_backups(self.dirpath, row['uri'], record_json)
        #this modifies the JSON based on a particular JSON data structure defined by the user
        record_json = json_func(record_json, row)
        #this posts the JSON
        record_post = self.sesh.post(self.api_url + row['uri'], json=record_json).json()
        print(record_post)
        return record_post

    #@atl.as_tools_logger(logger)
    def search_data(self, row):
        '''Performs a search via the ArchivesSpace API

           Parameters:
            search_string: The search to perform.

           Returns:
            dict: The JSON response from the ArchivesSpace API.
        '''
        pass

    #@atl.as_tools_logger(logger)
    def search_container_profiles(self, row):
        '''Searches container profiles by name. NOTE: make sure that I added the container lookup function that stores all containers.

           Parameters:
            row['container_profile']: The name of the container profile to search.

           Returns:
            dict: The JSON response from the ArchivesSpace API.
        '''
        search = self.sesh.get(self.api_url + '/search?page=1&page_size=500&type[]=container_profile&q=title:' + row['container_profile']).json()
        return search

    #@atl.as_tools_logger(logger)
    def create_data(self, row, json_func):
        '''Creates new records via the ArchivesSpace API.

           Parameters:
            row: A row of a CSV file containing record creation data. Passed in via aspace_tools.py
            json_data: The json structure to use in the record creation process.

           Returns:
            dict: The JSON response from the ArchivesSpace API.
        '''
        record_json, endpoint = json_func(row)
        record_post = self.sesh.post(self.api_url + endpoint, json=record_json).json()
        return record_post

    #@atl.as_tools_logger(logger)
    def delete_data(self, row):
        '''Deletes records via the ArchivesSpace API.

           Parameters:
            row['uri']: The URI of the record to delete.
            dirpath: Path to the backup directory. Defined in as_tools_config.yml

           Returns:
            dict: The JSON response from the ArchivesSpace API.
        '''
        record_json = self.sesh.get(self.api_url + row['uri']).json()
        script_tools.create_backups(self.dirpath, row['uri'], record_json)
        record_delete = self.sesh.delete(self.api_url + row['uri']).json()
        return record_delete

    #@atl.as_tools_logger(logger)
    def get_nodes(self, row):
        '''Gets a list of child URIs for an archival object record

           Parameters:
            row['resource_uri']: The URI of the parent resource
            row['ao_node_uri']: The URI of the parent archival object

           Returns:
            list: A list of child URIs, titles, and parent IDs.

           Note:
            this only retrieves the immediate children of the parent, not any of their children.
        '''
        record_children = self.sesh.get(self.api_url + row['resource_uri'] + '/tree/node?node_uri=' + row['ao_node_uri']).json()
        pprint.pprint(record_children)
        #this will return a list of child dicts - move this out to make more modules
        children = record_children['precomputed_waypoints'][row['ao_node_uri']]['0']
        child_list = [[child['uri'], child['title'], child['parent_id']]
                      for child in children]
        pprint.pprint(child_list)
        return child_list

    #flatten the output into a list
    #also maybe create a callback where you can input a sigle resource id?
    #@atl.as_tools_logger(logger)
    def get_tree(self, row):
        '''Gets a tree for a record.

           Parameters:
            row['uri']: The URI of the record.

           Returns:
            dict: The JSON response from the ArchivesSpace API.
        '''
        tree = self.sesh.get(self.api_url + row['uri'] + '/tree').json()
        pprint.pprint(tree)
        return tree

    #THIS ISN"T RIGHT - NEEDS A NODE ID
    def get_node_from_root(self, row):
        '''Gets a tree path from the root record to archival objects.

           NOTE: find out how this is different from the regular get tree endpoint

           Parameters:
            row['uri']: The URI of the resource record.
            row['node_id']: The id of the archival object node

           Returns:
            dict: The JSON response from the ArchivesSpace API.
        '''
        int_node_id = int(row['node_id'])
        print(int_node_id)
        print(type(int_node_id))
        tree_from_node = self.sesh.get(f"{self.api_url}{row['uri']}/tree/node_from_root?node_ids={int_node_id}").json()
        pprint.pprint(tree_from_node)
        return tree_from_node

    #@atl.as_tools_logger(logger)
    def get_extents(self, row):
        '''Calculates extents for a set of resource records.

           Parameters:
            row['uri']: The URI of the resource to calculate.

           Returns:
            list: A list of record URIs, total extents, and extent units.
        '''
        extent_calculator = self.sesh.get(self.api_url + '/extent_calculator?record_uri=' + row['uri']).json()
        extent_data = [row['uri'], extent_calculator['total_extent'], extent_calulator['units']]
        return extent_data

    #@atl.as_tools_logger(logger)
    def get_json_data(self, row):
        '''Retrieves JSON data from the ArchivesSpace API. NOTE: Want to flatten this to CSV with the pandas module (can flatten nested JSON)

           Parameters:
            row['uri']: The URI of the record to retrieve

           Returns:
            dict: The JSON response from the ArchivesSpace API.
        '''
        record_json = self.sesh.get(self.api_url + row['uri']).json()
        #add functions here to get particular data from JSON - see get_nodes
        #can add the different variations to the data structs file or create another one
        return record_json

    def get_required_fields(self, row):
        '''Retrieves required fields for a record type from the ArchivesSpace API.

           Parameters:
            row['uri']: The URI of the repository
            row['record_type']: The type of the record to retrieve

           Returns:
            dict: The JSON response from the ArchivesSpace API.
        '''
        required_fields = self.sesh.get(self.api_url + row['uri'] + '/required_fields/' + row['record_type']).json()
        pprint.pprint(required_fields)
        return required_fields

    def get_linked_top_containers(self, row):
        '''Retrieves containers linked to a given resource from the ArchivesSpace API.

           Parameters:
            row['uri']: The URI of the record to retrieve

           Returns:
            dict: The JSON response from the ArchivesSpace API.
        '''
        pass


    ### EVERYTHING BELOW THIS IS EAD RELATED

    def export_ead(self, row, ead3=False, get_ead=None):
        '''Exports EAD files using a list of resource IDs as input.

           Parameters:
            row['resource_id']: The ID of the resource
            row['repo_id']: The ID of the repository

           Returns:
            str: A string representation of the EAD response from the ArchivesSpace API.
        '''
        repo_id = row['repo_id']
        resource_id = row['resource_id']
        print(f'Exporting {resource_id}')
        if ead3 == True:
            get_ead = self.sesh.get(f"{self.api_url}/repositories/{repo_id}/resource_descriptions/{resource_id.strip()}.xml?include_unpublished=true&ead3=true", stream=True).text
        elif ead3 == False:
            get_ead = self.sesh.get(f"{self.api_url}/repositories/{repo_id}/resource_descriptions/{resource_id.strip()}.xml?include_unpublished=true", stream=True).text
        print(f'{resource_id} exported. Writing to file.')
        ead_file_path = f"{self.dirpath}/{resource_id}.xml"
        with open(ead_file_path, 'a', encoding='utf-8') as outfile:
            outfile.write(get_ead)
        print(f'{resource_id} written to file: {ead_file_path}')
        return ead_file_path

    def export_ead_2002(self, row):
        return self.export_ead(row)

    def export_ead_3(self, row):
        return self.export_ead(row, ead3=True)

    def transform_ead_2002(self, ead_file):
        outfile = open(f"{self.dirpath}/{ead_file[:-4]}_out.xml", 'a', encoding='utf8')
        subprocess.Popen(["java", "-cp", "/usr/local/Cellar/saxon/9.9.1.3/libexec/saxon9he.jar", "net.sf.saxon.Transform",
                        "-s:" + self.dirpath + '/' + ead_file,
                        "-xsl:" + "transformations/yale.aspace_v112_to_yalebpgs.xsl",
                        "-o:" + outfile], stdout=outputfile, stderr=outputfile,
                       encoding='utf-8')

#This might be different now for EAD3?
    def transform_ead_3(self, ead_file_path):
    #     '''Transforms EAD files using a user-defined XSLT file.'''
        print(f'''Transforming file: {ead_file_path}
               using {self.ead_3_transformation}
               writing to {ead_file_path[:-4]}_out.xml
               ''')
        subprocess.run(["java", "-cp", "/usr/local/Cellar/saxon/9.9.1.3/libexec/saxon9he.jar", "net.sf.saxon.Transform",
                        f"-s:{ead_file_path}",
                        f"-xsl:{self.ead_3_transformation}",
                        f"-o:{ead_file_path[:-4]}_out.xml"], stdout=self.output_file, stderr=self.output_file,
                       encoding='utf-8')
        print(f'File transformed: {ead_file_path}')
        return f"{ead_file_path[:-4]}_out.xml"
        #return open(f"{ead_file_path[:-4]}_out.xml", 'r', encoding='utf-8').read()

    def validate_ead_3(self, ead_file_path):
        print(f'Validating file: {ead_file_path}')
        try:
            doc = etree.parse(ead_file_path)
            try:
                self.ead_3_schema.assertValid(doc)
                print('Valid')
            except etree.DocumentInvalid as err:
                print('Schema Validation Error')
                print(traceback.format_exc())
                print(err.error_log)
            except Exception:
                print(traceback.format_exc())
        #this finds a problem with the file
        except IOError:
            print('Invalid file')
            print(traceback.format_exc())
        #this finds syntax errors in XML
        except etree.XMLSyntaxError as err:
            print(f'XML Syntax Error: {ead_file_path}')
            print(traceback.format_exc())
            print(err.error_log)
        except Exception:
            print(traceback.format_exc())

    def export_transform_validate_ead3(self, row):
        '''Runs export, transform, and validate EAD functions using a user-defined schema file.'''
        ead_file_path = self.export_ead_3(row)
        transformed_ead_path = self.transform_ead_3(ead_file_path)
        validated_ead = self.validate_ead_3(transformed_ead_path)

    def prep_schema_for_validation(self):
        #will validate against this xsd file - can do that using lxml since it's not a schematron
        ead_3_schema = requests.get("https://raw.githubusercontent.com/SAA-SDT/EAD3/master/ead3.xsd").text
        ead_3_schema_encoded = etree.fromstring(bytes(ead_3_schema, encoding='utf8'))
        return etree.XMLSchema(ead_3_schema_encoded)

# def validate_ead_2002(ead_file):
#     '''Validates EAD files using a user-defined schema file. Only for EAD 2002'''
#     print('Done!')
#     print('Validating transformations against EAD 2002 and Schematron schemas')
#     newfilelist = os.listdir(dirpath + '/outfiles')
#     for outfile in newfilelist:
#         subprocess.Popen(["/Users/amd243/Dropbox/git/crux/target/crux-1.3-SNAPSHOT-all.jar", "-s",
#                         dirpath + "/transformations/yale.aspace.ead2002.sch",
#                         dirpath + '/outfiles/' + outfile], stdout=outputfile, stderr=outputfile,
#                              encoding='utf-8')
#         subprocess.Popen(["/Users/amd243/Dropbox/git/crux/target/crux-1.3-SNAPSHOT-all.jar",
#                               dirpath + '/outfiles/' + outfile], stdout=outputfile, stderr=outputfile,
#                              encoding='utf-8')
#     print('All Done! Check outfile for validation report')
#
