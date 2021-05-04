#!/usr/bin/python3
#~/anaconda3/bin/python

import os
import traceback
import requests
import json
from pathlib import Path

import dill as pickle

#from utilities import db as dbssh
from utilities import dbssh
from utilities import utilities as u


from crud import ASCrud
from json_data import ASJsonData
from queries import ASQueries

import aspace_tools_logging as atl
import data_processing as dp

'''
This file contains three functions which provide the scaffolding for interacting
with the ArchivesSpace API and MySQL database.

CRUD actions which are called by the call_api function are stored in the crud.py
file. CRUD functions include create_data, update_data, etc.

Todo:

    Add options for database query outputs - outfile, generator, list, DF, etc.

    Command line interface in main.py (rename??) - in progress
    Add variables to doc sctrings in json data, queries, etc. - in progress
    Do I need to import the login function here. Can I just import that function?
    I have been thinking about using the .apply function in conjunction with
    the json functionality of pandas for this
    use something to flatten the nested JSON
    use an error logging function to wrap the try/except
    -integrate update_microfilm.py into this process
'''

logger = atl.logging.getLogger(__name__)

#@atl.as_tools_logger(logger)
def api_login(url=None, username=None, password=None):
    '''Logs into the ArchivesSpace API.

       Parameters:
        url: The URL to the ArchivesSpace API.
        username: The user's username.
        password: The user's password.

       Returns:
        dict: The JSON response from the ArchivesSpace API.
    '''
    try:
        if url is None and username is None and password is None:
            url = input('Please enter the ArchivesSpace API URL: ')
            username = input('Please enter your username: ')
            password = input('Please enter your password: ')
        auth = requests.post(url+'/users/'+username+'/login?password='+password).json()
        #if session object is returned then login was successful; if not it failed.
        if 'session' in auth:
            session = auth["session"]
            h = {'X-ArchivesSpace-Session':session, 'Content_Type': 'application/json'}
            print('Login successful!')
            logger.debug('Success!')
            return (url, h)
        else:
            print('Login failed! Check credentials and try again.')
            logger.debug('Login failed')
            logger.debug(auth.get('error'))
            #try again
            u, heads = login()
            return u, heads
    except:
        print('Login failed! Check credentials and try again!')
        logger.exception('Error: ')
        u, heads = login()
        return u, heads


class ASpaceDB():

    def __init__(self):
        self.config_file = u.get_config(cfg='as_tools_config.yml')
        self.dirpath = u.setdirectory(self.config_file['backup_directory'])
        self.csvfile = u.opencsvdict(self.config_file['input_csv'])
        self.dbconn = dbssh.DBConn(config_file=self.config_path)
        self.query_data = ASQueries()

    def extract_note_query(self):
        '''Runs a query to get all notes and then extracts the note content and note type

           This is a different format than the others; I want to be able to get a count of
           this but I'm not sure how to work it into everything else...
        '''
        try:
            query_func = self.query_data.all_notes()
            query_data = dp.extract_note_content(query_func, 'extract_notes.csv', self.dbconn)
            #not this - want a count of the individual things...
            counter = query_data['type'].count()
            print(counter)
        finally:
            #yes? or do I want this to stay open?
            self.dbconn.close_conn()
        return query_data

    #@atl.as_tools_logger(logger)
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
        return (self.dbconn.run_query_list(query_func()))

    #This probably won't work for Dash since it returns a generator
    #Either can create another function just for the dash queries, which is actually probably better
    #since then I can specify optional arguments...
    #@atl.as_tools_logger(logger)
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
        return (self.dbconn.run_query_list(query_func(row)) for row in self.csvfile)


def save_session(session, api_url):
    '''Saves a session that is not yet in the session folder'''
    if 'archivesspace' in api_url:
        fpname = api_url[8:-21]
    elif 'local' in api_url:
        fpname = 'local'
    with open(f'sessions/{fpname}.pkl', 'wb') as out_strm:
        pickle.dump(session, out_strm)
        return f'sessions/{fpname}.pkl'

def load_session(api_url, session_list, session=None, session_file=None):
    '''Loads a session that is already in the session folder'''
    if ('local' in api_url and 'local.pkg' in session_list):
        session_file = 'sessions/local.pkl'
        session = pickle.load(open(session_file, 'rb'))
    else:
        sessions = [(pickle.load(open(f'sessions/{sesh}', 'rb')), f'sessions/{sesh}') for sesh in session_list if api_url[8:-21] == sesh[:-4]]
        if sessions:
            session = sessions[0][0]
            session_file = sessions[0][1]
    return session, session_file

