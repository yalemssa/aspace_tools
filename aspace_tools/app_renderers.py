#!/usr/bin/python3
#~/anaconda3/bin/python

import inspect
import urllib
import yaml
import os
import traceback
from os.path import expanduser
from pathlib import Path
import json
import time
import pandas as pd
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objs as go

#from utilities import dbssh
#using the local database for testing
from utilities import db as dbssh

from queries import ASQueries
from json_data import ASJsonData
from aspace_run import ASpaceDB
import app_dropdown_values as dv


'''
This file contains functions which populate drop-down lists and generate HTML elements for the layout
Also stores the functions which run SQL queries and populate SQL and JSON tables.

Will probably move the layout stuff to a different file soon.
'''

#should pass in config file here...otherwise it looks for the utilities module config file...
def get_data(query_func, inputs=None, csvdata=False, result=None):
    try:
        as_db = ASpaceDB()
        if csvdata is True:
            result = as_db.run_db_queries(query_func)
            result = process_bulk_query_data(result)
            result = pd.DataFrame(result)
        else:
            if inputs is not None:
                print(inputs)
                query = query_func(inputs)
            else:
                query = query_func()
            result = as_db.dbconn.run_query_df(query)
    except Exception as exc:
        print(traceback.format_exc(exc))
    finally:
        print('Closing connection')
        as_db.dbconn.close_conn()
    return result

def run_bulk_queries(query_func, input_vals):
    #this seems....tenuous; but works for now
    csv_selection = input_vals[0]['props']['options'][0]['value']
    config_file_helper(csv_selection, 'input_csv')
    return get_data(query_func, csvdata=True)

def run_custom_reports(query_func, input_vals):
    #this seems....tenuous; but works for now
    combined_input_values = [input_value['props']['value'] for input_value in input_vals]
    print(f'Combined input values: {combined_input_values}')
    return get_data(query_func, inputs=combined_input_values)

def run_password_protected_queries(query_func, input_vals):
    #ultimately could define this password somewhere else
    if input_vals[0]['props']['value'] == 'grant_to_mssa':
        return get_data(query_func)

def input_query_helper(query_func, input_vals, run_query_func):
    if input_vals:
        try:
            return run_query_func(query_func, input_vals)
        except:
            import traceback
            print(traceback.format_exc())
            return
    else:
        raise dash.exceptions.PreventUpdate()

def process_results(dataset):
    if len(dataset) > 2000:
        result_total = f'Showing 1-2000 of {len(dataset)} results.'
    else:
        result_total = f'{len(dataset)} results.'
    #is this where this should be?
    datasets = dataset.values.tolist()
    if [None, 0] in datasets:
        datasets.remove([None, 0])
    return result_total, datasets

##############################
#### Query App Functions #####
##############################

# def get_query_dict(queries):
#     return [item for item in dir(queries)
#             if (item != 'atl' and item != 'logger' and not item.startswith('__') and 'count_helper' not in item)]

def download_csv_template(jsontemplatedict):
    '''
    Goal is to create the JSON templates, and then convert those to CSV file that can
    be used to create either full finding aids/top level records, or to update subrecords
    in bulk

    Should really re-do this
    '''
    #fileob = open('templates/' + jsontemplatedict['jsonmodel_type'] + '.csv', 'a', encoding='utf-8', newline='')
    #csvout = csv.writer(fileob)
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
                pass
                #print(key, value)
        else:
            subfield_list.append(key)
    #csvout.writerow(subfield_list)
    #fileob.close()
    return subfield_list

#Wrapper loop to create all templates
#Want to remove the schema name from the template header
#also remove the jsonmodel type
def download_csv_templates(jsontemplates):
    for template_key, template_value in jsontemplates.items():
        download_csv_template(template_value)

def get_count_query_dict(queries):
    return [item for item in dir(ASQueries)
            if 'count' in item]

def dict_doc_helper(type_name):
    return [item for item in dir(ASQueries)
            if inspect.getdoc(getattr(ASQueries, item)) is not None and
            type_name in inspect.getdoc(getattr(ASQueries, item))]

def process_bulk_query_data(results):
    return (row for result in results
            for row in result)

###########################
#### API APP Functions ####
###########################

def get_function_subcategories():
    #could this be used for the query and the bulk update stuff? How do I abstract all the values...
    dv.bulk_create_subcategories
    dv.bulk_update_subcategories
    dv.yams_query_subcategories
    dv.mssa_query_subcategories
    pass


#create things return a tuple:
def get_create_functions():
    return [item for item in dir(ASJsonData)
            if (inspect.getdoc(getattr(ASJsonData, item)) and 'tuple: ' in inspect.getdoc(getattr(ASJsonData, item)))]

