#!/usr/bin/python3
#~/anaconda3/bin/python

'''Functions and classes for handling requests to the ArchivesSpace API'''

import csv
from dataclasses import dataclass
from functools import wraps
import typing
import traceback

import requests

import aspace_utils


def _api_caller(crud_func, decorated=True):
    '''Sources: https://stackoverflow.com/questions/60907323/accessing-class-property-as-decorator-argument
                https://stackoverflow.com/questions/10724854/how-to-do-a-conditional-decorator-in-python
    '''
    def api_caller_decorator(json_func):
        @wraps(json_func)
        def wrapper(*args, **kw):
            # this should make the docrator optional, so that the json functions can be returned by themselves
            if not decorated:
                return json_func
            else:
                cls = args[0]
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
        writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames + ['info'])
        writer.writeheader()
        err_writer = csv.DictWriter(err_file, fieldnames=reader.fieldnames + ['info'])
        err_writer.writeheader()
        for row in aspace_utils.progress_bar(reader, count=cls.cfg.row_count):
            try:
                row = json_func(row)
                if crud_func == ASpaceCrud.reader:
                    row = crud_func(cls.cfg.api_url, cls.cfg.sesh, row)
                    print(row)
                # this is going to wrap the JSON function, and will have access
                # to the CRUD functions. Problem right now is that I can't access
                # the CRUD functions without instantiating the class. Currently
                # they rely on class variables to function. Could nix that and pass 
                # the sesh + api url, since I have them. But then why even have
                # the CRUD, why not just use the script tools?
            #     if crud_func in (ASpaceCrud.delete_data, ASpaceCrud.read_data):
            #         row = crud_func(row)
            #     elif crud_func in (ASpaceCrud.create_data, ASpaceCrud.update_data):
            #         row = json_func(row)
            #     writer.writerow(row)
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
    '''Class for handling create, read, update, and delete requests to the ArchivesSpace API

       Parameters:
        self.config_file: The configuration file
        self.config_file['api_url']: The ArchivesSpace base API URL
        self.config_file['api_username']: The ArchivesSpace username
        self.config_file['api_password']: The ArchivesSpace password
        self.config_file['backup_directory']: The string representation of the backup directory
        self.config_file['input_csv']: The string representation of the input CSV file path

       Usage:
        ::
          
          from aspace_tools import ASpaceCrud

          as_run = ASpaceRun()
    '''

    def __init__(self, aspace_conn):
        self.cfg = aspace_conn

    def creator(api_url, uri, sesh, record_json, csv_row) -> dict:
        '''Creates new records via the ArchivesSpace API.

           :param csv_row: A row of a CSV file containing record creation data.
           :param json_data: The json structure to use in the record creation process.
           :return: The CSV dict with the URI of the newly-created record attached

           Usage:
            ::
          
              with open(as_run.csvfile, encoding='utf8') as infile:
                reader = csv.DictReader(infile)
                for row in reader:
                    row = as_run.create_data(row, create_archival_object)

        '''
        return aspace_utils.post_record(api_url, uri, sesh, record_json, csv_row)

#    @_api_caller
    def reader(api_url, sesh, uri):
        '''Retrieves data via the ArchivesSpace API.

           Parameters:
            csv_row['uri']: The URI of the record to retrieve

           Returns:
            dict: The JSON response from the ArchivesSpace API.

           Usage:
            ::
          
              with open(as_run.csvfile, encoding='utf8') as infile:
                reader = csv.DictReader(infile)
                for row in reader:
                    json_record = as_run.read_data(row)
        '''
        return aspace_utils.get_record(api_url, uri, sesh)

 #   @_api_caller
    def updater(csv_row, json_func):
        '''Updates data via the ArchivesSpace API.

           Parameters:
            csv_row['uri']: The URI of the record to update.
            json_func: The json structure to use in the update.

           Returns:
            list: The CSV row with the URI of the update record appended to the end.

           Usage:
            ::
          
              with open(as_run.csvfile, encoding='utf8') as infile:
                reader = csv.DictReader(infile)
                for row in reader:
                    row = as_run.update_data(row, update_date_begin)
        '''
        record_json = aspace_utils.get_record(self.api_url, csv_row['uri']. self.sesh)
        aspace_utils.create_backups(self.dirpath, csv_row['uri'], record_json)
        record_json, uri = json_func(record_json, csv_row)
        return aspace_utils.post_record(self.api_url, uri, self.sesh, record_json, csv_row)

#    @_api_caller
    def deleter(csv_row):
        '''Deletes data via the ArchivesSpace API.

           :param csv_row['uri']: The URI of the record to delete.
           :return: The JSON response from the ArchivesSpace API.
           :raises ArchivesSpaceError: if delete is unsuccessful

           Usage:
            ::
          
              with open(as_run.csvfile, encoding='utf8') as infile:
                reader = csv.DictReader(infile)
                for row in reader:
                    try:
                        row = as_run.delete_data(row)
                    except ArchivesSpaceError:
                        pass
        '''
        return aspace_utils.delete_record(csv_row['uri'], self.sesh, self.dirpath)


def main():
    pass


if __name__ == "__main__":
    main()
