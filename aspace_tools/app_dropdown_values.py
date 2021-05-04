#!/usr/bin/python3
#~/anaconda3/bin/python

'''This file stores drop-down list values for reporting and bulk operation categories and sub-categories'''
#import dash_bootstrap_components as dbc
#what are the children of dropdown menu items??? So, not really sure if this is what I want
# def create_bootstrap_dropdown():
#     dropdown_menu = dbc.DropdownMenu(
#         label="",
#         children=[dbc.DropdownMenuItem(children=None)]
#
#
#     )
#     return dropdown_menu

template_options = [
{'label': 'Required fields only', 'value': 'required_only'},
{'label': 'Added value fields', 'value': 'added_value'},
{'label': 'All fields', 'value': 'all_fields'}]

archivesspace_instances = [{'label': 'PROD', 'value': 'https://archivesspace.library.yale.edu/api'},
            {'label': 'TEST', 'value': 'https://testarchivesspace.library.yale.edu/api'},
            {'label': 'DEV', 'value': 'https://devarchivesspace.library.yale.edu/api'},
            {'label': 'LOCAL', 'value': 'http://localhost:8089'}]

query_categories = sorted(['Data auditing: YAMS',
                           'Data auditing: MSSA',
                           'Administrative reports',
                           'Descriptive data',
                           'Custom reports',
                           'Statistics',
                           'Bulk queries'])

mssa_query_subcategories = sorted(['Locations',
                                   'Containers',
                                   'Restrictions'])

yams_query_subcategories = sorted(['Containers',
                                   'Notes',
                                   'Restrictions',
                                   'Dates',
                                   'Agents',
                                   'Subjects'])

bulk_operation_categories = sorted(['Create records',
                                    'Update records',
                                    'Delete records',
                                    'Suppress records',
                                    'Link records',
                                    'Merge records',
                                    'Position records',
                                    'Migrate enumerations',
                                    'Get records'])


#SO: not sure about subcategories for API-related things. Might be better to just create some more granular
#top-level categories and update the documentation there. I'm thinking about adding one for common error
#remediation or other common tasks, plus one for creating full finding aids...

# bulk_create_subcategories = sorted(['Create descriptive records',
#                                     'Create collection control records',
#                                     'Create authority records',
#                                     'Create digitization and born-digital tracking records'
#                                         ])
#
# bulk_update_subcategories = sorted(['Create subrecords',
#                                     'Update subrecords',
#                                     'Update records',
#                                     'Remediate common errors'])


#MAYBE just put all the list generating functions here...including the API instance thing,