#update things return a dict:
def get_update_functions():
    #not sure if this will work if there is no docstring...wasn't working before.
    return [item for item in dir(ASJsonData)
           if (inspect.getdoc(getattr(ASJsonData, item)) and 'dict: ' in inspect.getdoc(getattr(ASJsonData, item)))
           and 'link' not in item and 'delete' not in item and 'get' not in item]

def get_function_helper(mod, qual):
    return [item for item in dir(mod)
            if qual in item]

# def get_files(self, fp):
#     return os.listdir(fp)
#
# def get_folders(self, fp):
#     return next(os.walk(fp))[1]

def config_file_helper(value, config_type):
    homedir = expanduser("~")
    fp = open(homedir + '/as_tools_config.yml', 'r', encoding='utf-8')
    cfg_file = yaml.load(fp, Loader=yaml.FullLoader)
    cfg_file[config_type] = value
    fpout = open(homedir + '/as_tools_config.yml', 'w', encoding='utf-8')
    yaml.dump(cfg_file, fpout)
    fp.close()
    return cfg_file[config_type]


#############################
#### Rendering Functions ####
#############################

def create_bar_graph(query_value, dataset):
    return dcc.Graph(id='stat_graph',
                      style={'width': '60%', 'margin': '20px auto', 'color': 'black',
                            'border-style': 'groove', 'border-color': '#eceef0', 'background-color': 'background-color',
                            'font-family': 'Mallory-Book'},
                      figure={
                         'data': [go.Bar(x=list(dataset[0]), y=list(dataset[1]))],
                                        # marker={'colors': ['#00356b', '#286dc0', '#63aaff', '#dddddd', '#4a4a4a',
                                        #                    '#222222', '#978d85', 'f9f9f9']}, textinfo='label')],
                         'layout': go.Layout(title=str(query_value).replace('_', ' ').capitalize(), margin={"l": 30, "r": 30})})

def generate_table_from_json(json_template):
    #if it is a list it is repeatable - make sure to note this; would also like to note required
    #fields though not sure how to do that yet...especially subrecords like dates and extents in resourced
    from operator import itemgetter
    top_level_keys = []
    for key, value in json_template.items():
        if type(value) is list:
            #maybe for now just do a check on the first value
            if type(value[0]) is str:
                top_level_keys.append([key, str(value)])
            elif type(value[0]) is dict:
                sub_record_keys = []
                try:
                    for item in value:
                        for k, v in item.items():
                            sub_record_keys.append([k, str(v)])
                except AttributeError:
                    print(item)
                sub_record_keys = sorted(sub_record_keys, key=itemgetter(0))
                top_level_keys.append([key, str(sub_record_keys)])
            else:
                pass
        else:
            top_level_keys.append([key, str(value)])
    top_level_keys = sorted(top_level_keys, key=itemgetter(0))
    nested_table = generate_nested_table(top_level_keys)
    final_table = generate_transposed_table_not_df(nested_table)
    return final_table

def generate_nested_table(nested_json_list):
    for row in nested_json_list:
        if '[[' in row[1]:
            #i think i actually need to use literal eval here
            from ast import literal_eval
            row[1] = generate_transposed_table_not_df(literal_eval(row[1]))
    return nested_json_list

def generate_table_not_df(dataframe, max_rows=2000):
    return html.Table(
        # Header
        [html.Tr([html.Th(column[0]) for column in dataframe])] +

        # Body
        [html.Tr([html.Td(column[1]) for column in dataframe])],
    )

def generate_transposed_table_not_df(self, dataframe, max_rows=2000):
    return html.Table(
        # Header
        [html.Tr([html.Th(column[0]), html.Td(column[1])]) for column in dataframe]
    )

def generate_table(dataframe, max_rows=2000):
    return html.Table(
        # Header
        [html.Tr([html.Th(column) for column in dataframe.columns])] +

        #I am guessing here that I can add something so the nested tables will
        #display correctly

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][column], className='table-cell') for column in dataframe.columns
            #this is where I can maybe do a nested list comprehension
            #for
        ]) for i in range(min(len(dataframe), max_rows))]
    , className='query-table')

def generate_csv(dataframe):
    csv_string = dataframe.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8,%EF%BB%BF" + urllib.parse.quote(csv_string)
    return csv_string

def generate_template_csv(template_data):
    blank_dataframe = pd.DataFrame(data=None, columns=template_data)
    csv_string = blank_dataframe.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8,%EF%BB%BF" + urllib.parse.quote(csv_string)
    return csv_string

def generate_json(json_bit):
    json_string = json.dumps(json_bit, indent=4, sort_keys=True)
    json_string = "data:application/json;charset=utf-8,%EF%BB%BF" + urllib.parse.quote(str(json_string))
    return json_string
