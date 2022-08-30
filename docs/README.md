# ArchivesSpace Tools

`aspace_tools` is a Python package for interacting with the ArchivesSpace API and MySQL database.

## Requirements

* Python 3.10+
* Read/write access to ArchivesSpace API and/or database

## Installation

```
$ cd /path/to/package
$ pip install .
```

## Quick Start

### What does this package do? Who is it for?

This package provides a variety of functions for creating, reading, updating, and deleting data from ArchivesSpace.

The package is organized into several modules. `aspace_tools` can be imported into other Python code or into an interactive Python session. Standalone scripts which can more easily be distributed to end users can be generated using the `generate_script.py` script. See the module overviews below for more details on the functionality of the package.

This package was written for archivists who use the ArchivesSpace API to perform create, read, update, and delete actions in bulk. 

### Configuration

To get started, configure your API and database login information, set a backup directory, and define your input/output CSV file paths by filling in the appropriate fields in the included `as_tools_config.yml` template file.

### Running `aspace_tools` within an interactive session

`aspace_tools` can be imported into a Python interpreter and run interactively.

```
$ python
Python 3.8.5 (default, Sep  4 2020, 02:22:02)
[Clang 10.0.0 ] :: Anaconda, Inc. on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> from aspace_tools import aspace_requests, aspace_run
>>> aspace_conn = aspace_run.ASpaceConnection()
>>> client = aspace_requests.ASpaceRequests(aspace_conn)
>>> client.update_date_begin()

```

#### Making multiple requests in an interactive session

To make another request within the same interactive session, you must change the input CSV path in your configuration file. There are two ways to do this:

__Method 1: Updating in the Python interpreter__

Within the Python interpreter, enter the following to manually update the input CSV file and backup directory:

```
>>> print(aspace_conn.csvfile)
/path/to/old/input/file.csv
>>> print(aspace_conn.row_count)
79
>>> print(aspace_conn.dirpath)
/path/to/old/backup/folder
>>> print(aspace_conn.sesh)
<requests.sessions.Session object at 0x7f9fa03e5450>
>>> new_file_path = '/path/to/new/input_file.csv'
>>> new_backup_directory = '/path/to/new/directory'
>>> aspace_conn.update_from_input(new_file_path, new_backup_directory)
>>> print(aspace_conn.csvfile)
/path/to/new/input_file.csv
>>> print(aspace_conn.row_count)
130
>>> print(aspace_conn.dirpath)
/path/to/new/directory
>>> print(aspace_conn.sesh)
<requests.sessions.Session object at 0x7f9fa03e5450>
>>> client.cfg = aspace_conn
```

__Method 2: Updating the configuration file__


Open the configuration file, usually `as_tools_config.yml`, and update the required values - often this means updating the input CSV file and the backup directory. Save the file. Then, in your Python interpreter, enter the following:

```
>>> aspace_conn.update_from_config()
>>> client.cfg = aspace_conn
```

In both methods, the input CSV file and/or backup directories will be changed, but the ArchivesSpace HTTP session will remain the same. To change the API instance you are working with, you must instantiate a new ASpaceConnection object.

<!-- #### Operating on individual records

This package is designed to take an input CSV file and perform actions on all rows in that CSV file. However, it is possible to run this code against a single record. To do this, do the following:

```
json_data = ASpaceRequests.search_all(csv_row, decorated=False)
``` -->

### Using `aspace_tools` in your own code

Another way to use this code is to include it within your own Python files. 

```
#!/usr/bin/python3

from aspace_tools import json_data as jd

def main():
	aspace_conn = ASpaceConnection.from_dict('as_tools_config.yml')
	client = ASpaceRequests(aspace_conn)
	client.update_date_begin()

if __name__ == "__main__":
	main()

```

<!-- ## Running `aspace_tools` from the command line

TBD - need to update the CLI scripts before this can be done. -->

## Tutorial

### `aspace_requests.py`

### `aspace_run.py`

### `generate_script.py`

The `generate_script.py` file enables the autogeneration of standalone Python scripts which can be run by end users without having to install the entire `aspace_tools` package. These scripts are run from the command line by entering, for example `python update_date_begin.py`.

To generate a new script, run the following command:

`python -m aspace_tools.generate_script`

Follow the on-screen prompts to select an output directory and an available JSON template.

### `aspace_utils.py`

### `data_processing.py`

### `ead_tools.py`





