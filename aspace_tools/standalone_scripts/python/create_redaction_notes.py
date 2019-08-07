#/usr/bin/python3
#~/anaconda3/bin/python

import json, traceback
import requests
from utilities import utilities as u

def create_access_note(api_url, headers, csvfile, note_text):
    for row in csvfile:
        try:
            uri = row[0]
            record_json = requests.get(api_url + uri, headers=headers).json()
            new_note = {'jsonmodel_type': 'note_multipart',
                        'publish': True,
                        'subnotes': [{'content': note_text,
                                  'jsonmodel_type': 'note_text',
                                  'publish': True}],
                        'type': 'accessrestrict'}
            record_json['notes'].append(new_note)
            record_post = requests.post(api_url + uri, headers=headers, json=record_json).json()
            print(record_post)
        except Exception as exc:
            print(uri)
            print(traceback.format_exc())

def main():
    note_text = "Some records in this finding aid have been redacted, as they include student names, donor names, and other restricted data. These records will not appear in the published finding aid."
    header_row, csvfile = u.opencsv()
    api_url, headers = u.login()
    create_access_note(api_url, headers, csvfile, note_text)
    print('All Done!')

if __name__ == "__main__":
    main()