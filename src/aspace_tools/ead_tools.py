#!/usr/bin/python3

'''Functions for working with EAD files.'''

import subprocess
from lxml import etree
import traceback

import requests

def export_ead(api_url, dirpath, sesh, csv_row, ead3=False, get_ead=None):
    '''Exports EAD files using a list of resource IDs as input.

       Parameters:
        csv_row['resource_id']: The ID of the resource
        csv_row['repo_id']: The ID of the repository

       Returns:
        str: A string representation of the EAD response from the ArchivesSpace API.
    '''
    repo_id = row['repo_id']
    resource_id = row['resource_id']
    print(f'Exporting {resource_id}')
    if ead3 == True:
        get_ead = sesh.get(f"{self.api_url}/repositories/{csv_row['repo_id']}/resource_descriptions/{csv_row['resource_id'].strip()}.xml?include_unpublished=true&ead3=true", stream=True).text
    elif ead3 == False:
        get_ead = sesh.get(f"{api_url}/repositories/{csv_row['repo_id']}/resource_descriptions/{csv_row['resource_id'].strip()}.xml?include_unpublished=true", stream=True).text
    print(f"{csv_row['resource_id']} exported. Writing to file.")
    ead_file_path = f"{dirpath}/{resource_id}.xml"
    with open(ead_file_path, 'a', encoding='utf-8') as outfile:
        outfile.write(get_ead)
    print(f'{resource_id} written to file: {ead_file_path}')
    return ead_file_path

def export_ead_2002(row):
    return export_ead(row)

def export_ead_3(row):
    return export_ead(row, ead3=True)

def transform_ead_2002(ead_file, dirpath, output_file):
    outfile = open(f"{dirpath}/{ead_file[:-4]}_out.xml", 'a', encoding='utf8')
    subprocess.Popen(["java", "-cp", "/usr/local/Cellar/saxon/9.9.1.3/libexec/saxon9he.jar", "net.sf.saxon.Transform",
                    "-s:" + dirpath + '/' + ead_file,
                    "-xsl:" + "transformations/yale.aspace_v112_to_yalebpgs.xsl",
                    "-o:" + outfile], stdout=output_file, stderr=output_file,
                   encoding='utf-8')

def transform_ead_3(ead_file_path, output_file, ead_3_transformation):
     '''Transforms EAD files using a user-defined XSLT file.'''
    print(f'''Transforming file: {ead_file_path}
           using {ead_3_transformation}
           writing to {ead_file_path[:-4]}_out.xml
           ''')
    subprocess.run(["java", "-cp", "/usr/local/Cellar/saxon/9.9.1.3/libexec/saxon9he.jar", "net.sf.saxon.Transform",
                    f"-s:{ead_file_path}",
                    f"-xsl:{ead_3_transformation}",
                    f"-o:{ead_file_path[:-4]}_out.xml"], stdout=output_file, stderr=output_file,
                   encoding='utf-8')
    print(f'File transformed: {ead_file_path}')
    return f"{ead_file_path[:-4]}_out.xml"
    #return open(f"{ead_file_path[:-4]}_out.xml", 'r', encoding='utf-8').read()

def validate_ead_3(ead_3_schema, ead_file_path):
	'''Validates an EAD file against the EAD3 schema'''
    print(f'Validating file: {ead_file_path}')
    try:
        doc = etree.parse(ead_file_path)
        try:
            ead_3_schema.assertValid(doc)
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

def export_transform_validate_ead3(row):
    '''Runs export, transform, and validate EAD functions using a user-defined schema file.'''
    ead_file_path = export_ead_3(row)
    transformed_ead_path = transform_ead_3(ead_file_path)
    validated_ead = validate_ead_3(transformed_ead_path)

def prep_schema_for_validation():
	'''Retrieves EAD3 schema from Github and returns as an etree Schema object'''
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