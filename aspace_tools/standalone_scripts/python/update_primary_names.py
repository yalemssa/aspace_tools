import utilities, requests, json, os, time, traceback, sys, logging, csv

api_url, headers = utilities.login()
h1, csvfile = utilities.opencsv()
dirpath = input('Please enter path to backup directory: ')
x = 0
for i, row in enumerate(csvfile, 1):
	print('working on row: ' + str(i))
	try:
		uri = row[0]
		sort_name = row[1]
		primary_name = row[2]
		rest_of_name = row[3]
		dates = row[4]
		prefix = row[5]
		suffix = row[6]
		title = row[7]
		qualifier = row[8]
		name_order = row[9]
		record_json = requests.get(api_url + uri, headers=headers).json()
		if 'error' in record_json:
			print('error: could not retrieve ' + str(uri))
			print(str(record_json.get('error')))
			continue
		outfile = utilities.openjson(dirpath, uri[1:].replace('/','_'))
		json.dump(record_json, outfile)
		for name in record_json['names']:
			if 'is_display_name' in name:
				if name['is_display_name'] == True:
					if name['sort_name'] == sort_name:
						name['primary_name'] = primary_name
						name['rest_of_name'] = rest_of_name
						name['dates'] = dates
						name['prefix'] = prefix
						name['suffix'] = suffix
						name['title'] = title
						name['qualifier'] = qualifier
						name['name_order'] = name_order
					else:
						print('error: sort name does not match column')
						print(uri)
						print(sort_name)
						print(name['sort_name'])
		record_update = requests.post(api_url + uri, headers=headers, json=record_json).json()
		if 'status' in record_update:
			x += 1
		if 'error' in record_update:
			print('error: could not update ' + str(uri) + '\n')
			print('log: ' + str(record_update.get('error')) + '\n')
	except Exception as exc:
		print(uri)
		print(traceback.format_exc())
print('All done!')
print('Successful updates: ' + str(x))
print('Update attempts: ' + str(i))