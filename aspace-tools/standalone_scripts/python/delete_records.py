#/usr/bin/python3
#~/anaconda3/bin/python

import requests, json, logging, time, traceback
from utilities import utilities

#this can work for any kind of AS object that has its own URI - i.e. agents, subjects, archobjs, resource, dos, classifications, etc.
def delete_records(api_url, headers, csvfile):
    #log_file_name = input('Please enter path to log file: ')
    utilities.error_log()
    starttime = time.time()
    dirpath = utilities.setdirectory('/Users/amd243/Dropbox/2019_may_desktop/unassociated_backups')
    x = 0
    for i, row in enumerate(csvfile, 1):
        record_uri = row[0]
        try:
            record_json = requests.get(api_url + record_uri, headers=headers).json()
            if 'error' in record_json:
                logging.debug('error: could not retrieve ' + str(record_uri))
                logging.debug(str(record_json.get('error')))
            outfile = utilities.openoutfile(filepath=dirpath + '/' + record_uri[1:].replace('/','_') + '.json')
            json.dump(record_json, outfile)
            delete = requests.delete(api_url + record_uri, headers=headers, json=record_json).json()
            print(delete)
            if 'status' in delete.keys():
                x += 1
            if 'error' in delete.keys():
                logging.debug(str(record_uri))
                logging.debug('log: ' + str(delete.get('error')))   
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

def main():
    api_url, headers = utilities.login()
    csvheaders, csvfile = utilities.opencsv()
    delete_records(api_url, headers, csvfile)

if __name__ == "__main__":
    main()