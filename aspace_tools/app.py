# -*- coding: utf-8 -*-
import inspect
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash.exceptions
import os
import traceback
import signal
import json
from ast import literal_eval
from collections import deque
from subprocess import Popen, PIPE
import dash_table
import plotly.graph_objs as go
import pprint
import jsonpickle
from pathlib import Path

from utilities import utilities as u

#local imports
from queries import ASQueries
from json_data import ASJsonData
from crud import ASCrud
from templates import ASTemplates
from aspace_run import ASpaceRun, as_session
import app_renderers as renderers
from app_layouts import serve_layout
import app_dropdown_values as dv

import aspace_tools_logging as atl
logger = atl.logging.getLogger(__name__)


config_file = u.get_config(cfg=str(Path.home()) + '/as_tools_config.yml')

app = dash.Dash(__name__)
app.config.suppress_callback_exceptions = True
app.layout = serve_layout

#############################
#### Query App Callbacks ####
#############################

#CAN'T I JUST PUT THE DIVIDER IN THE INPUT DIV???

@app.callback(
    Output('input_div', 'children'),
    [Input('selected_query_dropdown', 'value')],
    [State('query_type_dropdown', 'value')])
def define_inputs(query_name, value):
    if value == 'Custom reports':
        #param_formatted = param
        query_func = getattr(ASQueries, query_name)
        query_vars = [v for v in query_func.__code__.co_varnames if v != 'row']
        input_div_children = [dcc.Input(id=str(param_name), type="text", placeholder=str(param_name), className='input_style') for param_name in query_vars]
        #this change broke everything - need to find another way to do the spacing or another way to get the input value - or both...
        #input_div_children = [[dcc.Input(id=str(param_name), type="text", placeholder=str(param_name), className='input_style'), html.Div(className='divider')] for param_name in query_vars]
        #input_div_children = [item for child in input_div_children for item in child]
        return input_div_children
    if value in ['Data auditing: MSSA', 'Administrative reports', 'Data auditing: YAMS']:
        input_div_children = [dcc.Input(id='pw_input', type='password', placeholder='Enter password', className='input_style')]
        return input_div_children
    if value == 'Bulk queries':
        input_div_children = [dcc.Dropdown(multi=False,
                             id='input_csv_dropdown',
                             placeholder='Select an input CSV',
                             options=[{"label": i, "value": 'data/query_inputs/' + i} for i in os.listdir('data/query_inputs')], className='drop'
                                )
                  ]#, className='dropdown'))
        return input_div_children
    else:
        dash.exceptions.PreventUpdate()

#adding subtypes means i have to redo this; and also the docs...not sustainable; also
@app.callback(
    Output('selected_query_dropdown', 'options'),
    [Input('query_type_dropdown', 'value')])
def update_dropdown(query_type):
    if query_type:
        if query_type == 'Statistics':
            return [{'label': i.replace('_', ' ').capitalize(), "value": i} for i in sorted(renderers.get_count_query_dict(ASQueries))]
        else:
            print(f'query type: {query_type}')
            return [{'label': i.replace('_', ' ').capitalize(), "value": i} for i in sorted(renderers.dict_doc_helper(query_type))]
    else:
        raise dash.exceptions.PreventUpdate()

@app.callback(Output('query_description', 'children'),
    [Input('selected_query_dropdown', 'value')])
def show_query_description(value):
    if value:
        query_func = getattr(ASQueries, value)
        docstring = inspect.getdoc(query_func)
        return html.Div(docstring)
    else:
        raise dash.exceptions.PreventUpdate()


@app.callback(Output('stat_graph', 'figure'),
    [Input('date_slider', 'value')],
    [State('selected_query_dropdown', 'value'),
    State('unzipped_datastore', 'data')])
def update_date_graphs(slider_value, query_value, dataset):
    if dataset:
        if slider_value:
            if ('decade' in query_value or 'century' in query_value):
                #I think this is what I need to update to get t
                if (slider_value[0] in dataset[0] and slider_value[1] in dataset[0]):
                    mindex, maxdex = (dataset[0].index(slider_value[0]), dataset[0].index(slider_value[1]))
                    new_counts = dataset[1][mindex:maxdex]
                    new_years= [row for row in dataset[0] if int(row) >= slider_value[0] and int(row) <= slider_value[1]]
                    return {'data': [go.Bar(x=new_years, y=new_counts)],
                                            # marker={'colors': ['#00356b', '#286dc0', '#63aaff', '#dddddd', '#4a4a4a',
                                            #                    '#222222', '#978d85', 'f9f9f9']}, textinfo='label')],
                            'layout': go.Layout(title=str(query_value).replace('_', ' ').capitalize(), margin={"l": 30, "r": 30})}
                else:
                    raise dash.exceptions.PreventUpdate()
            else:
                raise dash.exceptions.PreventUpdate()
        else:
            raise dash.exceptions.PreventUpdate()
    else:
        raise dash.exceptions.PreventUpdate()

