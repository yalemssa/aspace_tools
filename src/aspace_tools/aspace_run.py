#!/usr/bin/python3
#~/anaconda3/bin/python

'''Functions and classes for handling requests to the ArchivesSpace API'''

import csv
from dataclasses import dataclass
from functools import wraps
import typing
import traceback

import requests

from . import aspace_utils

def _api_caller(crud_func):
    '''Sources: https://stackoverflow.com/questions/60907323/accessing-class-property-as-decorator-argument
                https://stackoverflow.com/questions/10724854/how-to-do-a-conditional-decorator-in-python
    '''
    def api_caller_decorator(json_func):
        @wraps(json_func)
        def wrapper(*args, **kw):
            cls = args[0]
            # this is a hacky way to make the decorators sort of conditional
            # if just the regular csv row is passed in, either when the class
            # is instantiated or not, the function will take the row as 
            # an argument and will not run the process_data function.
            if isinstance(cls, dict):
                return json_func(cls)
            if len(args) == 2:
                if isinstance(args[1], dict):
                    return json_func(args[1])
            process_data(cls, json_func, crud_func)       
            print(cls.cfg.csvfile)
            print(cls.cfg.sesh)
            print(cls.cfg.api_url)
            print(crud_func)
        return wrapper
    return api_caller_decorator

def process_data(cls, json_func, crud_func):
    '''Boilerplate code for making bulk requests via a CSV input file'''
    with open(cls.cfg.csvfile, 'r', encoding='utf8') as infile, open(cls.cfg.output_file, 'a', encoding='utf8') as outfile, open(cls.cfg.error_file, 'a', encoding='utf8') as err_file:
        reader = csv.DictReader(infile)
        # used to be able to call writeheader at initialization of the DictWriter, but seems
        # like you can't do that anymore in Python 3.10
        writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames + ['info', 'jsonmodel_type'])
        writer.writeheader()
        err_writer = csv.DictWriter(err_file, fieldnames=reader.fieldnames + ['info', 'jsonmodel_type'])
        err_writer.writeheader()
        for row in aspace_utils.progress_bar(reader, count=cls.cfg.row_count):
            try:
                # should I do something different here? I've seen that using a bunch of if/else's
                # to decide which functions to run is not ideal
                if crud_func == ASpaceCrud.creator:
                    # forms the JSON and returns the endpoint
                    record_json, uri = json_func(row)
                    # posts the record, returns the input row with the new URI appended
                    row = crud_func(cls.cfg.api_url, cls.cfg.sesh, uri, record_json, row)
                if crud_func == ASpaceCrud.updater:
                    row = crud_func(cls.cfg.api_url, cls.cfg.sesh, cls.cfg.dirpath, row, json_func)
                if crud_func == ASpaceCrud.reader:
                    # this just returns the result, as JSON. Still need to do something with it. Like write it?
                    result = crud_func(cls.cfg.api_url, cls.cfg.sesh, row)
                writer.writerow(row)
            except (aspace_utils.ArchivesSpaceError, requests.exceptions.RequestException) as err:
                print(traceback.format_exc())
                instructions = input(f'Error! Enter R to retry, S to skip, Q to quit: ')
                if instructions == 'R':
                    row = crud_func(row)
                    writer.writerow(row)
                elif instructions == 'S':
                    row = aspace_utils.handle_error(err, row)
                    err_writer.writerow(row)
                    continue
                elif instructions == 'Q':
                    break

class ASpaceConnection:
    '''Holds ArchivesSpace connection and configuration data'''

    def __init__(self, config_file='as_tools_config.yml'):
        cfg = aspace_utils.check_config(config_file)
        self.api_url = cfg.get('api_url')
        self.username = cfg.get('api_username')
        self.password = cfg.get('api_password')
        self.dirpath = cfg.get('backup_directory')
        self.csvfile = cfg.get('input_csv')
        self.output_file = f"{cfg.get('input_csv').replace('.csv', '')}_success.csv"
        self.error_file = f"{cfg.get('input_csv').replace('.csv', '')}_errors.csv"
        self.row_count = aspace_utils.get_rowcount(cfg.get('input_csv'))
        self.sesh = aspace_utils.start_session(cfg, return_url=False)

    def update_from_input(self, input_csv: str, backup_dir=None):
        '''Takes user input and updates input files and row count, and optionally the backup directory'''
        self.csvfile = input_csv
        if backup_dir:
            self.dirpath = backup_dir
        self.row_count = aspace_utils.get_rowcount(input_csv)
        self.output_file = f"{input_csv.replace('.csv', '')}_success.csv"
        self.error_file = f"{input_csv.replace('.csv', '')}_errors.csv"

    def update_from_config(self, config_file='as_tools_config.yml'):
        '''Takes an updated configuration file and updates inputs without restarting the Aspace session'''
        cfg = aspace_utils.check_config(config_file)
        self.csvfile = cfg.get('input_csv')
        self.dirpath = cfg.get('backup_directory')
        self.row_count = aspace_utils.get_rowcount(cfg.get('input_csv'))
        self.output_file = f"{cfg.get('input_csv').replace('.csv', '')}_success.csv"
        self.error_file = f"{cfg.get('input_csv').replace('.csv', '')}_errors.csv"

class ASpaceCrud:
    '''Class which stores functions called by the aspace_requests module. This class
       is not usually instantiated and the methods are usually not called directly.

       There are no class attributes for ASpaceCrud.

    '''

    def creator(api_url, sesh, uri, record_json, csv_row) -> dict:
        '''Creates new records via the ArchivesSpace API.

           :param csv_row: A row of a CSV file containing record creation data.
           :param json_data: The json structure to use in the record creation process.
           :return: The CSV dict with the URI of the newly-created record attached
        '''
        return aspace_utils.post_record(api_url, uri, sesh, record_json, csv_row)

#    @_api_caller
    def reader(api_url, sesh, uri, dirpath):
        '''Retrieves data via the ArchivesSpace API.

           Parameters:
            uri: The URI of the record to retrieve

           Returns:
            dict: The JSON response from the ArchivesSpace API.
        '''
        record_json = aspace_utils.get_record(api_url, uri, sesh)
        aspace_utils.create_backups(dirpath, uri, record_json)
        return record_json

 #   @_api_caller
    def updater(api_url, sesh, dirpath, csv_row, json_func):
        '''Updates data via the ArchivesSpace API.

           Parameters:
            csv_row['uri']: The URI of the record to update.
            json_func: The json structure to use in the update.

           Returns:
            list: The CSV row with the URI of the update record appended to the end.
        '''
        record_json = aspace_utils.get_record(api_url, csv_row['uri']. sesh)
        aspace_utils.create_backups(dirpath, csv_row['uri'], record_json)
        record_json, uri = json_func(record_json, csv_row)
        return aspace_utils.post_record(api_url, uri, sesh, record_json, csv_row)

#    @_api_caller
    def deleter(csv_row, sesh, dirpath):
        '''Deletes data via the ArchivesSpace API.

           :param csv_row['uri']: The URI of the record to delete.
           :return: The JSON response from the ArchivesSpace API.
           :raises ArchivesSpaceError: if delete is unsuccessful
        '''
        return aspace_utils.delete_record(csv_row['uri'], sesh, dirpath)


def main():
    pass


if __name__ == "__main__":
    main()
