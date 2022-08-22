#!/usr/bin/python3

'''
Utility functions and custom exceptions for aspace_tools

'''

import csv
import json
import logging
import sys

import yaml

import requests
from rich import print

class LoginError(Exception):
    '''Custom exception to catch ArchivesSpace login errors

       Returns:
        An f-string which contains the status code of the request, the ArchivesSpace base API URL, the username submitted during the login attempt, and the error message

    '''
    def __init__(self, status_code, url, username, message="Login failed!"):
        self.status_code = status_code
        self.url = url
        self.username = username
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message} URL: {self.url}, Username: {self.username}, Status code: {self.status_code}"

class ArchivesSpaceError(Exception):
    '''Custom exception to catch ArchivesSpace API call errors

       Returns:
        An f-string which contains the URI of the record on which the error was encountered, the status code of the request, the error message from the ArchivesSpace response, and the generic error message for the exception
    '''
    def __init__(self, uri, status_code, aspace_message, message="ArchivesSpace Error!"):
        self.uri = uri
        self.status_code = status_code
        self.aspace_message = aspace_message
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message} URI: {self.uri}, Status code: {self.status_code}, Message: {self.aspace_message.get('error')}"

def get_rowcount(fp) -> int:
    '''Calculates the number of rows in a CSV file
        
       Parameters:
        fp: A string representation of the input file path

       Returns:
        The number of rows in the input file

    '''
    with open(fp, encoding='utf8') as input_file:
        return len(list(csv.reader(input_file))) - 1

def progress_bar(it, count=None, prefix="", size=60, out=sys.stdout):
    '''A simple local progress bar which obviates the need for a third-party
       library such as tqdm. Adapted from this post: https://stackoverflow.com/a/34482761

       Parameters:
        it: The iterator
        count: Optional precalculated row count, for generators
        prefix: Optional prefix message. Default "".
        size: Optional bar size. Default 60.
        out: Where to output the progress bar. Default stdout.
    '''
    if count is None:
        count = len(it)
    def show(counter):
        advance = int(size*counter/count)
        percent_done = counter/count
        print("{}{}{} {}/{} {:.2%}".format(prefix, u"█"*advance, "."*(size-advance), counter, count, percent_done), 
                end='\r', file=out, flush=True)
    show(0)
    for i, item in enumerate(it):
        yield item
        show(i+1)
    print("\n", flush=True, file=out)

def get_record(api_url, uri, sesh) -> dict:
    '''Makes an HTTP GET request and attempts to return a JSON response

       Parameters:
        api_url: The base URL of the ArchivesSpace API
        uri: The URI of the record to retrieve
        sesh: The HTTP session object
    '''
    record = sesh.get(f"{api_url}{uri}")
    if record.status_code == 200:
        return json.loads(record.text)
    else:
        raise ArchivesSpaceError(uri, record.status_code, json.loads(record.text))

def post_record(api_url, uri, sesh, record_json, csv_row) -> dict:
    '''Makes an HTTP POST request and attempts to return a JSON response

       Parameters:
        api_url: The base URL of the ArchivesSpace API
        uri: The URI of the record to update
        sesh: The HTTP session object
        record_json: The JSON representation of the record to update
        csv_row: The CSV row containing data to update
    '''
    record = sesh.post(f"{api_url}{uri}", json=record_json)
    # what if the text cannot be converted to json? need to make sure it works
    if record.status_code == 200:
        result = json.loads(record.text)
        if result.get('status') == 'Created':
            csv_row['info'] = result['uri']
        return csv_row
    else:
        # do something with the row here?
        raise ArchivesSpaceError(uri, record.status_code, json.loads(record.text))

def delete_record(api_url, uri, sesh, dirpath) -> dict:
    '''Makes an HTTP DELETE request and attempts to return a JSON response

       Parameters:
        api_url: The base URL of the ArchivesSpace API
        uri: The URI of the record to delete
        sesh: The HTTP session object
        dirpath: The string representation of the backup directory
    '''
    record_json = get_record(uri, sesh)
    create_backups(dirpath, uri, record_json)
    delete = sesh.delete(f"{api_url}{uri}", json=record_json)
    if delete.status_code == 200:
        return json.loads(delete.text)
    else:
        raise ArchivesSpaceError(uri, record.status_code, json.loads(delete.text))

