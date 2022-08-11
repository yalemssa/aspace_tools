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

## Package Overview/Tutorial

This package is organized into several modules. `aspace_tools` can either be imported into a Python file or interactive interpreter, or standalone scripts can be generated using the `generate_script.py` module.s

To get started, configure your API and database login information, set a backup directory, and define your input/output CSV file paths by filling in the appropriate fields in the included `as_tools_config.yml` template file.