#/usr/bin/python3
#~/anaconda3/bin/python

import json, traceback, datetime, os
import requests
from utilities import utilities as u
from delete_records import delete_records

#add in the DB query here???

def get_child_count(api_url, headers, resource_uri):
	c = requests.get(api_url + resource_uri + '/tree/root', headers=headers).json()
	return c['child_count']

def create_og_accession_object(api_url, headers, csvfile):
	fileobject, csvoutfile = u.opencsvout(output_csv='/Users/amd243/Desktop/new_aos.csv')
	for i, row in enumerate(csvfile):
		resource_uri = row[0]
		print('Working on ' + str(resource_uri))
		before = get_child_count(api_url, headers, resource_uri)
		print('before: ' + str(before))
		new_ao = {'jsonmodel_type': 'archival_object', 'title': 'Original Accession', 
		'level': 'series', 'publish': True, 'position': 0, 
		'resource': {'ref': resource_uri}, 
		'repository': {'ref': '/repositories/12'}}
		new_ao_post = requests.post(api_url + '/repositories/12/archival_objects', headers=headers, json=new_ao).json()
		after = get_child_count(api_url, headers, resource_uri)
		print('after: ' + str(after))
		if 'status' in new_ao_post:
			row.append(new_ao_post['uri'])
		csvoutfile.writerow(row)

def set_new_parent(api_url, headers, csvfile):
	for i, row in enumerate(csvfile, 1):
		ao_uri = row[0]
		position = row[3]
		level = row[4]
		new_parent = row[5]
		if level == 'file':
			make_change = requests.post(api_url + ao_uri + '/parent?parent=' + new_parent + '&position=' + position, headers=headers).json()
			print(make_change)

#more logging?
def update_child_position(api_url, headers, csvfile):
	counter_range = list(range(0, 13000, 300))
	parent_uris = set()
	for i, row in enumerate(csvfile, 1):
		try:
			if i in counter_range:
				print(f"Working on row {i}")
			ao_uri = row[0]
			parent_uri = row[1]
			resource_uri = row[2]
			position = row[3]
			record_post = requests.post(api_url + resource_uri + '/accept_children?children[]=' 
										+ ao_uri + '&position=' + position, headers=headers).json()
			if 'error' in record_post:
				print(ao_uri)
				print(record_post.get('error'))
			parent_uris.add((parent_uri, resource_uri))
		except Exception as exc:
			print(ao_uri)
			print(traceback.format_exc())
			continue
	return parent_uris

def check_parent(api_url, headers, parent_uri_set):
	parents_to_delete = []
	for parent_uri, resource_uri in parent_uri_set:
		if parent_uri != '':
			node_data = requests.get(api_url + resource_uri + '/tree/node?node_uri=' + parent_uri, headers=headers).json()
			if node_data['child_count'] == 0:
				parents_to_delete.append([parent_uri])
			else:
				print(parent_uri, resource_uri)
				print(node_data['child_count'])
	return parents_to_delete

def get_filenames():
	full_dir_list = []
	dirpath = "/Users/amd243/Desktop/inventory_reports/resources_to_fix_w_ids/"
	dirlist = os.listdir(dirpath)
	for item in dirlist:
		if item != '.DS_Store':
			item = dirpath + item
			full_dir_list.append(item)
	return full_dir_list

def main():
	print(datetime.datetime.now())
	api_url, headers = u.login(url="https://archivesspace.library.yale.edu/api", username="amd243", password="FFmIjc5xLw")
	#header_row, csvfile = u.opencsv(input_csv='/Users/amd243/Desktop/inventory_uris_to_fix.csv')
	#create_og_accession_object(api_url, headers, csvfile)
	filename_list = get_filenames()
	for filename in filename_list:
		print('Starting: ' + str(filename))
		print(datetime.datetime.now())
		header_row, csvfile = u.opencsv(input_csv=filename)
		set_new_parent(api_url, headers, csvfile)
		#parent_uri_set = update_child_position(api_url, headers, csvfile)
		#print(datetime.datetime.now())
		#parent_uris_to_delete = check_parent(api_url, headers, parent_uri_set)
		#print(datetime.datetime.now())
		#delete_records(api_url, headers, parent_uris_to_delete)
		print(datetime.datetime.now())


if __name__ == "__main__":
	main()

'''
/Users/aliciadetelich/Desktop/inventory_reports/2944_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/2977_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/2949_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/2973_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/2979_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/2989_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3001_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3044_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3045_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3065_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3068_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3091_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3096_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3143_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3148_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3180_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3212_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3228_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3236_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3247_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3265_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3268_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3274_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3283_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3313_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3332_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3360_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3361_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3379_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3388_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3392_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3393_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3399_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3405_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3406_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3408_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3409_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3414_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3447_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3468_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3477_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3528_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3545_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3562_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3568_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3633_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3637_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3648_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3665_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3675_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3677_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3679_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3680_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3687_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3688_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3691_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3692_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3693_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3694_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3696_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3697_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3699_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3702_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3715_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3721_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3723_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3730_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3743_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3748_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3751_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3754_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3755_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3804_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3831_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3839_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3864_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3887_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3895_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3897_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3909_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3919_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3926_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3967_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3985_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/3992_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/4008_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/4009_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/4038_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/4081_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/4121_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/4133_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/4136_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/4196_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/4235_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/4249_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/4256_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/4265_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/4281_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/4285_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/4554_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/4562_results.csv
/Users/aliciadetelich/Desktop/inventory_reports/5584_results.csv
'''