#/usr/bin/python3
#~/anaconda3/bin/python

import utilities, requests, json, os, time, traceback, sys

#Can use this to update single parts of a date record; will update all dates in a single record as it loops through
def update_subrecord_components(subrecord, *fields):
    starttime = time.time()
    values = utilities.login()
    headers, csvfile = utilities.opencsv()
    dirpath = utilities.setdirectory()
    x = 0
    for i, row in enumerate(csvfile, 1):
        record_uri = row['uri']
        try:
            record_json = requests.get(values[0] + record_uri, headers=values[1]).json()
            #Stores the "before" JSON in a directory specified by the user
            if 'error' in record_json:
                logging.debug('error: could not retrieve ' + str(record_uri))
                logging.debug(str(record_json.get('error')))
            outfile = admin.openjson(dirpath, record_uri[1:].replace('/','_'))
            json.dump(record_json, outfile)
            for field in fields:
                for key, value in row.items():
                    if field == key:
                        if key == 'repository':
                            record_json[subrecord][0][key] = {'ref': value}
                        else:
                            #this needs the position because it doesn't update every one, just the first.
                            #all the more reason we need IDs for this stuff.     
                                                              
                            record_json[subrecord][0][key] = value
            record_data = json.dumps(record_json)
            record_update = requests.post(values[0]+ record_uri, headers=values[1], data=record_data).json()
            print(record_update)
            if 'status' in record_update.keys():
                x += 1
            if 'error' in record_update.keys():
                logging.debug('error: could not update ' + str(record_uri) + '\n')
                logging.debug('log: ' + str(record_update.get('error')) + '\n')
                print(record_update)
                #txtout.write(str(resource_uri + '\n'))
        except Exception as exc:
            print(record_uri)
            print(traceback.format_exc())
            logging.debug(record_uri)
            logging.exception('Error: ')
            continue
    utilities.keeptime(starttime)
    logging.debug('Total update attempts: ' + str(i))
    #add count of successful updates to log file
    logging.debug('Records updated successfully: ' + str(x))
    print('All Done!')

if __name__ == "__main__":
    utilities.error_log()
    subrec_type = input('What type of subrecord are you updating?: ')
    component_list = input('What fields would you like to update?: ')
    update_subrecord_component(subrec_type, component_list)