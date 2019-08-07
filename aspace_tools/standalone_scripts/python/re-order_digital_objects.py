
'''Yale University Art Gallery and the Yale Center for British Art, recordings of lectures and presentations    [Preservica] ms_0001_s01_b005_f0058 /repositories/12/archival_objects/821671    2

Yale University Art Gallery and the Yale Center for British Art, recordings of lectures and presentations   [Preservica] ru_0359_1998-a-056_b0043   /repositories/12/archival_objects/821671    2
'''

from collections import Counter, defaultdict
from operator import itemgetter
import json
import pprint
import traceback

import requests

from utilities import utilities as u

'''1.) Report of all archival objects with digital object instances
2.) Only want to look at the ones with more than one instance
3.) Would also want to exclude anything that's already been re-ordered
        -NOT implemented - maybe take the time stamp from the previous report and use as input

'''
def process_data(do_dict_copy, dirpath):
    get_config_path = input("Please enter path to config file: ")
    config_file = u.get_config(cfg=get_config_path)
    api_url, headers = u.login(url=config_file['api_url'], username=config_file['api_username'], password=config_file['api_password'])
    for key, value in do_dict_copy.items():
        try:
            print('Working on: ' + str(key))
            record_json = requests.get(api_url + key, headers=headers).json()
            outfile = u.openoutfile(filepath=dirpath + '/' + key[1:].replace('/','_') + '.json')
            json.dump(record_json, outfile)
            newlist = zip_lists(record_json, value)
            record_json_new = update_json(record_json, newlist)
            record_post = requests.post(api_url + key, headers=headers, json=record_json_new).json()
            print(record_post)
        except Exception as exc:
            print(traceback.format_exc())
            continue

def zip_lists(json_rec, do_dict_value):
    '''Helper function for process_data: gets the URI and index position of a list of archival object instances and stores
    in a new list. This is ordered by the position of the instance. Compares length of new instance list to length of 
    digital object dictionary value (also a list). If a match there are the same number of instances, and then zips together
    the value list, which is also sorted by digital object name. This allows us to get the desired position and URI in the same
    list, so we know what instance we should be replacing.'''
    do_list = [[instance['digital_object']['ref'], i] for i, instance in enumerate(json_rec['instances']) 
                if instance['instance_type'] == 'digital_object']
    if len(do_list) == len(do_dict_value):
        #generator?
        return list(zip(do_list, do_dict_value))

def update_json(json_rec, newlist):
    '''Helper function for process_data: takes the zipped list and JSON record as input. Combines each nested instance list
    into a single list and assigns into variables. If the current URI does not match the desired URI, replace the current
    URI at the given position with the desired URI.'''
    for item in newlist:
        #generator?
        newitem = [i for items in item for i in items]
        instance_do = newitem[0]
        instance_position = newitem[1]
        new_instance_do = newitem[3]
        #this should work - I do wonder if it can't get fucked up somehow
        if instance_do != new_instance_do:
            json_rec['instances'][int(instance_position)]['digital_object']['ref'] = new_instance_do
    return json_rec

#### Prep the Data ####
def prep_data(csv_file):
#converts it to a list - need it more than once; could just open the file i guess
    csvlist = [row for row in csv_file]
    counted = create_counter(csvlist)
    #initialize a default dict to store uris as keys and csv data as values in a list
    do_dict = create_default_dict(csvlist, counted)
    do_dict_sorted = sort_dict(do_dict)
    return do_dict_sorted

def create_default_dict(csv_list, count_dict):
    do_dict = defaultdict(list)
    for row in csv_list:
        ao_uri = row[2]
        if ao_uri in count_dict:
            do_dict[ao_uri].append(row)
    return dict(do_dict)

def sort_dict(dig_obj_dict):
    for value in dig_obj_dict.values():
        value = sorted(value, key=itemgetter(0))
    return dig_obj_dict

def create_counter(csv_list):
    urilist = [row[2] for row in csv_list]
    counted = {k: v for k, v in Counter(urilist).items() if v > 1}
    return counted

def main():
    #instead of this, import query and save results in list; use timestamp from previous report to limit results
    header_row, csvfile = u.opencsv(input_csv=config_file['api_input_csv'])
    digital_object_dictionary = prep_data(csvfile)
    pprint.pprint(digital_object_dictionary)
    process_data(digital_object_dictionary, config_file['input_dir'])


if __name__ == "__main__":
    main()

