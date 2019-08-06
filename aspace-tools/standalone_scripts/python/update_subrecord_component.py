#/usr/bin/python3
#~/anaconda3/bin/python

import utilities, requests, json, os, time, traceback, sys, logging, csv

#change to csvdict...
def update_subrecord_component(subrecord, component, qual=None):
    starttime = time.time()
    values = utilities.login()
    headers, csvfile = utilities.opencsv()
    dirpath = utilities.setdirectory()
    x = 0
    for i, row in enumerate(csvfile, 1):
        record_uri = row[0]
        sort_name = row[1]
        new_text = row[2]
        try:
            record_json = requests.get(values[0] + record_uri, headers=values[1]).json()
            if 'error' in record_json:
                logging.debug('error: could not retrieve ' + str(record_uri))
                logging.debug(str(record_json.get('error')))
            outfile = utilities.openjson(dirpath, record_uri[1:].replace('/','_'))
            json.dump(record_json, outfile)
            if qual != None:
                for item in record_json[subrecord]:
                    if item[component] != qual:
                        item[component] = 'lcsh'
            else:
                #i.e for name dict in record_json['names']
                # if 'dates' in record_json['display_name']:
                #     if record_json['display_name']['dates'].endswith('.'):
                #         new_date = record_json['display_name']['dates'][:-1]
                #         print(new_date)
                #         record_json['display_name']['dates'] = new_date
                for name in record_json['names']:
                    if 'dates' in name:
                        if name['dates'].endswith('.'):
                            name['dates'] = name['dates'][:-1]
                    #item[component] = updated_text
                    #i.e. if name['rest_of_name'] == rest_of_name; make sure to use the right name...
                    # if 'qualifier' in name:
                    #     if name['sort_name'] == sort_name:
                    #         name['qualifier'] = new_text
                        #and ends with a period
                        # if item[component].endswith('.'):
                        #     if item[component].endswith('etc.'):
                        #         print(item[component])
                        #     else:
                        #         item[component] = item[component][:-1]
                        #         x += 1
            #add something here that will look for a matc in the csv itself.
            record_data = json.dumps(record_json)
            record_update = requests.post(values[0]+ record_uri, headers=values[1], data=record_data).json()
            print(record_update)
            if 'status' in record_update.keys():
                x += 1
            if 'error' in record_update.keys():
                logging.debug('error: could not update ' + str(record_uri) + '\n')
                logging.debug('log: ' + str(record_update.get('error')) + '\n')
                print(record_update)
        except Exception as exc:
            print(record_uri)
            print(traceback.format_exc())
            logging.debug(record_uri)
            logging.exception('Error: ')
            continue
    utilities.keeptime(starttime)
    logging.debug('Total update attempts: ' + str(i))
    logging.debug('Records updated successfully: ' + str(x) + '\n')
    print('All Done!')

if __name__ == "__main__":
    log_input = input('Please enter path to log file')
    utilities.error_log(filepath=log_input)
    subrec = input('Please enter subrecord type: ')
    comp = input('Please enter component to update: ')
    qual = input('Would you like to qualify your update by term? Enter term if yes, enter N if no: ')
    if qual == 'N':
        update_subrecord_component(subrec, comp)
    if qual != 'N':
        update_subrecord_component(subrec, comp, qual)