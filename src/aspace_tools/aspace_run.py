#!/usr/bin/python3
#~/anaconda3/bin/python

'''Classes for handling API and database connections and requests.'''

import csv
import traceback

import requests

from . import db
from . import script_tools
from . import json_data
# from . import queries
# from . import data_processing as dp

class ASpaceDB():
    '''Class for handling database queries'''

    def __init__(self):
        self.config_file = script_tools.check_config('as_tools_config', 'yml')
        self.dirpath = self.config_file.get('backup_directory')
        self.csvfile = self.config_file.get('input_csv')
        self.dbconn = db.DBConn(config_file=self.config_path)
        #self.query_data = ASQueries()

    def extract_note_query(self):
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

    def run_db_query(self, query_func, outfile=None):
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

    def run_db_queries(self, query_func):
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


class ASpaceRun():
    '''Class for handling API calls'''

    def __init__(self):
        self.config_file = script_tools.check_config('as_tools_config', 'yml')
        self.api_url = self.config_file.get('api_url')
        self.username = self.config_file.get('api_username')
        self.password = self.config_file.get('api_password')
        self.dirpath = self.config_file.get('backup_directory')
        self.csvfile = self.config_file.get('input_csv')
        self.output_file = f"{self.csvfile.replace('.csv', '')}_success.csv"
        self.error_file = f"{self.csvfile.replace('.csv', '')}_errors.csv"
        self.row_count = script_tools.get_rowcount(self.csvfile)
        try:
            _, self.sesh = script_tools.start_session(self.config_file)
        except script_tools.LoginError:
            # what here?
            pass

    def create_data(self, csv_row, json_func):
        '''Creates new records via the ArchivesSpace API.

           Parameters:
            csv_row: A row of a CSV file containing record creation data.
            json_data: The json structure to use in the record creation process.

           Returns:
            list: The CSV row with the URI of the newly-created record attached
        '''
        record_json, uri = json_func(csv_row)
        return script_tools.post_record(self.api_url, uri, self.sesh, record_json, csv_row)

    def read_data(self, csv_row):
        '''Retrieves data via the ArchivesSpace API.

           Parameters:
            csv_row['uri']: The URI of the record to retrieve

           Returns:
            dict: The JSON response from the ArchivesSpace API.
        '''
        return script_tools.get_record(self.api_url, csv_row['uri'], self.sesh)

    def update_data(self, csv_row, json_func):
        '''Updates data via the ArchivesSpace API.

           Parameters:
            csv_row['uri']: The URI of the record to update.
            json_func: The json structure to use in the update.

           Returns:
            list: The CSV row with the URI of the update record appended to the end.
        '''
        record_json = script_tools.get_record(self.api_url, csv_row['uri']. self.sesh)
        script_tools.create_backups(self.dirpath, csv_row['uri'], record_json)
        record_json, uri = json_func(record_json, csv_row)
        return script_tools.post_record(self.api_url, uri, self.sesh, record_json, csv_row)

    def delete_data(self, csv_row):
        '''Deletes data via the ArchivesSpace API.

           Parameters:
            csv_row['uri']: The URI of the record to delete.

           Returns:
            dict: The JSON response from the ArchivesSpace API.
        '''
        return script_tools.delete_record(csv_row['uri'], self.sesh, self.dirpath)

    def call_api(self, crud_func, json_func=None):
        '''Loops through a CSV file and runs the user-selected CRUD functions'''
        if json_func:
            json_func = getattr(json_data, json_func)
        with open(self.csvfile, 'r', encoding='utf8') as infile, open(self.output_file, 'a', encoding='utf8') as outfile, open(self.error_file, 'a', encoding='utf8') as err_file:
            reader = csv.DictReader(infile)
            writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames + ['info']).writeheader()
            err_writer = csv.DictWriter(err_file, fieldnames=reader.fieldnames + ['info']).writeheader()
            for row in progress_bar(reader, count=self.row_count):
                try:
                    row = self.crud_func(row, json_func)
                    writer.writerow(row)
                except (script_tools.ArchivesSpaceError, requests.exceptions.RequestException) as err:
                    instructions = input(f'Error! Enter R to retry, S to skip, Q to quit: ')
                    if instructions == 'R':
                        row = self.crud_func(row, json_func)
                        writer.writerow(row)
                    elif instructions == 'S':
                        row = script_tools.handle_error(err, row)
                        err_writer.writerow(row)
                        continue
                    elif instructions == 'Q':
                        break
