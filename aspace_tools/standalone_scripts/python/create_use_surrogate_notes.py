#/usr/bin/python3
#~/anaconda3/bin/python

import json, traceback
import requests
from utilities import utilities as u

def create_access_note(record_json, row):
    uri = row[0]
    external_id = row[1]
    note_text = f"This material has been microfilmed. Patrons must use {external_id} instead of the originals."
    new_note = {'jsonmodel_type': 'note_multipart',
                'publish': True,
                'subnotes': [{'content': note_text,
                          'jsonmodel_type': 'note_text',
                          'publish': True}],
                'type': 'accessrestrict',
                'rights_restriction': {'local_access_restriction_type': ['UseSurrogate']}}
    record_json['notes'].append(new_note)
    return record_json

def update_access_note(record_json, row):
    uri = row[0]
    persistent_id = row[1]
    external_id = row[2]
    note_text = f"This material has been microfilmed. Patrons must use {external_id} instead of the originals"
    for note in record_json['notes']:
        if note['persistent_id'] == persistent_id:
            note['subnotes'][0]['content'] = note_text
            note['rights_restriction'] = {'local_access_restriction_type': ['UseSurrogate']}
    return record_json

def process_data(api_url, headers, csvfile, func):
    for row in csvfile:
        uri = row[0]
        try:
            record_json = requests.get(api_url + uri, headers=headers).json()
            record_json = func(record_json, row)
            record_post = requests.post(api_url + uri, headers=headers, json=record_json).json()
            print(record_post)
        except Exception as exc:
            print(uri)
            print(traceback.format_exc())


def main():
    #note_text = "Some records in this finding aid have been redacted, as they include student names, donor names, and other restricted data. These records will not appear in the published finding aid."
    header_row, csvfile = u.opencsv("/Users/amd243/Dropbox/2019_may_desktop/hm_reports/hm_aos_need_updates/parts_need_notes.csv")
    api_url, headers = u.login(url="https://archivesspace.library.yale.edu/api", username="amd243", password="FFmIjc5xLw")
    process_data(api_url, headers, csvfile, create_access_note)
    print('All Done!')

if __name__ == "__main__":
    main()