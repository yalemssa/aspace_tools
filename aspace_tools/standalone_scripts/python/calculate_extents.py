#/usr/bin/python3
#~/anaconda3/bin/python

import utilities, traceback, csv, json, requests


def calculate_extents():
	api_url, headers = utilities.login()
	header_row, csvfile = utilities.opencsv()
	fileobject, csvoutfile = utilities.opencsvout()
	header_row = header_row + ['total_extent', 'units']
	csvoutfile.writerow(header_row)
	for row in csvfile:
		try:
			uri = row[0]
			extent_calc = requests.get(api_url + '/extent_calculator?record_uri=' + uri, headers=headers).json()
			row.append(str(extent_calc['total_extent']))
			row.append(extent_calc['units'])
			csvoutfile.writerow(row)
		except Exception as exc:
			print(uri)
			print(traceback.format_exc())
			csvoutfile.writerow([uri])
	fileobject.close()
	print('All Done!')

if __name__ == '__main__':
	calculate_extents()