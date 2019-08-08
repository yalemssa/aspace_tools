# ArchivesSpace Tools

`aspace_tools` is a Python package and command-line interface for interacting with the ArchivesSpace API and MySQL database, usually using CSV files as input and output.

## Requirements

* Python 3.7+
* [utilities](https://github.com/ucancallmealicia/utilities) package, which will also install a several other dependencies: `pandas`, `bs4`, `requests`, `pymysql`, `paramiko`, and `sshtunnel`
* Read/write access to ArchivesSpace API and/or database

## Installation

```
$ cd /path/to/package
$ pip install .
```

## Package Overview/Tutorial

This package is organized into several modules, which allows for easy extensibility and limits the repetition of boilerplate code.

`aspace_tools` can either be imported into a Python file or interactive interpreter, or run on the command line using the the `aspace_api.py` and `aspace_db.py` interfaces.

To get started, configure your API and database login information, set a backup directory, and define your input/output CSV file paths by filling in the appropriate fields in the included `as_tools_config.yml` template file, and move the file to your home directory.

##### `aspace_api.py`

This is the primary command-line interface for interaction with the ArchivesSpace API. It is called with two required arguments: 1.) the `crud.py` function to be called, i.e. `create_data`, `update_data` 2.) The `json_data.py` function to be called, i.e. `create_archival_objects`

To run a basic API update using `aspace_api.py`, do the following:

```
$ ./aspace_api.py update_data update_primary_names
```

```
$ ./aspace_api.py update_enum_position
```

If running the `update_record_components` function, an additional argument is required to specify the field to be updated, i.e. `level`. The `update_subrecord_components` function requires two additional arguments, the subrecord type, i.e. `extent`, and the field to be updated, i.e. `extent_type`. If running the `merge_records` function, a third argument is required to specify the record type, i.e. `agent`.

Examples:

```
$ ./aspace_api.py merge_data agent
```

```
$ ./aspace_api.py update_data update_record_component level
```

```
$ ./aspace_api.py update_data update_subrecord_component extent extent_type
```

See the `crud.py` and `json_data.py` API documentation to see which fields are required in each CSV input file.

##### `aspace_db.py`

This is the primary command-line interface for interaction with the ArchivesSpace MySQL database. It is called with two required arguments: 1.) Whether to run the `run_db_query` function or the `run_db_queries` function 2.) The `queries.py` file to be called, i.e. `get_access_notes`

To run a single database query from `queries.py`, do:

```
$ ./aspace_db.py run_db_query get_all_microfilm
```

To run multiple database queries using a CSV as input, do:

```
$ ./aspace_db.py run_db_queries get_accessrestrict_notes
```

##### `aspace_run.py`

This file contains three functions which provide the basic scaffolding for the other modules. The   `call_api` function is a loop which processes each line of an input CSV that is defined in the `aspace_tools_config.yml` file. This is the primary function that is called in `aspace_api.py` and will be the primary function used if importing the package into another `.py` file or an interactive interpreter.

```
def call_api(api_url, headers, csvfile, dirpath=None, crud=None, json_data=None):
    record_set = []
    for i, row in enumerate(csvfile, 1):
        try:
            if json_data != None:
                # the crud function selected by the user is called, and the
                # json_data function selected by the user is passed to the crud function
                record_json = crud(api_url, headers, row, dirpath, json_data)
                if crud.__name__ == 'create_data':
                    append_uris_to_record_set(row, record_json, record_set)
                print(record_json)
            else:
                record_json = crud(api_url, headers, row, dirpath)
                print(record_json)
                if crud.__name__ == 'get_data':
                    record_set.append(record_json)
            if 'error' in record_json:
                exception_handler(record_json.get('error'), 'error')
        except Exception as exc:
            exception_handler(traceback.format_exc(), 'exception')
    if record_set:
        return record_set
  ```

The function takes several arguments. The `api_url`, `headers`, `csvfile`, and `dirpath` arguments can all be stored in the `as_tools_config.yml` file. The `crud` and `json_data` arguments are populated with functions from the `crud.py` and `json_data.py` files.

_NOTE_: Not all `crud` functions take a `json_data` function as an argument.

Example usage:

