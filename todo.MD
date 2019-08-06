# aspace-tools

## Basic Structure:
* Central file which contains the looping and requesting functions, db query functions
* Decorator file which contains error logging, timing, and counter functions - or just use utilities
* Data structure file which contains various JSON templates
* Queries file which contains various queries - want this in a .py file to take
advantage of f strings
* ArchivesSpace templates stuf

## To-Do:
* Create CSV templates for all json_data functions
* Want to be able to have options for certain fields - like not all aos need a date or extent

##Dependencies:
* utilities module for file handling (need to add tests to utilities still)
* requests (OR ASNAKE) module - preferably ASNAKE