@app.callback([Output('stat_graph_div', 'children'),
    Output('unzipped_datastore', 'data')],
    [Input('query_result', 'data')],
    [State('selected_query_dropdown', 'value'),
     State('query_type_dropdown', 'value')])
def get_graph(dataset, query_value, query_type):
    if query_type == 'Statistics':
        if dataset:
            unzipped_dataset = list(zip(*dataset[1]))
            if ('decade' in query_value or 'century' in query_value):
                min_year = min(unzipped_dataset[0])
                max_year = max(unzipped_dataset[0])
                return [renderers.create_bar_graph(query_value, unzipped_dataset),
                        html.Div(dcc.RangeSlider(id='date_slider',
                        #can't get the damn 2010 dates to actually show up...
                                   min=min_year,
                                   max=max_year,
                                   value=[20, 2010],
                                   step=10,
                                   pushable=50,
                                   allowCross=False,
                                   marks={str(i): str(i) for i in range(0, max_year + 50, 50)}, updatemode='drag'
                                   ), style={'width': '60%', 'margin': 'auto', 'padding': '5px'})], unzipped_dataset
            else:
                return dcc.Graph(id='stat_graph',
                                 style={'width': '60%', 'margin': '20px auto', 'color': 'black',
                                        'border-style': 'groove', 'border-color': '#eceef0', 'background-color': 'background-color',
                                        'font-family': 'Mallory-Book'},
                                 figure={
                                     'data': [go.Pie(labels=list(unzipped_dataset[0]), values=list(unzipped_dataset[1]),
                                                    marker={'colors': ['#00356b', '#286dc0', '#63aaff', '#dddddd', '#4a4a4a',
                                                                       '#222222', '#978d85', 'f9f9f9']}, textinfo='label')],
                                     'layout': go.Layout(title=str(query_value).replace('_', ' ').capitalize(), margin={"l": 30, "r": 30})}), unzipped_dataset
        else:
            raise dash.exceptions.PreventUpdate()
    else:
        raise dash.exceptions.PreventUpdate()

#'pw_input', 'value'
#'input_csv_dropdown', 'value'

@app.callback([Output('query_table', 'children'),
    Output('download-link', 'children'),
    Output('number-of-results', 'children'),
    Output('query_result', 'data')],
    [Input('go_time_query', 'n_clicks')],
    [State('selected_query_dropdown', 'value'),
    State('query_type_dropdown', 'value'),
    State('input_div', 'children')])
def run_query(n_clicks, query_value, query_type, input_vals, dataset=None):
    if n_clicks > 0:
        if query_value:
            query_func = getattr(ASQueries, query_value)
            if query_type == 'Bulk queries':
                dataset = renderers.input_query_helper(query_func, input_vals, renderers.run_bulk_queries)
            if query_type == 'Custom reports':
                dataset = renderers.input_query_helper(query_func, input_vals, renderers.run_custom_reports)
            if query_type in ['Data auditing: MSSA', 'Administrative reports', 'Data auditing: YAMS']:
                dataset = renderers.input_query_helper(query_func, input_vals, renderers.run_password_protected_queries)
            if query_type not in ['Bulk queries', 'Custom reports', 'Data auditing: MSSA', 'Administrative reports', 'Data auditing: YAMS']:
                try:
                    dataset = renderers.get_data(query_func)
                except:
                    import traceback
                    print(traceback.format_exc())
                    raise dash.exceptions.PreventUpdate()
            result_total, datasets = renderers.process_results(dataset)
            return renderers.generate_table(dataset), html.A('Click to download report', download="as_data.csv", href=renderers.generate_csv(dataset), target="_blank"), html.Div(result_total), [list(dataset.columns), datasets]
        else:
            raise dash.exceptions.PreventUpdate()
    else:
        raise dash.exceptions.PreventUpdate()

