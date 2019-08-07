#/usr/bin/python3
#~/anaconda3/bin/python

import utilities, requests, json, logging, time, traceback

def add_tc_data():
	starttime = time.time()
	api_url, headers = utilities.login()
	header_row, csvfile = utilities.opencsv()
	dirpath = utilities.setdirectory()
	x = 0
	for i, row in enumerate(csvfile, 1):
		try:
			tc_uri = row[0]
			barcode = row[1]
			logging.debug('Working on row ' + str(i) + ': ' + tc_uri)
			record_json = requests.get(api_url + tc_uri, headers=headers).json()
			if 'error' in record_json:
				logging.debug('error: could not retrieve ' + str(tc_uri))
				logging.debug(str(record_json.get('error')))
			outfile = utilities.openjson(dirpath, tc_uri[1:].replace('/','_'))
			json.dump(record_json, outfile)
			record_json['barcode'] = barcode
			record_json['type'] = 'Box'
			new_location = {'jsonmodel_type': 'container_location', 'ref': '/locations/9', 'status': 'current', 'start_date': '2017-03-01'}
			record_json['container_locations'].append(new_location)
			record_data = json.dumps(record_json)
			record_post = requests.post(api_url + tc_uri, headers=headers, data=record_data).json()
			print('Row ' + str(i) + ': ' + str(record_post))
			if 'status' in record_post:
				x += 1
			if 'error' in record_post:
				logging.debug('uri: ' + str(tc_uri))
				logging.debug('log: ' + str(record_post.get('error')))
		except Exception as exc:
			print(tc_uri)
			print(traceback.format_exc())
			logging.debug(tc_uri)
			logging.exception('Error: ')
			continue
	logging.debug('Total update attempts: ' + str(i))
	logging.debug('Records updated successfully: ' + str(x))
	utilities.keeptime(starttime)
	print('All Done!')

if __name__ == "__main__":
    log_input = input('Please enter path to log file: ')
    utilities.error_log(filepath=log_input)
    add_tc_data()