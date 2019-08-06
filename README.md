# aspace-tools

A Python interface for doing stuff with the ArchivesSpace API and MySQL database, usually with CSV files.

NOTE: THESE DOCS - AND THE ENTIRE MODULE - ARE STILL IN PROGRESS

## Requirements

* Python 3.7+
* `utilities` package (will also install a few other dependencies)

## Installation

```
$ cd /path/to/package
$ pip install .

```

## Package Structure/API Documentation

```
aspace-tools
│   README.md
│   LICENSE.txt
│   MANIFEST.in
│   setup.py    
│
└───aspace-tools
    │   __init__.py
    |   aspace-api.py
    |   aspace-db.py
    │   aspace_tools.py
    │   crud.py
    │   json_data.py
    │   queries.py
    │   templates.py
    |   data_processing.py
    |   aspace_tools_logging.py
    |   aspace_tools_tests.py
    |   as_tools_config.yml (this is a blank template; once filled out should be moved to home directory)
    │
    └───standalone_scripts
    |   └───python
    │   |      asnake_implement.py
    |   |      calculate_extents.py
    |   |      create_digital_objects.py
    |   |      create_events.py
    |   |      create_file_versions.py
    |   |      create_hm_external_ids.py
    |   |      create_local_restrictions.py
    |   |      create_redaction_notes.py
    |   |      create_use_surrogate_notes.py
    |   |      delete_records.py
    |   |      delete_rights_restrictions.py
    |   |      get_note_content.py
    |   |      login.py
    |   |      merge_records.py
    |   |      project_indexes.py
    |   |      re-order_digital_objects.py
    |   |      re-position_enumeration_values.py
    |   |      unpublish_notes.py
    |   |      update_agent_sources_auth_ids.py
    |   |      update_hm_microfilm.py
    |   |      update_inventory_archival_objects.py
    |   |      update_location_coordinates.py
    |   |      update_notes.py
    |   |      update_primary_names.py
    |   |      update_subrecord_component.py
    |   |      update_subrecord_components.py
    |   |      update_subrecords.py
    |   |      update_top_containers.py
    |   |
    |   └───sql
    │   |      all_accessrestrict_notes.sql
    │   |      all_userestricts_notes.sql
    │   |      copyright_issues_access_notes.sql
    │   |      hm_restrictions_external_ids.sql
    │   |      local_access_restrictions_rus.sql
    │   |      mssa_accessions_2015-2019.sql
    │   |      mssa_acquisitions_by_fy.sql
    │   |      rights_restriction_count.sql
    │   |      staff_ui_urls.sql
    |
    └───implementations
    │      music_data.py
    │
    └───templates
    │
    └───logs
    |      logging_config.yml    
    │
    └───fixtures
           as_schema_data.py
           property_exclusions.csv (does the file path need to be changed in templates.py?)
           schema_exclusions.csv (same as above)
           schemas.json
```

This package adopts a modular, plugin-type style that easily can be extended to include other functions. The structure of this package eliminates a significant amount of repeated code in standalone ArchivesSpace API scripts.

##### `apispace.py`

 The main functions are stored in `apispace.py`, which serves as the primary user interface for the package.

`apispace.py` includes two functions:

`call_api(api_url, headers, csvfile, dirpath=None, action=None, data_struct=None)`

This function establishes the basic loop structure of a call to the ArchivesSpace API.

```
def call_api(api_url, headers, csvfile, dirpath=None, crud=None, json_data=None):
    record_set = []
    for i, row in enumerate(csvfile, 1):
        try:
            if data_struct != None:
                record_json = crud(api_url, headers, row, dirpath, json_data)
                if action == create_data:
                    if 'uri' in record_json:
                        row.append(record_json['uri'])
                        record_set.append(row)
                print(record_json)
            else:
                record_json = crud(api_url, headers, row)
                print(record_json)
                if action == get_data:
                    record_set.append(record_json)
            if 'error' in record_json:
                print(f'Error on row {i}')
                print(record_json.get('error'))
        except Exception as exc:
            print(f'Error on row {i}')
            print(traceback.format_exc())
    if record_set:
        return record_set

```

The function is called directly by the end-user's implementation and takes the following arguments:

* `api_url`: the URL for the ArchivesSpace API
* `headers`: authentication for the ArchivesSpace API
* `csvfile`: a CSV file containing URIs and other data to be processed
* `dirpath`: a directory path for any backups to be stored.
* `crud`: the CRUD action to be taken. All of the CRUD functions are stored in `crud.py`
* `json_data`: JSON data structures for create and update functions are formed from the CSV input file using functions which are stored `json_data.py`

As noted, the `crud` and `json_data` arguments are populated by functions from the `crud.py` and `json_data.py` files.

`run_db_queries(dbconn, csvfile, query_action)`

This function runs multiple database queries based on an input CSV file. Query functions are stored in the `queries.py` file. To run a single query, just use the `dbssh.py` file in the `utilities` module.

##### `crud.py`

This file holds all of the CRUD-related functions that are used in the `process` function.

`update_data(api_url, headers, row, dirpath, funct)`

Takes a JSON structure from `json_data.py` as input

`update_parent(api_url, headers, row, dirpath)`

Updates the parent and position of an archival objects record.

`merge_data(api_url, headers, row, dirpath, record_type)`

Merges two records.

`create_data(api_url, headers, row, _, funct)`

Takes a JSON structure from `json_data.py` as input.

`delete_data(api_url, headers, row, dirpath)`

`get_nodes(api_url, headers, row)`

`get_data(api_url, headers, row)`

##### `json_data.py`

This file holds all JSON data structures which are used in create, update, and delete functions

##### `queries.py`

This file holds all query strings and query functions used in the `run_db_query` and `run_db_queries` functions in `apispace.py`

##### `templates.py`

This file compiles JSON and CSV templates using the ArchivesSpace schema

## Tutorial

To run a basic API update using `apispace.py`, do the following:

```
$ python
Python 3.7.3 (default, Mar 27 2019, 16:54:48)
[Clang 4.0.1 (tags/RELEASE_401/final)] :: Anaconda custom (64-bit) on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> from apispace import apispace, crud, json_data
>>> from utilities import utilities as u
>>> api_url, headers = u.login(url=url, username=username, password=password)
>>> _, csvfile = u.opencsv(input_csv='path/to/csvfile.csv')
>>> dirpath = u.setdirectory('/path/to/output/directory')
>>> apispace.process(api_url, headers, csvfile, dirpath=dirpath, action=crud.update_data, data_struct=json_data.update_notes)
```

To run a single database query, do:

```
>>> from apispace import apispace, queries
>>> from utilities import dbssh, utilities
>>> dbconn = dbssh.DBConn()
>>> dirpath = utilities.set_directory('/path/to/folder')
>>> query_data = apispace.run_db_query(dbconn, queries.get_extent_types, dirpath=dirpath)
```

Note: requires a configuration file, `config.yml` with database connection data. Can also use the `db` file in `utilities` package to connect without SSH.

To run multiple database queries using a CSV as input, do:

```
>>> from apispace import apispace, queries
>>> from utilities import dbssh
>>> dbconn = dbssh.DBConn()
>>> _, csvfile = utilities.opencsv('/path/to/csvfile.csv')
>>> query_data = apispace.run_db_queries(dbconn, csvfile, queries.get_distinct_creators)
```

To compile JSON and CSV templates, do:

```
```
