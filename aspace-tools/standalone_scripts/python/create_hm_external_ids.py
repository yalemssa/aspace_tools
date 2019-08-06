import requests, json, traceback
from utilities import utilities as u
import new_use_surrogate_notes


def create_hm_external_id(record_json, row):
    uri = row[0]
    hm_number = row[1]
    new_external_id = {'jsonmodel_type': 'external_id',
                        'external_id': hm_number,
                        'source': 'local_surrogate_call_number'}
    if 'external_ids' in record_json:
        if len(record_json['external_ids']) > 0:
            ex_ids = [e['external_id'] for e in record_json['external_ids']]
            if hm_number in ex_ids:
                print('Record already has HM external ID')
            else:
                record_json['external_ids'].append(new_external_id)
        else:
            record_json['external_ids'].append(new_external_id)
    else:
        record_json['external_ids'] = [new_external_id]
    #record_json = add_access_notes(record_json, row)
    return record_json

#maybe have row be optional
def add_access_notes(record_json, row):
    exists = 0
    if len(record_json['notes']) > 0:
        for note in record_json['notes']:
            if note['type'] == 'accessrestrict':
                if 'This material has been microfilmed' in note['subnotes'][0]['content']:
                    print('Note exists!')
                    exists = 1
    if exists == 0:
        record_json = new_use_surrogate_notes.create_access_note(record_json, row)
    return record_json

def main():
    h1, c1 = u.opencsv("/Users/amd243/Dropbox/2019_may_desktop/hm_reports/hm_aos_need_updates/wholes_need_ex_ids.csv")
    api_url, headers = u.login(url="https://archivesspace.library.yale.edu/api", username="amd243", password="FFmIjc5xLw")
    new_use_surrogate_notes.process_data(api_url, headers, c1, create_hm_external_id)


if __name__ == "__main__":
    main()
