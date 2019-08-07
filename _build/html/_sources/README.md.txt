This is the main documentation page for the `aspace_tools` Python package.

`aspace_tools` is a command-line interface for interacting with the ArchivesSpace API and MySQL database, usually using CSV files as input and output.

## Requirements

* Python 3.7+
* `utilities` package (will also install a few other dependencies)

## Installation

```
$ cd /path/to/package
$ pip install .

```

## Project Structure/Philosophy

This package is structured in a modular fashion which makes it highly extensible and which limits the repetition of boilerplate code.

While all functions can be run independently, the primary way that end users will interact with the package is through the `aspace_api.py` and `aspace_db.py` command-line interfaces.

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
    │   as_tools_config.yml (this is a blank template; once filled out should be moved to home directory)
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

### `aspace_run.py`

 The main scaffolding for all the other functions are stored in `aspace_run.py`.

### `crud.py`

This file holds all of the CRUD-related functions that are used in the `aspace_run.call_api` function.

### `json_data.py`

This file holds all JSON data structures which are used in create, update, and delete functions in `crud.py`

### `queries.py`

This file holds all query strings and query functions used in the `run_db_query` and `run_db_queries` functions in `aspace_run.py`

### `templates.py`

This file compiles JSON and CSV templates using the ArchivesSpace schema,

## Tutorial

End-user interaction with this package takes place on the command line.

To run a basic API update using `aspace_api.py`, do the following:

```
$ ./aspace_api update_data update_primary_names
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
