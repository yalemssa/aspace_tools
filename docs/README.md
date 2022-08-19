# ArchivesSpace Tools

`aspace_tools` is a Python package for interacting with the ArchivesSpace API and MySQL database.

## Requirements

* Python 3.8+
* Read/write access to ArchivesSpace API and/or database

## Installation

```
$ cd /path/to/package
$ pip install .
```

## What Does This Code Do?

The `aspace_tools` package is organized into several modules. `aspace_tools` can be imported into a Python file or used in an interactive interpreter session. Standalone scripts which can more easily be distributed to end users can be generated using the `generate_script.py` script.

To get started, configure your API and database login information, set a backup directory, and define your input/output CSV file paths by filling in the appropriate fields in the included `as_tools_config.yml` template file.

## Running `aspace_tools` within an interactive session

`aspace_tools` can be imported into a Python interpreter and run interactively.

```
$ python
Python 3.8.5 (default, Sep  4 2020, 02:22:02)
[Clang 10.0.0 ] :: Anaconda, Inc. on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> from aspace_tools import aspace_run
>>> as_run = aspace_run.ASpaceRun()
>>> as_run.call_api(update_data, "update_date_begin")

```

## Using `aspace_tools` in your own code

Another way to use this code is to include it within your own Python files. 

```
#!/usr/bin/python3

from aspace_tools import aspace_run

def main():
	as_run = aspace_run.ASpaceRun()
	as_run.call_api(update_data, "update_date_begin")

if __name__ == "__main__":
	main()

```

<!-- ## Running `aspace_tools` from the command line

TBD - need to update the CLI scripts before this can be done. -->

## Using `generate_script.py`

The `generate_script.py` file enables the autogeneration of Python scripts which can be run by end users without having to install the entire package.

To generate a new script, run the following command:

`python -m aspace_tools.generate_script`

Follow the on-screen prompts to select an output directory and an available JSON template.