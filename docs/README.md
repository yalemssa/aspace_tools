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

## What does this package do? Who is it for?

The `aspace_tools` package is organized into several modules. `aspace_tools` can be imported into a Python file or used in an interactive interpreter session. Standalone scripts which can more easily be distributed to end users can be generated using the `generate_script.py` script.

## Configuration

To get started, configure your API and database login information, set a backup directory, and define your input/output CSV file paths by filling in the appropriate fields in the included `as_tools_config.yml` template file.

## Running `aspace_tools` within an interactive session

`aspace_tools` can be imported into a Python interpreter and run interactively.

```
$ python
Python 3.8.5 (default, Sep  4 2020, 02:22:02)
[Clang 10.0.0 ] :: Anaconda, Inc. on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> from aspace_tools import aspace_requests, aspace_run
>>> aspace_conn = aspace_run.ASpaceConnection.from_dict()
>>> client = aspace_requests.ASpaceRequests(aspace_conn)
>>> client.update_date_begin()

```

### Making multiple requests in an interactive session

To make another request within the same interactive session, you must change the input CSV path in your configuration file. There are two ways to do this:

__Method 1: Updating the config file and starting a new ASpaceConnection__

Open the configuration file, usually `as_tools_config.yml`, and update the required values - often this means updating the input CSV file and the backup directory. Save the file. Then, in your Python interpreter, enter the following:

```
>>> print(client.cfg.input_csv, client.cfg.row_count)
'/path/to/old/file.csv' 150
>>> aspace_conn = ASpaceConnection.from_dict()
>>> client.cfg = aspace_conn
>>> print(client.cfg.input_csv, client.cfg.row_count)
>>>'/path/to/new/file.csv' 129
```

The advantage of this method is that the user only needs to update the configuration file and restart the session, and does not need to manually re-set any variables or call any utility functions. The disadvantage is that a new ArchivesSpace HTTP session will be started, rather than using the same session as the previous set of requests. 

__Method 2: Updating the client.cfg variables__

Within the Python interpreter, enter the following to manually update the input CSV file and backup directory

```
>>> from aspace_tools import script_tools as st
>>> new_csv = '/path/to/new/file.csv'
>>> new_backup_dir = '/path/to/new/backup/folder'
>>> client.cfg.input_csv = new_csv
>>> client.cfg.row_count = st.get_rowcount(new_csv)
>>> client.cfg.backup_directory = new_backup_dir
```

The advantage of this method is that the same ArchivesSpace HTTP session is used, as the ASpaceConnection class is not re-instantiated. The disadvantage is that the CSV row count that is used for the progress bar is not automatically updated when the input CSV is changed, and so this needs to be reset as well. To do this, the user needs to import the script_tools module, which contains a variety of utility functions that are used throughout the package.

### Operating on individual records

This package is designed to take an input CSV file and perform actions on all rows in that CSV file. However, it is possible to run this code against a single record. To do this, do the following:

```



```

## Using `aspace_tools` in your own code

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

## Using `generate_script.py`

The `generate_script.py` file enables the autogeneration of standalone Python scripts which can be run by end users without having to install the entire `aspace_tools` package. These scripts are run from the command line by entering, for example `python update_date_begin.py`.

To generate a new script, run the following command:

`python -m aspace_tools.generate_script`

Follow the on-screen prompts to select an output directory and an available JSON template.





