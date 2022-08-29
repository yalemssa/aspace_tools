#!/usr/bin/python3
#~/anaconda3/bin/python

'''Classes for handling API and database connections and requests.'''

import csv
from dataclasses import dataclass
from functools import wraps
import typing
import traceback

import requests


import db
import script_tools
#import json_data

# from . import db
# from . import script_tools
# from . import json_data
# from . import queries
# from . import data_processing as dp

class ASpaceDB():
    """Class for handling database queries

       .. code-block:: python

          from aspace_tools import ASpaceDB
          from aspace_tools import queries

          as_db = ASpaceDB()
          data = as_db.run_query(queries.box_list)
          print(data)

    """

    def __init__(self):
        self.config_file = script_tools.check_config('as_tools_config', 'yml')
        self.dirpath = self.config_file.get('backup_directory')
        self.csvfile = self.config_file.get('input_csv')
        #self.dbconn = db.DBConn(config_file=self.config_path)
        #self.query_data = ASQueries()

    #def extract_note_query(self):
        '''Runs a query to get all notes and then extracts the note content and note type
        '''
        #try:
            #query_func = self.query_data.all_notes()
            #query_data = dp.extract_note_content(query_func, 'extract_notes.csv', self.dbconn)
            #not this - want a count of the individual things...
           # counter = query_data['type'].count()
            #print(counter)
        #finally:
            #yes? or do I want this to stay open?
            #self.dbconn.close_conn()
        #return query_data

    def run_query(self, query_func, outfile=None):
        '''Runs a single query against the ArchivesSpace database.

           Parameters:
            dbconn: The database connection
            query_func: The query to run.

           Todo:
            make sure that there is an outfile in the config file to store query data.
            Have the outfile be a default arg that can set if don't want to just return
            a generator or whatever.
        '''
        #should not need this - should already be passing in a function
        #query_func = getattr(self.query_data, query_func)
        #return (self.dbconn.run_query_list(query_func()))

    def run_queries(self, query_func):
        '''Runs multiple queries against the ArchivesSpace database.

           Parameters:
            query_func: The query to run. Passed in from queries.py

           Todo:
            Also need to determine whether running the run_query_list function  is the best approach.
            Add a thing so I can run a single query on the command line...
            This works as it should. Formulates the f-string query and runs it, returning a generator
            of lists (right?). From here can process the output in any way you like - can write to output file or do any additional processing
            MUST CLOSE THE DB CONNECTION!
        '''
        #query_func = getattr(self.query_data, query_func)
       # return (self.dbconn.run_query_list(query_func(row)) for row in self.csvfile)