def as_session(api_url, username, password, session=None):
    '''Session handler function'''
    #Searches the session folder to get a list of sessions
    session_list = os.listdir('sessions')
    #run the load session function - if there isn't any session the return values will both be None; if there is a session
    #that value will be returned along with the session filepath
    session, session_file = load_session(api_url, session_list)
    #if there isn't already a session for the API URL, create one and save it
    if (session == [] or session == None):
        try:
            session = requests.Session()
            session.headers.update({'Content_Type': 'application/json'})
            response = session.post(api_url + '/users/' + username + '/login',
                         params={"password": password, "expiring": False})
            if response.status_code != 200:
                print(f"Error could not connect: {response.status_code}")
            else:
                session_toke = json.loads(response.text)['session']
                session.headers['X-ArchivesSpace-Session'] = session_toke
                session_file = save_session(session, api_url)
        except Exception:
            print(traceback.format_exc())
    print(session)
    return session, session_file

def config_file_helper():
    config_file = u.get_config(cfg='as_tools_config.yml')

    with open('as_tools_config.yml', 'r', encoding='utf-8') as config_file:
        cfg = json.load(config_file)
    cfg[config_type] = value
    with open('data/config.json', 'w', encoding='utf-8') as config_file:
        json.dump(cfg, config_file)
    return value

class ASpaceRun():

    def __init__(self):
        '''Need to test what happens if I change a value in the config file...'''
        self.config_file = u.get_config(cfg='as_tools_config.yml')
        self.api_url = self.config_file['api_url']
        self.username = self.config_file['api_username']
        self.password = self.config_file['api_password']
        #is this what I want?
        self.dirpath = u.setdirectory(self.config_file['backup_directory'])
        #this can be changed, the csvdict function will need to be called again
        self.csvfile = u.opencsvdict(self.config_file['input_csv'])
        self.sesh, self.sesh_file = as_session(self.api_url, self.username, self.password)
        self.json_data = ASJsonData()
        self.crud = ASCrud(self.config_file, self.sesh)

    def append_uris_to_record_set(self, record_json, row):
        #Need to fix the CSV dict business now that everything is one...
        if 'uri' in record_json:
            row.update({'uri': record_json['uri']})
        else:
            row.update({'uri': 'NONE'})
        new_row = [v for k, v in row.items()]
        return new_row
    #        this don't work - UPDATE, I THINK I DID FIX IT. MAKE SURE.
    #        Will also need to make sure that what's happening in this func is passed to record set - or do i need to return these things??
    #        row.append(record_json['uri'])
    #        record_set.append(row)

    #@atl.as_tools_logger(logger)
    def exception_handler(self, msg, type, i):
        print(f'Error on row {i}')
        logger.error(f'Error on row {i}')
        if type == 'error':
            logger.error(msg)
        if type == 'exception':
            logger.exception('Error')

    def result_handler(self, record_json, success_counter, i):
        if 'status' in record_json:
            success_counter += 1
            if success_counter in range(0, 50000, 100):
                #DO SOMETHING HERE TO FACILITATE UPDATING THE DASH DASHBOARD.
                pass
        if 'error' in record_json:
            self.exception_handler(record_json.get('error'), 'error', i)
        return success_counter

    #@atl.as_tools_logger(logger)
    def call_api(self, row, row_count, record_set, success_counter, crud_func, json_func):
        '''This is the basic boilerplate loop structure for processing CSV files for use
           in ArchivesSpace API calls. Both the crud and json_data variables should be
           populated by functions from the json_data.py and crud.py files.

           Parameters:
            crud: The CRUD action to take. Populated by crud.py
            json_data: The JSON structure to formulate. Populated by json_data.py

           Todo:
            implement factory method?
        '''
        try:
            if json_func is not None:
                #this will return the JSON response when a record is created or updated
                record_json = crud_func(row, json_func)
                success_counter = self.result_handler(record_json, success_counter, row_count)
                if crud_func.__name__ == 'create_data':
                    new_row = self.append_uris_to_record_set(record_json, row)
                    record_set.append(new_row)
                logger.debug(record_json)
                #print(record_json)
            else:
                record_json = crud_func(row)
                logger.debug(record_json)
                #print(record_json)
                if crud_func.__name__ == 'get_data':
                    record_set.append(record_json)
        except Exception as exc:
            #this isn't right - actually didn't i fix it and just forget to take out this comment...
            self.exception_handler(traceback.format_exc(), 'exception', row_count)
        return (record_set, success_counter)

    def call_api_looper(self, crud_func, json_func=None):
        '''Moving the loop out of the call_api function so the latter can be used elsewhere'''
        record_set = []
        success_counter = 0
        crud_func = getattr(self.crud, crud_func)
        if json_func is not None:
            json_func = getattr(self.json_data, json_func)
        for row_count, row in enumerate(self.csvfile, 1):
            record_set, success_counter = self.call_api(row, row_count, record_set, success_counter, crud_func, json_func)
        if record_set:
            return (record_set, row_count, success_counter)
        else:
            return (row_count, success_counter)
