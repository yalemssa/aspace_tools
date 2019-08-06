
import requests, json, traceback, time
from utilities import utilities as u
from utilities import dbssh

'''ALSO NEED TO ADD EXTERNAL IDS TO ARCHIVAL OBJECTS!!!! Must re-do this for Collier and the
system indicator one... this means that I need the HM number on my input spreadsheets'''

hm_ind_query = """
SELECT CONCAT('/repositories/', tc.repo_id, '/top_containers/', tc.id) as tc_uri
    , tc.indicator AS container_num
from sub_container sc
LEFT JOIN enumeration_value ev on ev.id = sc.type_2_id
LEFT JOIN top_container_link_rlshp tclr on tclr.sub_container_id = sc.id
LEFT JOIN top_container tc on tclr.top_container_id = tc.id
LEFT JOIN top_container_profile_rlshp tcpr on tcpr.top_container_id = tc.id
LEFT JOIN container_profile cp on cp.id = tcpr.container_profile_id
LEFT JOIN top_container_housed_at_rlshp tchar on tchar.top_container_id = tc.id
LEFT JOIN location on location.id = tchar.location_id
LEFT JOIN instance on sc.instance_id = instance.id
LEFT JOIN archival_object ao on instance.archival_object_id = ao.id
LEFT JOIN resource on ao.root_record_id = resource.id
LEFT JOIN enumeration_value ev2 on ev2.id = ao.level_id
WHERE resource.id = 5024
AND tc.indicator like '%U%
"""

ms_ru_instance_query = """
SELECT DISTINCT CONCAT('/repositories/', ao.repo_id, '/archival_objects/', ao.id) as ao_uri
    , CONCAT(sc.indicator_3, 'U') AS gc_num
from sub_container sc
LEFT JOIN enumeration_value ev on ev.id = sc.type_2_id
LEFT JOIN top_container_link_rlshp tclr on tclr.sub_container_id = sc.id
LEFT JOIN top_container tc on tclr.top_container_id = tc.id
LEFT JOIN top_container_profile_rlshp tcpr on tcpr.top_container_id = tc.id
LEFT JOIN container_profile cp on cp.id = tcpr.container_profile_id
LEFT JOIN top_container_housed_at_rlshp tchar on tchar.top_container_id = tc.id
LEFT JOIN instance on sc.instance_id = instance.id
LEFT JOIN archival_object ao on instance.archival_object_id = ao.id
LEFT JOIN resource on ao.root_record_id = resource.id
LEFT JOIN enumeration_value ev2 on ev2.id = ao.level_id
WHERE resource.id = 4499
"""

#add this to utilities - adapted from practical decorators lecture
def logtime(func):

    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsedtime = time.time() - start_time
        m, s = divmod(elapsedtime, 60)
        h, m = divmod(m, 60)
        print(f'Total time: {h}:{m}:{s}')
        return result

    return wrapper

def run_indicator_queries():
    pass

#needs to be lists; this just prepares data for update. Don't need it for everything
def process_data(csv1, csv2, outfilename):
    fileobject, csvoutfile = u.opencsvout(output_csv=outfilename)
    header_row = ['tc_uri', 'ao_uri', 'hm_number', 'indicator']
    csvoutfile.writerow(header_row)
    for row in csv1:
        ao_uri = row[0]
        indicator = row[1]
        for r in csv2:
            tc_uri = r[0]
            ind = r[1]
            call_number = r[2]
            if indicator == ind:
                row.insert(0, tc_uri)
                row.insert(2, call_number)
        csvoutfile.writerow(row)
    fileobject.close()

#need to make sure there isn't already one of these - need to delete one from prod
def create_external_id(record_json, hm_call_number):
    new_external_id = {'jsonmodel_type': 'external_id',
                        'external_id': hm_call_number,
                        'source': 'local_surrogate_call_number'}
    #isn't it always?
    if 'external_ids' in record_json:
        if len(record_json['external_ids']) > 0:
            ex_ids = [e['external_id'] for e in record_json['external_ids']]
            if hm_call_number in ex_ids:
                print('Record already has HM external ID')
            else:
                record_json['external_ids'].append(new_external_id)
        else:
            record_json['external_ids'].append(new_external_id)
    else:
        record_json['external_ids'] = [new_external_id]
    return record_json

def create_instance(record_json, tc_uri):
    new_instance = {'jsonmodel_type': 'instance', 'instance_type': 'mixed_materials',
                    'sub_container': {'jsonmodel_type': 'sub_container',
                                        'top_container': {'ref': tc_uri}}
                    }
    record_json['instances'].append(new_instance)
    return record_json

def delete_subcontainers(record_json):
    for instance in record_json['instances']:
        if 'sub_container' in instance:
            if 'type_2' in instance['sub_container']:
                if instance['sub_container']['type_2'] == 'reel':
                    del instance['sub_container']['type_2']
                    del instance['sub_container']['indicator_2']
            if 'type_3' in instance['sub_container']:
                if instance['sub_container']['type_3'] == 'reel':
                    del instance['sub_container']['type_3']
                    del instance['sub_container']['indicator_3']
    return record_json

def add_access_notes(record_json, hm_call_number):
    exists = 0
    if len(record_json['notes']) > 0:
        for note in record_json['notes']:
            if note['type'] == 'accessrestrict':
                if 'This material has been microfilmed' in note['subnotes'][0]['content']:
                    print('Note exists!')
                    exists = 1
    if exists == 0:
        record_json = create_access_note(record_json, hm_call_number)
    return record_json

def create_access_note(record_json, external_id):
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

def create_backups(dirpath, ao_uri, record_json):
    outfile = u.openoutfile(filepath=dirpath + '/' + ao_uri[1:].replace('/','_') + '.json')
    json.dump(record_json, outfile, sort_keys=True, indent=4)

'''Can start implementing the process_data module here, but need to move the rows out of the update data func'''
@logtime
def update_data(api_url, headers, csvfile, dirpath):
    for i, row in enumerate(csvfile, 1):
        try:
            tc_uri = row[0]
            ao_uri = row[1]
            hm_call_number = row[2]
            record_json = requests.get(api_url + ao_uri, headers=headers).json()
            create_backups(dirpath, ao_uri, record_json)
            record_json = delete_subcontainers(record_json)
            record_json = create_instance(record_json, tc_uri)
            record_json = create_external_id(record_json, hm_call_number)
            #only want this here for partially filmed collections; otherwise the access note
            #goes at the resource level; can expand this to do that too, though most wholly
            #filmed collections are already done.
            record_json = add_access_notes(record_json, hm_call_number)
            record_post = requests.post(api_url + ao_uri, headers=headers, json=record_json).json()
            if 'error' in record_post:
                print(record_post.get('error'))
        except Exception as exc:
            print(ao_uri)
            print(traceback.format_exc())
    print(f'Rows processed: {i}')

def main():
    api_url, headers = u.login(url="https://archivesspace.library.yale.edu/api", username="amd243", password="FFmIjc5xLw")
    header_row, csvfile = u.opencsv(input_csv="/Users/amd243/Desktop/children_out.csv")
    dirpath = u.setdirectory("/Users/amd243/Desktop/children_out_prodbackups")
    update_data(api_url, headers, csvfile, dirpath)

if __name__ == "__main__":
    main()