def create_backups(dirpath, uri, record_json):
    '''Creates a backup of a JSON file prior to update

       Parameters:
        dirpath: The string representation of the backup directory
        uri: The URI of the record to back up
        record_json: The JSON to back up
    '''
    with open(f"{dirpath}/{uri[1:].replace('/','_')}.json", 'a', encoding='utf8') as outfile:
        json.dump(record_json, outfile, sort_keys=True, indent=4)

def check_config(file_name='config', file_type='json') -> dict:
    '''Checks whether a configration file exists, and if so opens and returns
       the file. Can handle either .json or .yml files.

       Parameters:
        file_name: The configuration file name. Default value 'config'
        file_type: The configuration file type. Default value 'json'
    '''
    path_to_this_file = os.path.dirname(os.path.realpath(sys.argv[0]))
    config_path = os.path.join(path_to_this_file, f"{file_name}.{file_type}")
    if os.path.exists(config_path):
        with open(config_path, encoding='utf8') as config_file:
            if file_type == 'yml':
                return yaml.safe_load(config_file)
            elif file_type == 'json':
                return json.load(config_file)

def get_data_path(config, data_type):
    '''Checks the location of a CSV file. Asks for a path if file is not found.'''
    if config:
        csv_path = config.get(data_type)
        if csv_path not in (None, ''):
            return csv_path
        else:
            return input(f'Please enter path to {data_type}: ')
    else:
        return input(f'Please enter path to {data_type}: ')

def get_login_inputs() -> tuple:
    '''Requests login information from the end user

       Returns:
        A tuple containing user-submitted ArchivesSpace URL, username, and password
    '''
    url = input('Please enter the ArchivesSpace API URL: ')
    username = input('Please enter your username: ')
    password = input('Please enter your password: ')   
    return url, username, password

def check_credentials(config) -> tuple:
    '''Checks the confiration file for login information, asks for user 
       input if not found.

       Returns:
        A tuple containing credentials from the configuration file or, if configuration data is missing, from user-submitted input
    '''
    if config:
        if (config.get('api_url') in (None, '')) or (config.get('username') in (None, '')) or (config.get('password') in (None, '')):
            return get_login_inputs()
        else:
            return config['api_url'], config['username'], config['password']
    else:
        return get_login_inputs()

def start_session(config=None) -> tuple:
    '''Starts an HTTP session, attempts to login to ArchivesSpace API.

       Parameters:
        config: The configuration file

       Returns:
        The base API URL and session key
    '''
    url, username, password = check_credentials(config)
    session = requests.Session()
    session.headers.update({'Content_Type': 'application/json'})
    auth_request = session.post(f"{url}/users/{username}/login?password={password}")
    if auth_request.status_code == 200:
        print(f'Login successful!: {url}')
        session_token = json.loads(auth_request.text)['session']
        session.headers['X-ArchivesSpace-Session'] = session_token
        return url, session
    else:
        raise LoginError(auth_request.status_code, url, username)

def handle_result(csv_row, record_post) -> dict:
    '''Appends the URI of a successfully created or updated record to the 
       input CSV row
    
       Parameters:
        csv_row: The row of input data
        record_post: The response of the POST request

       Returns:
        CSV row with the URI of the created or updated record.
    '''
    if record_post.get('status') == 'Created':
        csv_row['info'] = record_post['uri']
    return csv_row

def handle_error(error, csv_row) -> dict:
    '''Appends the ArchivesSpace error message of a failed update to the 
       input CSV row

       Parameters:
        error: The error message
        csv_row: The row of input data

       Returns:
        CSV row with the error message of the failed update
    '''
    csv_row['info'] = error
    return csv_row
                    
def get_endpoints():
    pass

def main():
    fp = "/Users/aliciadetelich/Desktop/all_ru_1160_files.csv"
    rowcount = get_rowcount(fp)
    with open(fp, encoding='utf8') as input_file:
        reader = csv.reader(input_file)
        for row in progress_bar(reader, count=rowcount, prefix="Processing file: "):
            time.sleep(0.3)


if __name__ == '__main__':
    main()


