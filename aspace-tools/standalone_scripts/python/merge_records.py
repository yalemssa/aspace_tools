#/usr/bin/python3
#~/anaconda3/bin/python

import requests, json, logging, time, traceback
from utilities import utilities

def record_check_helper(vic_json, k, target_json, exclusions):
    for item in vic_json[k]:
        new_item = {}
        for key, value in item.items():
            if key not in exclusions:
                new_item[key] = value
        target_json[k].append(new_item)

def record_check(api_url, headers, victim_json, target):
    print('target: ' + str(target))
    target_record = requests.get(api_url + target, headers=headers).json()
    exclusions = ['create_time', 'created_by', 'last_modified_by', 'lock_version',
                    'system_mtime', 'user_mtime']
    #if its an empty list it will be false
    if victim_json['agent_contacts']:
        print('victim has contact info')
        record_check_helper(victim_json, 'agent_contacts', target_record, exclusions)
    if victim_json['dates_of_existence']:
        print('victim has dates')
        record_check_helper(victim_json, 'dates_of_existence', target_record, exclusions)
    if victim_json['notes']:
        print('victim has notes')
        record_check_helper(victim_json, 'notes', target_record, exclusions)
    return target_record

def merge_records(record_type):
    starttime = time.time()
    api_url, headers = utilities.login()
    _, csvfile = utilities.opencsv()
    dirpath = utilities.setdirectory()
    x = 0
    for i, row in enumerate(csvfile, 1):
        try:
            target = row[0]
            victim = row[1]
            # victim_refs = [{'ref': victim} for victim in victims.split(', ')]
            # for v in victims.split(', '):
            victim_backup = requests.get(api_url + victim, headers=headers).json()
            if 'error' in victim_backup:
                logging.debug('error: could not retrieve ' + str(victim))
                logging.debug(str(victim_backup.get('error')))
            outfile = utilities.openoutfile(filepath=dirpath + '/' + victim[1:].replace('/','_'))
            json.dump(victim_backup, outfile)
            merge_json = {'target': {'ref': target}, 
                          'victims': [{'ref': victim}], 
                          'jsonmodel_type': 'merge_request'}
            merge_request = requests.post(api_url + '/merge_requests/' + str(record_type), headers=headers, json=merge_json).json()
            print(merge_request)
            target_json = record_check(api_url, headers, victim_backup, target)
            logging.debug('Posting updates to target record')
            target_post = requests.post(api_url + target, headers=headers, json=target_json).json()
            logging.debug(target_post)
            #can take this out - have a function in utilities to handle.
            if 'status' in merge_request:
                    x += 1
            if 'error' in merge_request:
                    logging.debug('target: ' + str(target))
                    logging.debug('victim: ' + str(victim))
                    logging.debug('log: ' + str(merge_request.get('error')))
        except Exception as exc:
            print(target)
            print(traceback.format_exc())
            logging.debug(target)
            logging.exception('Error: ')
            continue
    logging.debug('Total update attempts: ' + str(i))
    #add count of successful updates to log file
    logging.debug('Records updated successfully: ' + str(x))
    utilities.keeptime(starttime)
    print('All Done!')

if __name__ == "__main__":
    log_input = input('Please enter path to log file: ')
    utilities.error_log(filepath=log_input)
    record_input = input('Please enter the record type you wish to merge (agent/subject): ')
    merge_records(record_input)