```
def main(result=None):
    home_dir = str(Path.home())
    config_file = u.get_config(cfg=home_dir + '/as_tools_config.yml')
    dirpath = u.setdirectory(config_file['backup_directory'])
    csvfile = u.opencsvdict(config_file['input_csv'])
    api_url, headers = u.login(url=config_file['api_url'], username=config_file['api_username'], password=config_file['api_password'])
    result = aspace_run.call_api(api_url, headers, csvfile, dirpath=dirpath, crud=crud.create_data, json_data=json_data.create_archival_objects)
    return result
```
See the [implementations](https://github.com/yalemssa/aspace-tools/tree/master/aspace_tools/implementations) sub-folder for more examples.

`aspace_run.py` also contains two functions for interacting with the ArchivesSpace MySQL database.

`run_db_query` will run a single query. Many queries can be called from the `queries.py` file, though it is also possible to pass in a standalone `.sql` file.

```
def run_db_query(dbconn, query_func, outfile=None):
    return (dbconn.run_query_list(query_func))
```

Example usage:

```
Example
```

`run_db_queries` will run multiple queries using a CSV as input. This is useful in cases where a user wants to query a lot of variable data, such as a list of barcodes, identifiers, etc. This function loops through the CSV file and calls a query function in `queries.py` which uses f-strings (new in Python 3.7) to insert variable data from a CSV into the query each time it is run.

```
def run_db_queries(dbconn, csvfile, query_func):
    return (dbconn.run_query_list(query_func(row)) for row in csvfile)
```

Example usage:

```
def main(result=None):
  try:
    home_dir = str(Path.home())
    config_file = u.get_config(cfg=home_dir + '/as_tools_config.yml')
    dirpath = u.setdirectory(config_file['backup_directory'])
    #what if just using the regular queries without f string functions?? Do like a csvfile=None variable?
    header_row, csvfile = u.opencsv(config_file['input_csv'])
    dbconn = dbssh.DBConn()
    result = aspace_tools.run_db_queries(dbconn, csvfile, getattr(queries, sys.argv[1]))
  finally:
     dbconn.close_conn()
     return result
```

The results of database queries can be written to an output file or stored in a Python list, generator, or DataFrame.

_NOTE_: Can also use the `db` file in `utilities` package to connect without SSH.

##### `crud.py`

This file holds all of the CRUD-related functions that are passed as the `crud` argument in the `aspace_run.call_api` function. These functions represent various types of create, read, update, and delete actions possible via the ArchivesSpace API. Some are generalized - the `update_data`, `create_data`, `get_data`, and `delete_data` functions can all be used to perform said actions on any record.

The `create_data`, `update_data`, and `get_data` functions call other functions which are stored in `json_data.py` to formulate the JSON which is required for API data transmission.

Other functions in this file are scoped to specific endpoints that are formatted somewhat differently or take
different parameters than the four generalized functions. These include functions which update the parent and position of an archival object and which update the position of an enumeration value, among others.

_NOTE_: currently working on a version of `crud.py` which implements the `ArchivesSnake` Python package.

##### `json_data.py`

This file holds all JSON data structures which are passed to the create, update, and delete functions in `crud.py`. The functions take a CSV row as input, and use the fields to populate a bit of JSON which is posted to ArchivesSpace via a `crud.py` function.

##### `queries.py`

This file holds all query strings and query functions used in the `run_db_query` and `run_db_queries` functions in `aspace_run.py`. Some functions are simply query strings which are passed to `run_db_query` and run once. Others take a CSV row as input and insert row data into a query using Python's f-string syntax.

##### `data_processing.py`

This file contains a compilation of post-processing functions that can be used on outputs from the ArchivesSpace API or database.

##### `templates.py`

This file compiles JSON and CSV templates using the ArchivesSpace schema. To compile the templates, do:

```
>>> from aspace_tools import templates
>>> t = templates.ASTemplates()
>>> as_templates = t.parse_schemas()
>>> print(as_templates['archival_object'])
>>> t.download_csv_templates(as_templates)
```

##### `aspace_tools_logging.py`

This file contains a custom logger which is initialized when the package is imported or run on the command line. All of the other files in this package import this file and initialize their own custom loggers.

##### `aspace_tools_tests.py`

Tests. Nothing here yet :(

##### `implementations`

Includes `.py` files that rely on the `aspace_tools` package.

##### `standalone_scripts`

Legacy `.py` and `.sql` files which do not rely on the `aspace_tools` package.

##### `templates`

Outputs from `templates.py` are stored in this folder.

##### `logs`

Logs are stored in this folder.

##### `fixtures`

These files are used by `aspace_tools_tests.py`.

## Package Structure

```
aspace-tools
│   README.md
│   LICENSE.txt
│   MANIFEST.in
│   setup.py    
│
└───aspace-tools
    │   __init__.py
    │   aspace_api.py
    │   aspace_db.py
    │   aspace_run.py
    │   crud.py
    │   json_data.py
    │   queries.py
    │   templates.py
    │   data_processing.py
    │   aspace_tools_logging.py
    │   aspace_tools_tests.py
    │   as_tools_config.yml
    │
    └───standalone_scripts
    │   └───python
    │   │     ..lots of .py files..
    │   │
    │   └───sql
    │         ..lots of .sql files..
    │
    └───implementations
    │      music_data.py
    │
    └───templates
    │
    └───logs
    │      logging_config.yml    
    │
    └───fixtures
           as_schema_data.py
           property_exclusions.csv (does the file path need to be changed in templates.py?)
           schema_exclusions.csv (same as above)
           schemas.json
```
