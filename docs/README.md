# ArchivesSpace Tools

`aspace_tools` is a Python package for interacting with the ArchivesSpace API and MySQL database.

## Requirements

* Python 3.10+
* Read/write access to ArchivesSpace API and/or database

## Installation

```
$ cd /path/to/aspace_tools/src
$ pip install .
```

## Tutorial

This package includes functions for creating, reading, updating, and deleting data from ArchivesSpace. It was created for archivists who use the ArchivesSpace API to programmatically modify archival metadata.

`aspace_tools` can be imported into a Python script or into an interactive Python session. Standalone scripts which can more easily be distributed to end users can be generated using the `generate_script.py` script. See the module overviews below for details on the functionality of the package.

### Getting started: configuration

An empty configuration file entitled `as_tools_config.yml` is included in the `/src` directory, so that users may store login credentials and file/directory paths. Entering data into the configuration file is not required. Any data that is missing will be requested by the application when the user attempts to call a function.

#### ArchivesSpace credentials

Connecting to the ArchivesSpace API requires the ArchivesSpace API URL along with the user's username and password. 

#### Input/output files

Most commonly, the functions in this package will be run against a CSV file that is supplied by the user, which contains the data about each record that is to be modified. The configuration file should include the path to this CSV file, e.g. `/Users/username/path/to/file.csv` for Mac or `C:\Users\username\path\to\file.csv`. The required CSV fields for each function are listed in the API documentation for this package. A CSV template can be generated for a given function by running the `generate_script.py` script.

#### Backup directories

When records are updated using functions in this package, JSON backups of the data prior to the updates are saved to a backup directory that is defined by the user.

#### Other configuration settings

There are other configuration settings that can be included in order to take advantage of less-developed parts of this package, including the `db_tools.py` module which facilitates querying the ArchivesSpace MySQL database. Additional documentation on these modules is forthcoming.

### Running `aspace_tools` within an interactive session

The `aspace_tools` package can be imported into the user's preferred Python interpreter and run interactively. To import the module, either install it via pip as described above, or navigate to the `/src` directory, and enter the following:

```
$ python
Python 3.8.5 (default, Sep  4 2020, 02:22:02)
[Clang 10.0.0 ] :: Anaconda, Inc. on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> from aspace_tools import aspace_run, aspace_requests
>>> 
```

#### Creating an ASpaceConnection object

Authentication is required before sending HTTP requests to the ArchivesSpace API. The `aspace_tools` package contains a class, `ASpaceConnection`, which handles authentication and user-defined configuration settings. 

To authenticate, enter the following into the interpreter:

```
>>> aspace_conn = aspace_run.ASpaceConnection()
Login Successful!: https://testarchivesspace.your.domain.edu/api
```

If credentials are present the in the `as_tools_config.yml` file, authentication will be attempted automatically. If not, the user will be prompted to enter credentials into the interpreter.

#### Sending requests

After the user is authenticated, it is possible to begin sending requests. Requests are sent by calling methods in the `aspace_requests.ASpaceRequests` class. To access these methods, first instantiate the class with the ArchivesSpace connection object as an argument, and then call one of the available methods to send the request. For example:

```
>>> client = aspace_requests.ASpaceRequests(aspace_conn)
>>> client.update_date_begin()
```

If an input CSV path is present in the `as_tools_config.yml` file, the update will begin immediately. If not, the user will be prompted to enter the path (e.g. `/path/to/the/input/file.csv`) to the file into the interpreter.

Note that if a CSV input path is present in the configuration file and one of these methods is calld, the update that is defined in the method will be applied to all of the records in the input spreadsheet. 

Consult the API documentation for more information on available methods and their required CSV fields.

#### After a request is made

After a request is made, a progress bar will appear in the terminal, which will indicate how many records have been processed, the total number of records to be processed, and the overall progress percentage. 

If the request is a read, update, or delete request, a JSON backup file will be created for each URI on the input spreadsheet, using the backup directory supplied by the user in the `as_tools_config.yml` file or, if this value is not present in the configuration file, when prompted to enter the path into the interpreter.

