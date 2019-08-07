#/usr/bin/python3
#~/anaconda3/bin/python

import json
import traceback
import requests
from utilities import utilities as u


#h1, c1 = u.opencsv(input_csv="/Users/aliciadetelich/Desktop/hm_local_access_restrictions_to_delete.csv")
h1, c1 = u.opencsv(input_csv="/Users/amd243/Desktop/ms_rus_w_hm_films.csv")
api_url, headers = u.login(url="https://archivesspace.library.yale.edu/api", username="amd243", password="FFmIjc5xLw")


#do something about boilerplate code


dirpath = "/Users/amd243/Desktop/ms_ru_restriction_backups"

# for row in c1:
# 	try:
# 		uri = row[0]
# 		persistent_id = row[1]
# 		record_json = requests.get(api_url + uri, headers=headers).json()
# 		outfile = u.openoutfile(filepath=dirpath + '/' + uri[1:].replace('/','_') + '.json')
# 		json.dump(record_json, outfile)
# 		for note in record_json['notes']:
# 			if note['persistent_id'] == persistent_id:
# 				if 'rights_restriction' in note:
# 					del note['rights_restriction']
# 		record_post = requests.post(api_url + uri, headers=headers, json=record_json).json()
# 		print(record_post)
# 	except Exception as exc:
# 		print(uri)
# 		print(traceback.format_exc())

for row in c1:
	try:
		uri = row[0]
		persistent_id = row[1]
		new_text = row[2]
		record_json = requests.get(api_url + uri, headers=headers).json()
		outfile = u.openoutfile(filepath=dirpath + '/' + uri[1:].replace('/','_') + '.json')
		json.dump(record_json, outfile)
		for note in record_json['notes']:
			if note['persistent_id'] == persistent_id:
				note['rights_restriction'] = {'local_access_restriction_type': ['UseSurrogate']}
				note['subnotes'][0]['content'] = new_text
		record_post = requests.post(api_url + uri, headers=headers, json=record_json).json()
		print(record_post)
	except Exception as exc:
		print(uri)
		print(traceback.format_exc())