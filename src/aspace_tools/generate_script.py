#!/usr/bin/python3

import csv
import inspect
import json
import os
from pathlib import Path
import sys
import re

from rich import print

import json_data
import script_tools


def generate_config(config_file_path):
    with open(config_file_path, 'w', encoding='utf8') as cfg_path:
        json_template = {"api_url": "","username": "", "password": "", "input_csv": "", "backup_directory": ""}
        json.dump(json_template, cfg_path, indent=4)

def get_csv_headers(docstring):
    string_lines = docstring.split('\n')
    headers = [line[line.find("'")+1:line.rfind("'")].strip() for line in string_lines if 'csv' in line]
    return headers

def generate_csv_template(csv_template_file_path, docstring):
    with open(csv_template_file_path, 'w', encoding='utf8') as template:
        writer = csv.writer(template)
        headers = get_csv_headers(docstring)
        writer.writerow(headers)

def get_func_data(module_name, func_string=None):
    if func_string is None:
        functions = get_func_list(module_name)
        print(functions)
        func_string = input('Enter desired function name: ')
    func_object = getattr(module_name, func_string)
    source_code = inspect.getsource(func_object)
    docstring = inspect.getdoc(func_object)
    signa = inspect.signature(func_object)
    return source_code, func_string, func_object, docstring, signa

def get_func_list(module):
    return [function for function in dir(module) if function[0] != '_']

def get_crud(signa):
    if 'record_json' in str(signa):
        get_func = inspect.getsource(getattr(script_tools, 'get_record'))
        post_func = inspect.getsource(getattr(script_tools, 'post_record'))
        return f"""{get_func}
{post_func}"""
    else:
        return inspect.getsource(getattr(script_tools, 'post_record'))

def get_params(signa):
    if 'record_json' in str(signa):
        return 'record_json, row'
    else:
        return 'row'

def get_record_template(signa):
    if 'record_json' in str(signa):
        return f"""
                    record_json = get_record(api_url, row['uri'], sesh)
                    create_backups(backup_directory, row['uri'], record_json)"""
    else:
        return '\r'

def func_template(return_value, func_name, params):
    template = f"""record_json, uri = {func_name.__name__}({params})"""
    if return_value == 'tuple':
        return template
    elif return_value == 'str':
        return template.replace('record_json, ', '')

def post_record_template(return_value, post_type='post_record'):
    template = f"""{post_type}(api_url, uri, sesh, record_json, row, writer)"""
    if return_value == 'tuple':
        return template
    elif return_value == 'str':
        return template.replace(', record_json', '')
    
def boilerplate(json_source_code, func_name, signa, params, return_value):
    return f"""#!/usr/bin/python3

import csv
import json
import logging
import os
import sys

# only do this in testing
from rich import print

import requests

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(module)s %(funcName)s %(message)s',
                    handlers=[logging.FileHandler("log.log", mode='a'),
                              stream_handler])

{get_func_data(script_tools, 'LoginError')[0]}
{get_func_data(script_tools, 'ArchivesSpaceError')[0]}
{get_func_data(script_tools, 'get_rowcount')[0]}
{get_func_data(script_tools, 'progress_bar')[0]}
{get_func_data(script_tools, 'get_data_path')[0]}
{get_func_data(script_tools, 'check_config')[0]}
{get_func_data(script_tools, 'check_credentials')[0]}
{get_func_data(script_tools, 'get_login_inputs')[0]}
{get_func_data(script_tools, 'start_session')[0]}
{get_func_data(script_tools, 'create_backups')[0]}
{get_func_data(script_tools, 'handle_error')[0]}
{get_crud(signa)}
{json_source_code}
def main():
    try:
        config = check_config()
        api_url, sesh = start_session(config)
        input_file_path = get_data_path(config, 'input_csv')
        backup_directory = get_data_path(config, 'backup_directory')
        output_file_path = f"{{input_file_path.replace('.csv', '')}}_success.csv"
        error_file_path = f"{{input_file_path.replace('.csv', '')}}_errors.csv"
        row_count = get_rowcount(input_file_path)
        with open(input_file_path, 'r', encoding='utf8') as infile, open(output_file_path, 'a', encoding='utf8') as outfile, open(error_file_path, 'a', encoding='utf8') as errfile:
            reader = csv.DictReader(infile)
            writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames + ['info'])
            writer.writeheader()
            err_writer = csv.DictWriter(errfile, fieldnames=reader.fieldnames + ['info'])
            err_writer.writeheader()
            for row in progress_bar(reader, count=row_count):
                try:{get_record_template(signa)}
                    {func_template(return_value, func_name, params)}
                    {post_record_template(return_value)}
                except (ArchivesSpaceError, requests.exceptions.RequestException) as err:
                    logging.error(err)
                    instructions = input(f'Error! Enter R to retry, S to skip, Q to quit: ')
                    if instructions == 'R':
                        logging.debug('Trying again...')
                        {post_record_template(return_value)}
                    elif instructions == 'S':
                        row = handle_error(err, row)
                        err_writer.writerow(row)
                        logging.debug('Skipping record...')
                        continue
                    elif instructions == 'Q':
                        logging.debug('Exiting on user request...')
                        break
    except LoginError as login_err:
        logging.error(login_err)
    except Exception as gen_ex:
        logging.exception(gen_ex)

if __name__ == '__main__':
    main()"""

def generate_data():
    #fp = input('Enter base file path: ')
    fp = "/Users/aliciadetelich/Desktop/script_generator"
    os.chdir(fp)
    config_file_path = os.path.join(fp, 'config.json')
    source_code, func_string, func_object, docstring, signa = get_func_data(json_data)
    script_file_path = os.path.join(fp, f'{func_string}.py')
    csv_template_file_path = os.path.join(fp, f'{func_string}_template.csv')
    return_value = func_object.__annotations__['return'].__name__
    params = get_params(signa)
    generate_csv_template(csv_template_file_path, docstring)
    generate_config(config_file_path)
    with open(script_file_path, 'w', encoding='utf8') as script_file:
        script_file.write(boilerplate(source_code, func_object, signa, params, return_value))

def main():
    generate_data()


if __name__ == '__main__':
    main()


'''

Is the logging setup ok?

Testing - IN PROGRESS. Tests? LOL
    Seems to be running REALLY slow - not sure if this is the network or the script.
    maybe try some different things and see what happens. Could just be the resource records...

DONE - Better error handling for HTTP errors: https://stackoverflow.com/questions/16511337/correct-way-to-try-except-using-python-requests-module
        DONE - Still need to figure out how to do a proper retry, right now it just stops everything
DONE - make sure that all the other json functions return the uri
DONE - Generate CSV template for script
DONE - Generate config
DONE - Add output - success/failure, new URIs to spreadsheet, something like that

Future:
Generate Pyinstaller
Review endpoints and add some more stuff to json_data...what about from templates.py....
Generate documentation

'''