Any errors which are encountered during the process will be printed to the interpreter, as well as to a log file in the `/logs` directory specified by the user (or, in the absence of this directory, to the user's home directory). After each error, the user will be prompted to retry the update, skip the record, or stop the entire process.

In addition to the error log, two output files will be written to the directory in which the input CSV file is stored. These files will be named `[original_filename]_success.csv` and `[original_filename]_errors.csv`. Each row from the original spreadsheet, plus the URI of the created or updated record, will be written to one of these spreadsheets depending on the outcome of the update.

#### Making multiple requests in an interactive session

To make another request within the same interactive session, using a different set of input data, the user must change the input CSV path in your configuration file. There are two ways to do this:

__Method 1: Updating in the Python interpreter__

Within the Python interpreter, enter the following to manually update the input CSV file and backup directory:

```
>>> print(aspace_conn.csvfile, aspace_conn.row_count, aspace_conn.dirpath, aspace_conn.sesh, sep='\n')
/path/to/old/input/file.csv
79
/path/to/old/backup/folder
<requests.sessions.Session object at 0x7f9fa03e5450>
>>> new_file_path = '/path/to/new/input_file.csv'
>>> new_backup_directory = '/path/to/new/directory'
>>> aspace_conn.update_from_input(new_file_path, new_backup_directory)
>>> print(aspace_conn.csvfile, aspace_conn.row_count, aspace_conn.dirpath, aspace_conn.sesh, sep='\n')
/path/to/new/input_file.csv
130
/path/to/new/directory
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

#### Operating on individual records

This package is designed to take an input CSV file and perform actions on all rows in that CSV file. However, it is possible to run pieces of the code on individual records if desired.

__Forming a JSON template__

```
>>> csv_row = {'search_string': 'A string to search'}
>>> endpoint = ASpaceRequests.search_all(csv_row)
>>> print(endpoint)
>>> /search?q=A string to search
```

__Getting a JSON record__

```
>>> csv_row = {'uri': '/repositories/2/archival_objects/294923'}
>>> 
```

__Posting a JSON record__

```
>>> csv_row = {'uri': '/repositories'}
>
```

### Using `aspace_tools` in your own code

Another way to use this code is to include it within your own Python files. For example, if the `aspace_tools` package is installed on the end-user's computer, this code could be stored in a `.py` file which is run from the Terminal or command prompt.


```
#!/usr/bin/python3

import csv
from aspace_tools import aspace_requests, aspace_run


def prep_data(fp):
	'''Takes some input data and modified it'''
	with open(fp, encoding='utf8') as infile:
		reader = csv.reader(infile)

def write_data(data):
	aspace_conn.update_from_input(new_file_path, new_backup_directory)
	pass

def update_data():
	aspace_conn = ASpaceConnection.from_dict(config_file='/path/to/your/as_tools_config.yml')
	client = ASpaceRequests(aspace_conn)
	client.update_date_begin()


def main():
	fp = "..."
	prep_data(fp)


if __name__ == "__main__":
	main()

```

### Generating scripts via `generate_script.py`

Not all users will need to install the entire `aspace_tools` package on their local machines. Sometimes users will want a standalone script for just their particular use case. The `generate_script.py` module generates these scripts from the `aspace_tools` package, along with a blank configuration file and a CSV template that can be provided to the end user.

To generate a new script, run the following command:

`python -m aspace_tools.generate_script`

Follow the on-screen prompts to select an available JSON template, and an output directory for the generated files.

<!-- ## Running `aspace_tools` from the command line

TBD - need to update the CLI scripts before this can be done. -->

## Module Overview

This section describes the functionality of each `aspace_tools` module.

### `aspace_run.py`

This module contains two classes, `ASpaceConnection` and `ASpaceCrud`, which handle ArchivesSpace connections and HTTP requests (respectively).

### `aspace_requests.py`

This module contains a single class, ASpaceRequests. The class contains methods which take a CSV row and, in some cases, a record's ArchivesSpace JSON record, as input, and return a new or modified JSON structure. The JSON structures that are returned by these methods are then posted to ArchivesSpace via one of the `aspace_run.ASpaceCrud` functions.

### `generate_script.py`

The `generate_script.py` file enables the autogeneration of standalone Python scripts which can be run by end users without having to install the entire `aspace_tools` package. These scripts are run from the command line by entering, for example `python update_date_begin.py`.

### `aspace_utils.py`

Utility functions which aid in file handling, error handling, progress tracking, logging, etc.

### `post_processing.py`

Miscellaneous functions which can be used to process data that is retrieved from the ArchivesSpace API

### `ead_tools.py`

Functions for exporting, transforming, and validating EAD files from ArchivesSpace.

### `db_tools.py`

Contains a class, `ASpaceDB` for connecting to and running SQL queries against the ArchivesSpace database

### `templates.py`

An experimental script for generating JSON templates from the ArchivesSpace schema.





