#/usr/bin/python3
#~/anaconda3/bin/python

import utilities, requests, json, logging, time, traceback

def add_local_type():
    starttime = time.time()
    api_url, headers = utilities.login()
    csvheaders, csvfile = utilities.opencsv()
    dirpath = utilities.setdirectory()
    x = 0
    for i, row in enumerate(csvfile, 1):
        record_uri = row[0]
        persistent_id = row[1]
        local_type = row[2]
        begin = row[3]
        end = row[4]
        try:
            record_json = requests.get(api_url + record_uri, headers=headers).json()
            if 'error' in record_json:
                logging.debug('error: could not retrieve ' + str(record_uri))
                logging.debug(str(record_json.get('error')))
            outfile = utilities.openjson(dirpath, record_uri[1:].replace('/','_'))
            json.dump(record_json, outfile)
            for note in record_json['notes']:
                if note['persistent_id'] == persistent_id:
                    note['rights_restriction']['local_access_restriction_type'].append(local_type)
                if begin != '':
                    #make sure that this is the correct format; only one date restriction per note, yes?
                    note['rights_restriction']['begin'] = begin
                if end != '':
                    note['rights_restriction']['end'] = end
            record_post = requests.post(api_url + record_uri, headers=headers, json=record_json).json()
            print(record_post)
            if 'status' in record_post:
                x += 1
            if 'error' in record_post:
                logging.debug(str(record_uri))
                logging.debug('log: ' + str(record_post.get('error')))   
        except Exception as exc:
            print(record_uri)
            print(traceback.format_exc())
            logging.debug(record_uri)
            logging.exception('Error: ')
            continue
    logging.debug('Total update attempts: ' + str(i))
    #add count of successful updates to log file
    logging.debug('Records updated successfully: ' + str(x))
    utilities.keeptime(starttime)  
    print('All Done!')

if __name__ == "__main__":
    log_file_name = input('Please enter path to log file: ')
    utilities.error_log(filepath=log_file_name)
    add_local_type()