###########################
#### API App Callbacks ####
###########################

@app.callback(
    Output('function_dropdown', 'options'),
    [Input('bulk_operation_category_dropdown', 'value')])
def update_api_dropdown(function_cat):
    if function_cat:
        if function_cat == 'Create records':
            return [{'label': i.replace('_', ' ').capitalize(), "value": i} for i in sorted(renderers.get_create_functions())]
        if function_cat == 'Update records':
            return [{'label': i.replace('_', ' ').capitalize(), "value": i} for i in sorted(renderers.get_update_functions())]
        if function_cat == 'Delete records':
            return [{'label': i.replace('_', ' ').capitalize(), "value": i} for i in sorted(renderers.get_function_helper(ASCrud, 'delete'))]
        if function_cat == 'Link records':
            return [{'label': i.replace('_', ' ').capitalize(), "value": i} for i in sorted(renderers.get_function_helper(ASJsonData, 'link'))]
        if function_cat == 'Merge records':
            return [{'label': i.replace('_', ' ').capitalize(), "value": i} for i in sorted(renderers.get_function_helper(ASCrud, 'merge'))]
        if function_cat == 'Position records':
            return [{'label': i.replace('_', ' ').capitalize(), "value": i} for i in sorted(renderers.get_function_helper(ASCrud, 'position'))]
        if function_cat == 'Suppress records':
            return [{'label': i.replace('_', ' ').capitalize(), "value": i} for i in sorted(renderers.get_function_helper(ASCrud, 'suppress'))]
        if function_cat == 'Migrate enumerations':
            return [{'label': i.replace('_', ' ').capitalize(), "value": i} for i in sorted(renderers.get_function_helper(ASCrud, 'migrate'))]
        if function_cat == 'Get records':
            return [{'label': i.replace('_', ' ').capitalize(), "value": i} for i in sorted(renderers.get_function_helper(ASCrud, 'get'))]
        else:
            raise dash.exceptions.PreventUpdate()
    else:
        raise dash.exceptions.PreventUpdate()

# @app.callback(
#     Output('function_dropdown', 'options'),
#     [Input('function_subcategory_dropdown')]
# )
# def update_api_subcategory_dropdown(function_cat):
#     if function_cat:
#         pass
#     else:
#         raise dash.exceptions.PreventUpdate()

@app.callback(
    [Output('api_table', 'children'), Output('operation-docs', 'children')],
    [Input('function_dropdown', 'value')])
def show_schema_docs(value):
    '''Shows function docs'''
    if value:
        if ('merge' in value or 'position' in value or 'suppress' in value or 'migrate' in value or 'get' in value):
            func = getattr(ASCrud, value)
        else:
            func = getattr(ASJsonData, value)
        #IS IT ALSO POSSIBLE TO RETURN A BUTTON HERE??? LIKE TO UPDATE??
        return (func.__doc__, 'Details:')
    else:
        raise dash.exceptions.PreventUpdate()

#I wonder if it would also be possible to use jsonpickle to store the as_run object.
#Something like if as_run != None, then start it on up.

#INTERESTINGLY, I no longer actually change the config file when I do this - that's why api_url_2
#continues to be production archivesspace. It should change when I select a new one but I don't think it is.
#I do still want it to do that so I will need to figure out how. But for now
#will just worry about

@app.callback(
    [Output('session_store', 'data'),
     Output('object_store', 'data')],
    [Input('api_instance_checklist', 'value')],
    [State('session_store', 'data'),
     State('object_store', 'data')])
