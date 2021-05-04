#!/usr/bin/python3
#~/anaconda3/bin/python

'''
This file sets up logging for the aspace-tools package. All of the other files import this file and then call the getLogger method to get their own custom loggers.
'''

import logging
import logging.config
import yaml
import os
import functools
import time
from decorator import decorator

def setup_logging(default_path='logs/logging_config.yml', default_level=logging.DEBUG):
    '''Sets up logging configuration'''
    print(f'Setting up logging in {__name__}')
    fp = default_path
    if os.path.exists(fp):
        with open(fp, 'r') as file_path:
            config = yaml.safe_load(file_path.read())
            logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)

def as_tools_logger(logger_object):
    '''This is a decorator function which takes a logger object as an argument
    and logs the start and end/runtime of each function called during program
    execution. This decorator is applied to almost every function in the
    aspace-tools package. Could potentially remove the decorator from all of the
    json_data.py functions (already not in the queries.py functions), since all
    they do is take strings and put them into dictionaries, which takes no time at all
    Would be nice to know when the function runs, though, so maybe have a second
    decorator for the queries.py and json_data functions??'''
    #def decorator_as_tools_logger(func):
    @decorator
    def wrapper_as_tools_logger(func, *args, **kwargs):
        logger_object.debug(f'Starting {func.__name__!r}')
        start_time = time.perf_counter()
        try:
            #logging.debug(f'args: {args}')
            #logging.debug(f'kwargs: {kwargs}')
            value = func(*args, **kwargs)
            end_time = time.perf_counter()
            run_time = end_time - start_time
            logger_object.debug(f'{func.__name__!r} run time: {run_time:.4f} secs')
            return value
        except Exception:
            logger_object.exception('Error: ')
    return wrapper_as_tools_logger
    #return decorator_as_tools_logger

setup_logging()