@dataclass(slots=True)
class ASpaceConnection:
    '''Holds ArchivesSpace connection and configuration data'''
    api_url: str
    username: str
    password: str
    dirpath: str
    csvfile: str
    output_file: str
    error_file: str
    row_count: int
    sesh: 'requests.sessions.Session'

    @classmethod
    def from_dict(cls: typing.Type["item"], config_file='as_tools_config.yml': str):
        '''Takes an opened configration file (YML or JSON) as input. Populates the ASpaceConnection variables with values from the config.
        Learned this from: https://dev.to/eblocha/using-dataclasses-for-configuration-in-python-4o53
        '''
        cfg = script_tools.check_config(config_file)
        return cls(
            api_url=cfg.get('api_url'),
            username=cfg.get('api_username'),
            password=cfg.get('api_password'),
            dirpath=cfg.get('backup_directory'),
            csvfile=cfg.get('input_csv'),
            output_file=f"{cfg.get('input_csv').replace('.csv', '')}_success.csv",
            error_file=f"{cfg.get('input_csv').replace('.csv', '')}_errors.csv",
            row_count=script_tools.get_rowcount(cfg.get('input_csv')),
            sesh=script_tools.start_session(cfg, return_url=False))

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
        return script_tools.post_record(api_url, uri, sesh, record_json, csv_row)

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
        return script_tools.get_record(api_url, uri, sesh)

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
        record_json = script_tools.get_record(self.api_url, csv_row['uri']. self.sesh)
        script_tools.create_backups(self.dirpath, csv_row['uri'], record_json)
        record_json, uri = json_func(record_json, csv_row)
        return script_tools.post_record(self.api_url, uri, self.sesh, record_json, csv_row)

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
        return script_tools.delete_record(csv_row['uri'], self.sesh, self.dirpath)

    # def run_process(self, crud_func, json_func=None):
    #     '''Loops through a CSV file and runs the user-selected CRUD functions

    #        :param crud_func: The CRUD function to use in the update
    #        :param json_func: The JSON template to use in the update

    #        Usage:
    #         ::
          
    #           from aspace_tools import ASpaceRun

    #           as_run = ASpaceRun()
    #           as_run.call_api(update_data, update_date_begin)

    #     '''
    #     if json_func:
    #         json_func = getattr(json_data, json_func)
    #     with open(self.csvfile, 'r', encoding='utf8') as infile, open(self.output_file, 'a', encoding='utf8') as outfile, open(self.error_file, 'a', encoding='utf8') as err_file:
    #         reader = csv.DictReader(infile)
    #         # used to be able to call writeheader at initialization of the DictWriter, but seems
    #         # like you can't do that anymore in Python 3.10
    #         writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames + ['info']).writeheader()
    #         err_writer = csv.DictWriter(err_file, fieldnames=reader.fieldnames + ['info']).writeheader()
    #         for row in progress_bar(reader, count=self.row_count):
    #             try:
    #                 if crud_func in (self.delete_data, self.read_data):
    #                     row = crud_func(row)
    #                 elif crud_func in (self.create_data, self.update_data):
    #                     row = crud_func(row, json_func)
    #                 writer.writerow(row)
    #             except (script_tools.ArchivesSpaceError, requests.exceptions.RequestException) as err:
    #                 instructions = input(f'Error! Enter R to retry, S to skip, Q to quit: ')
    #                 if instructions == 'R':
    #                     row = self.crud_func(row, json_func)
    #                     writer.writerow(row)
    #                 elif instructions == 'S':
    #                     row = script_tools.handle_error(err, row)
    #                     err_writer.writerow(row)
    #                     continue
    #                 elif instructions == 'Q':
    #                     break


            # if json_func:
            #     json_func = getattr(json_data, json_func)
            # for row in progress_bar(reader, count=self.row_count):
            #     try:
            #         if func in (read_data, delete_data):
            #             row = func(row)
            #         elif func in (create_data, update_data):
            #             row = func(row, json_func)
            #         writer.writerow(row)
            #     except (script_tools.ArchivesSpaceError, requests.exceptions.RequestException) as err:
            #         instructions = input(f'Error! Enter R to retry, S to skip, Q to quit: ')
            #         if instructions == 'R':
            #             row = self.crud_func(row, json_func)
            #             writer.writerow(row)
            #         elif instructions == 'S':
            #             row = script_tools.handle_error(err, row)
            #             err_writer.writerow(row)
            #             continue
            #         elif instructions == 'Q':
            #             break


def main():
    cfg = script_tools.check_config('as_tools_config.yml')
    as_conn = ASpaceConnection.from_dict(cfg)
    crud = ASpaceCrud(as_conn)
    print(crud.cfg.csvfile)
    print(crud.cfg.sesh)
    print(crud.cfg.row_count)
    crud.cfg.csvfile = "/Users/aliciadetelich/Dropbox/git/aspace_tools/data/inputs/mention.csv"
    print(crud.cfg.csvfile)
    print(crud.cfg.row_count)
    crud.cfg.row_count = script_tools.get_rowcount(crud.cfg.csvfile)
    crud.random_test_func()






if __name__ == "__main__":
    main()