def select_api_instance(value, sesh_store, obj_store, config_file=config_file):
    #need to actually have it modify the config file - I removed that at some point
    #also will need to have the login function work properly. Or just remove it. Who knows.
    #But right now the usernames are pulled from the config file and can't be changed
    #by the login box
    '''Modifies the config file to a user-selected ArchivesSpace instance'''
    print('\n')
    if value:
        print(f'api_value_1: {value}')
        if obj_store:
            print(f'input_value: {value}')
            if value in obj_store:
                print(f'session already exists: {value}')
                #is this necessary? sould have already instantiated this with the other config...
                #renderers.config_file_helper(value, 'api_url')
                #as_run = jsonpickle.decode(obj_store[value])
                as_run = obj_store[value]
                print(type(as_run))
            else:
                print(f'starting new session: {value}')
                renderers.config_file_helper(value, 'api_url')
                as_run = jsonpickle.encode(ASpaceRun())
                obj_store[value] = as_run
                print(type(as_run))
            # print(f'as_run_value: {as_run.api_url}')
            # #I thought that this was supposed to match the default value. but it doesn't?
            # if value != as_run.api_url:
            #     as_run.api_url = value
            #     renderers.config_file_helper(value, 'api_url')
            #     print(f'api_value_3: {as_run.api_url}')
            #     if as_run.api_url in sesh_store:
            #         print(f'session exists: {value}')
            #         test_decode = jsonpickle.decode(sesh_store[as_run.api_url])
            #         obj_store = jsonpickle.encode(as_run)
            #         print(test_decode)
            #     else:
            #         print(f'starting new session: {value}')
            #         as_run.sesh = as_session(api_url=as_run.api_url, username=as_run.username, password=as_run.password)
            #         sesh_store[as_run.api_url] = jsonpickle.encode(as_run.sesh)
            #         obj_store = jsonpickle.encode(as_run)
            # else:
            #     print('value equals as_run api value')
            #     print(value)
            #     print(as_run.api_url)
            #     raise dash.exceptions.PreventUpdate()
        else:
            obj_store = {}
            print(f'starting new session: {value}')
            renderers.config_file_helper(value, 'api_url')
            as_run = jsonpickle.encode(ASpaceRun())
            obj_store[value] = as_run
            print(type(as_run))
        #so maybe have the object store be the entire store of objects, and the sesh store be any one of those objects...
        return as_run, obj_store
    else:
        raise dash.exceptions.PreventUpdate()

def test_sesh(sesh_store):
    # for key, value in sesh_store.items():
    #     print(f'instance: {key}')
    lit_value = json.loads(sesh_store)
    print(lit_value)
    # headers = lit_value['py/state']['headers']['_store']['py/reduce']
    # for item in headers:
    #     print(item)

# @app.callback(
#     Output('selected_0', 'data'),
#     [Input('password_input', 'value'),
#     Input('username_input', 'value'),
#     Input('login_button', 'n_clicks')])
# def log_in_to_api(password, username, n_clicks):
#     '''Modifies the config file to a user-selected ArchivesSpace password'''
#     if value:
#         return rend.config_file_helper(value, 'api_password')
#     else:
#         raise dash.exceptions.PreventUpdate()


@app.callback(
    Output('selected_1', 'data'),
    [Input('input_file_dropdown', 'value')])
def select_input_file(value):
    '''Modifies the config file to a user-selected backup directory'''
    if value:
        return renderers.config_file_helper(value, 'input_csv')
    else:
        raise dash.exceptions.PreventUpdate()

@app.callback(
    Output('selected_2', 'data'),
    [Input('backup_folder_dropdown', 'value')])
def select_backup_directory(value):
    '''Modifies the config file to a user-selected backup directory.'''
    if value:
        return renderers.config_file_helper(value, 'backup_directory')
    else:
        raise dash.exceptions.PreventUpdate()

@app.callback(Output('output-storage', 'data'),
     [Input('go_time', 'n_clicks'), Input('stop_time', 'n_clicks'),
     Input('are_you_surrre', 'submit_n_clicks')],
     [State('backup_folder_dropdown', 'value'),
     State('input_file_dropdown', 'value'),
     State('function_dropdown', 'value'),
     State('session_store', 'data')])
