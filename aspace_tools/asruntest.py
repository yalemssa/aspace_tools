import json
import traceback
from collections import defaultdict
import pprint
import aspace_run as ar
from utilities import utilities as u

as_run = ar.ASpaceRun()
#as_run.call_api_looper('update_data', 'update_indicator_2')

# h1, c1 = u.opencsv('/Users/aliciadetelich/Desktop/glad_ao_multiple_instance_counts.csv')
#
# csvlist = [row for row in c1]
# newlist = []
#
# for row in csvlist:
#     uri = row[0]
#     display_string = row[1]
#     try:
#         record_json = as_run.sesh.get(as_run.api_url + uri).json()
#         for position, instance in enumerate(record_json['instances']):
#             tc_uri = instance['sub_container']['top_container']['ref']
#             tc_json = as_run.sesh.get(as_run.api_url + tc_uri).json()
#             tc_indicator = tc_json['indicator']
#             newrow = [uri, display_string, tc_uri, tc_indicator, position]
#             print(newrow)
#             newlist.append(newrow)
#     except Exception:
#         print(traceback.format_exc())
#         print(uri)
#
# fileobject, csvoutfile = u.opencsvout('/Users/aliciadetelich/Desktop/glad_ao_multiple_instance_counts_out.csv')
# csvoutfile.writerow(h1)
# csvoutfile.writerows(newlist)
# fileobject.close()

# def reorder_instances(self, record_json, csv_row):
#     '''Reorders instance subrecords in a descriptive record
#
#        Parameters:
#         record_json: The JSON representation of the archival object.
#         csv_row['uri']: The URI of the archival object record.
#         csv_row['tc_uri']: The URI of the top container.
#         csv_row['old_position']: The current position of the instance
#         csv_row['new_position']: The desired position of the instance.
#
#        Returns:
#         dict: The JSON structure.
#     '''
#         new_instance_list = []
#         for position, instance in enumerate(record_json['instances']):
#             if instance['sub_container']['top_container']['ref'] == csv_row['tc_uri']:
#
#
#         record_json['instances'] = new_instance_list
#         return record_json

h1, c1 = u.opencsv('/Users/aliciadetelich/Desktop/glad_ao_multiple_instance_counts_out.csv')

csvlist = [row for row in c1]

case_dict = defaultdict(list)

for row in csvlist:
	uri = row[0]
	tc_uri = row[2]
	tc_indicator = row[3]
	current_position = row[4]
	case_dict[uri].append([tc_uri, tc_indicator, current_position])

for key, value in case_dict.items():
	for position, v in enumerate(value):
		value[position].append(position)

pprint.pprint(dict(case_dict))

#now we have the case dictionary with the correct positions....

for key, valuelist in case_dict.items():
    #the key is the uri
    record_json = as_run.sesh.get(as_run.api_url + key).json()
    #this will run through each value in order
    new_instance_list = []
    for value in valuelist:
        tc_uri = value[0]
        for instance in record_json['instances']:
            if instance['sub_container']['top_container']['ref'] == tc_uri:
                new_instance_list.append(instance)
    record_json['instances'] = new_instance_list
    posted = as_run.sesh.post(as_run.api_url + key, json=record_json).json()
    print(posted)
