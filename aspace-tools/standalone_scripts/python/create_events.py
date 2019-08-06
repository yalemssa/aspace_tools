#/usr/bin/python3
#~/anaconda3/bin/python

import requests, json, os, time, traceback, sys, logging, csv
from utilities import utilities

#look up repositories, users
#create spreadsheet template for download

def create_events():
    starttime = time.time()
    api_url, headers = utilities.login()
    header_row, csvfile = utilities.opencsv()
    dirpath = utilities.setdirectory()
    x = 0
    for i, row in enumerate(csvfile, 1):
    	try:
    		#maybe dict_reader here? to work with spreadsheet column headers
    		#add external docs as optional entry
   			event_type = row[0]
   			outcome = row[1]
   			date_begin = row[2]
            #date_label = 'Digitized'
   			repo = row[3]
            external_documents = row[4]
            record_link = row[5]
            agent = row[6]
            external_doc_title = row[7]
            external_doc_location = row[8]
            record_json = {'jsonmodel_type': 'event', 'event_type': event_type, 'outcome': outcome,
         				'date': {'begin': date_begin, 'date_type': 'single', 
         						'jsonmodel_type': 'date', 'label': 'event'}, 
         				'repository': {'ref': '/repositories/' + str(repo)},
         				'linked_records': [{'ref': record_link, 'role': 'source'}], 
         				'linked_agents': [{'role': 'authorizer', 'ref': agent}],
                        'external_documents': []}
            if external_doc_title != '':
                external_document = {'jsonmodel_type': 'external_document', 'location': external_doc_location,
                                        'title': external_doc_title}
                record_json['external_documents'].append(external_document)
            record_update = requests.post(api_url + '/repositories/' + repo + '/events', headers=headers, json=record_json).json()
            if 'status' in record_update:
                x += 1
            if 'error' in record_update:
                #change this to indicate spreadsheet row?
                logging.debug('error: could not create record on row' + str(i))
                logging.debug('log: ' + str(record_update.get('error')))
                print(record_update)
        except Exception as exc:
        	#change this to indicate spreadsheet row?
            print(record_uri)
            print(traceback.format_exc())
            #change this to indicate spreadsheet row?
            logging.debug('Could not create record on row ' + str(i))
            logging.exception('Error: ')
            continue
    utilities.keeptime(starttime)
    logging.debug('Total update attempts: ' + str(i))
    logging.debug('Records updated successfully: ' + str(x))
    print('All Done!')

def main()
    log_input = input('Please enter path to log file: ')
    utilities.error_log(filepath=log_input)
    create_events()

if __name__ == '__main__':
    main()