def run_functions(n_clicks, s_clicks, confirm, backup_dir, input_file, function_name, sesh_store):
    #what might be the use of using state for the clicks here??
    if sesh_store:
        as_run = jsonpickle.decode(sesh_store)
        print(as_run.sesh)
        if not confirm:
            raise dash.exceptions.PreventUpdate()
        else:
            n_clicks += 1
            if n_clicks > 0 and s_clicks == 0:
                if backup_dir and input_file and function_name:
                    try:
                        #this is repetitive
                        as_run.csvfile = u.opencsvdict(input_file)
                        record_set = []
                        success_counter = 0
                        row_counter = 0
                        #don't actually use the pid variable anymore because of this while loop - am I sure this works?
                        #also seem to have removed the log file print stuff...
                        while as_run.csvfile:
                            row = next(as_run.csvfile)
                            print(row)
                            print(function_name)
                            if function_name in dir(as_run.crud):
                                record_set, success_counter = as_run.call_api(row, row_counter, record_set, success_counter, crud_func=getattr(as_run.crud, function_name))
                            elif function_name in dir(as_run.json_data):
                                #I think the problem is with the getattr
                                if (inspect.getdoc(getattr(as_run.json_data, function_name)) and 'tuple: ' in inspect.getdoc(getattr(as_run.json_data, function_name))):
                                    record_set, success_counter = as_run.call_api(row, row_counter, record_set, success_counter, crud_func=getattr(as_run.crud, 'create_data'), json_func=getattr(as_run.json_data, function_name))
                                #is this right? Maybe I want the link and stuff to be in this...
                                elif (inspect.getdoc(getattr(as_run.json_data, function_name)) and 'dict: ' in inspect.getdoc(getattr(as_run.json_data, function_name))):
                                    record_set, success_counter = as_run.call_api(row, row_counter, record_set, success_counter, crud_func=getattr(as_run.crud, 'update_data'), json_func=getattr(as_run.json_data, function_name))
                            if s_clicks > 0 and n_clicks > 0:
                                return html.Div('')
                    except Exception:
                        print(traceback.format_exc())
            else:
                raise dash.exceptions.PreventUpdate()
    else:
        raise dash.exceptions.PreventUpdate()

@app.callback([Output('display_log', 'children'), Output('log-update', 'interval')],
    [Input('go_time', 'n_clicks'), Input('stop_time', 'n_clicks'), Input('log-update', 'n_intervals')],
    [State('log-update', 'interval')])
def display_log(n_clicks, s_clicks, n_intervals, the_interval):
    if n_clicks:
        with open('logs/debug.log', 'r', encoding='utf-8') as lfile:
            last_30 = deque(lfile, 30)
            if (s_clicks == 0 and n_clicks > 0):
                return html.Div(list(last_30)), 1000
            if (s_clicks == 0 and n_clicks == 0):
                return html.Div(''), 2147483647
            if (s_clicks > 0 and n_clicks > 0):
                return html.Div(list(last_30)), 2147483647
    else:
        raise dash.exceptions.PreventUpdate()

################################
#### Template App Callbacks ####
################################

@app.callback([
    Output('schema_dropdown', 'options'),
    Output('as_templates_store', 'data')],
    [Input('all-tabs', 'value')],
    [State('as_templates_store', 'data'),
     State('object_store', 'data')])
def update_schema_dropdown(tabs, as_templates_store, obj_store):
    #this is problematic, actually - since it can't be used until an instance is selected in the bulk operations tab.
    #will fix that later
    if obj_store:
        if tabs:
            if tabs == 'template_tab':
                if not as_templates_store:
                    templates = ASTemplates(as_sesh)
                    as_templates = templates.parse_schemas()
                    print(f'Connected to {t.api_url}')
                    schema_names = [{'label': key.replace('_', ' '), 'value': key} for key in sorted(as_templates.keys()) if 'abstract' not in key]
                    return schema_names, as_templates
                else:
                    raise dash.exceptions.PreventUpdate()
            else:
                raise dash.exceptions.PreventUpdate()
        else:
            raise dash.exceptions.PreventUpdate()
    else:
        raise dash.exceptions.PreventUpdate()

@app.callback([
    Output('template_table', 'children'),
    Output('json_table', 'children'),
    Output('download_links', 'children')],
    [Input('go_time_schema', 'n_clicks')],
    [State('schema_dropdown', 'value'),
     State('as_templates_store', 'data')])
def show_schema_json(n_clicks, value, as_templates):
    if n_clicks > 0:
        if value:
            json_template = json.dumps(as_templates[value], indent=4, sort_keys=True)
            csv_template = renderers.download_csv_template(as_templates[value])
            put_it_in_the_div = [html.A('Download JSON', id='json_link', href=renderers.generate_json(as_templates[value]), download="template.json", target="_blank"),
                                 html.Div(className='divider'),
                                 html.Div(className='divider'),
                                 html.A('Download CSV', href=renderers.generate_template_csv(csv_template), download="template.csv", target="_blank")]
            return json_template, renderers.generate_table_from_json(as_templates[value]), put_it_in_the_div
        else:
            raise dash.exceptions.PreventUpdate()
    else:
        raise dash.exceptions.PreventUpdate()

if __name__ == '__main__':
    app.run_server(debug=True)
