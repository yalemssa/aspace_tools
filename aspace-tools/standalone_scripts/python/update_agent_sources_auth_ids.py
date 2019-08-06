import utilities, requests, json, os, time, traceback, sys, logging, csv

api1, headers1 = utilities.login()
dirpath = '/Users/amd243/Desktop/combined_agent_files/astf_final_final/backups_displaynames_no_uris_notlocal'
headers, csvfile = utilities.opencsv()
dirpath = utilities.setdirectory()
csvlist = [row for row in csvfile]
x = 0
for row in csvlist:
	try:
		uri = row[0]
		record_json = requests.get(api1 + uri, headers=headers1).json()
		if 'error' in record_json:
			print('error: could not retrieve ' + str(record_uri))
			print(str(record_json.get('error')))
		outfile = utilities.openjson(dirpath, uri[1:].replace('/','_'))
		json.dump(record_json, outfile)
		if 'display_name' in record_json:
			if 'authority_id' not in record_json['display_name']:
				if record_json['display_name']['source'] != 'local':
					for name in record_json['names']:
						if name['sort_name'] == record_json['display_name']['sort_name']:
							if 'authority_id' not in name:
								name['source'] = 'local'
			if 'authority_id' in record_json['display_name']:
				if 'http' not in record_json['display_name']['authority_id']:
					if 'dts' in record_json['display_name']['authority_id']:
						for name in record_json['names']:
							if name['sort_name'] == record_json['display_name']['sort_name']:
								if name['authority_id'] == record_json['display_name']['authority_id']:
									del name['authority_id']
							if name['source'] != 'local':
								name['source'] = 'local'
					else:
						print(record_uri)
		record_data = json.dumps(record_json)
		record_update = requests.post(api1+ uri, headers=headers1, data=record_data).json()
		print(record_update)
		if 'status' in record_update:
			x += 1
		if 'error' in record_update:
			print('error: could not update ' + str(uri) + '\n')
			print('log: ' + str(record_update.get('error')) + '\n')
	except Exception as exc:
		print(uri)
		print(traceback.format_exc())