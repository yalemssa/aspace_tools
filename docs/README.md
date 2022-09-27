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

### What does this package do? Who is it for?

This package includes functions for creating, reading, updating, and deleting data from ArchivesSpace. It was created for archivists who use the ArchivesSpace API to programmatically modify archival metadata.

`aspace_tools` can be imported into a Python script or into an interactive Python session. Standalone scripts which can more easily be distributed to end users can be generated using the `generate_script.py` script. See the module overviews below for details on the functionality of the package.

### Configuration

An empty configuration file entitled `as_tools_config.yml` is included in the `/src` directory, so that users may store login credentials and file/directory paths. Entering data into the configuration file is not required. Any data that is missing will be requested by the application when the user attempts to call a function.

#### ArchivesSpace Credentials

Connecting to the ArchivesSpace API requires the ArchivesSpace API URL along with the user's username and password. 

#### Input/Output Files

Most commonly, the functions in this package will be run against a CSV file that is supplied by the user, which contains the data about each record that is to be modified. The configuration file should include the path to this CSV file, e.g. `/Users/username/path/to/file.csv` for Mac or `C:\Users\username\path\to\file.csv`. The required CSV fields for each function are listed in the API documentation for this package. A CSV template can be generated for a given function by running the `generate_script.py` script.

#### Backup Directories

When records are updated using functions in this package, JSON backups of the data prior to the updates are saved to a backup directory that is defined by the user.

#### Other Configuration Settings

There are other configuration settings that can be included in order to take advantage of less-developed parts of this package, including the `db_tools.py` module which facilitates querying the ArchivesSpace MySQL database. Additional documentation on these modules is forthcoming.

### Running `aspace_tools` within an interactive session

Most parts of the `aspace_tools` package (except for the `generate_script.py` module) can be imported into the user's preferred Python interpreter and run interactively. To import the module, either install it via pip as described above, or navigate to the `/src` directory, and enter the following:

```
$ python
Python 3.8.5 (default, Sep  4 2020, 02:22:02)
[Clang 10.0.0 ] :: Anaconda, Inc. on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> from aspace_tools import aspace_run, aspace_requests
>>>
```

#### Creating an ASpaceConnection object

Authentication is required before making any requests to the ArchivesSpace API. The `aspace_tools` package contains a class, `ASpaceConnection`, which handles authentication andthe user-defined configuration settings. 

To authenticate, enter the following into the interpreter:

```
>>> aspace_conn = aspace_run.ASpaceConnection()
Login Successful!: https://testarchivesspace.your.domain.edu/api
```

If credentials are present the in the `as_tools_config.yml` file, authentication will be attempted automatically. If not, the user will be prompted to enter credentials into the interpreter.

#### Making a Request

After the user is authenticated, it is possible to begin making requests. Requests are made by calling methods in the `aspace_requests.ASpaceRequests` class. To access these methods, first instantiate the class, and then call one of the available methods. For example:

```
>>> client = aspace_requests.ASpaceRequests(aspace_conn)
>>> client.update_date_begin()
```

If an input CSV path is present in the `as_tools_config.yml` file, the update will begin immediately. If not, the user will be prompted to enter the path (e.g. `/path/to/the/input/file.csv`) to the file into the interpreter.

#### What Happens After a Request is Made

After a request is made, a progress bar will appear, which will indicate how many records have been processed, the total number of records to be processed, and the overall progress percentage. 

If the request is a read, update, or delete request, a JSON backup file will be created for each URI on the input spreadsheet, using the backup directory supplied by the user in the `as_tools_config.yml` file or, if this value is not present in the configuration file, when prompted to enter the path into the interpreter.

Any errors which are encountered during the process will be printed to the interpreter, as well as to a log file in the `/logs` directory specified by the user (or, in the absence of this directory, to the user's home directory)

In addition to the error log, two output files will be written to the directory in which the input CSV file is stored.

#### Making multiple requests in an interactive session

To make another request within the same interactive session, using a different set of input data, you must change the input CSV path in your configuration file. There are two ways to do this:

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

```

__Posting a JSON record__

```
```

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

## Module Overview

This section describes the functionality of each `aspace_tools` module.

### `aspace_run.py`

This module contains two classes, `ASpaceConnection` and `ASpaceCrud`, which handle ArchivesSpace connections and HTTP requests (respectively).

### `aspace_requests.py`

This module contains a single class, ASpaceRequests. The class contains methods which take a CSV row and, in some cases, a record's ArchivesSpace JSON record, as input, and return a new or modified JSON structure. The JSON structures that are returned by these methods are then posted to ArchivesSpace via one of the `aspace_run.ASpaceCrud` functions.

### `generate_script.py`

The `generate_script.py` file enables the autogeneration of standalone Python scripts which can be run by end users without having to install the entire `aspace_tools` package. These scripts are run from the command line by entering, for example `python update_date_begin.py`.

To generate a new script, run the following command:

`python -m aspace_tools.generate_script`

Follow the on-screen prompts to select an output directory and an available JSON template.

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





