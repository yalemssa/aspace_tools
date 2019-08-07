#Python 3

#This script updates locations which were incorrectly migrated into AS

#TO-DO - write log to file

import utilities, requests, json, csv, time, logging, traceback

def update_coordinates():
    starttime = time.time()
    api_url, headers = utilities.login()
    csvfile = utilities.opencsv()
    dirpath = utilities.setdirectory()
    x = 0
    for i, row in enumerate(csvfile, 1):
        record_uri = row[0]
        room = row[1]
        # coordinate_1_label = row[1]
        # coordinate_1_indicator = row[2]
        # coordinate_2_label = row[3]
        # coordinate_2_indicator = row[4]
        # coordinate_3_label = row[5]
        # coordinate_3_indicator = row[6]
        try:
            record_json = requests.get(api_url + record_uri, headers=headers).json()
            if 'error' in record_json:
                logging.debug('error: could not retrieve ' + str(record_uri))
                logging.debug(str(record_json.get('error')))
            outfile = utilities.openjson(dirpath, record_uri[1:].replace('/','_'))
            json.dump(record_json, outfile)
            record_json['room'] = room
            # record_json['coordinate_1_indicator'] = coordinate_1_indicator
            # record_json['coordinate_1_label'] = coordinate_1_label
            # record_json['coordinate_2_indicator'] = coordinate_2_indicator
            # record_json['coordinate_2_label'] = coordinate_2_label
            # record_json['coordinate_3_indicator'] = coordinate_3_indicator
            # record_json['coordinate_3_label'] = coordinate_3_label
            record_data = json.dumps(record_json)
            record_update = requests.post(api_url + record_uri, headers=headers, data=record_data).json()
            print(record_update)
            if 'status' in record_update:
                x += 1
            if 'error' in record_update:
                logging.debug(str(record_uri))
                logging.debug('log: ' + str(record_update.get('error')))   
        except Exception as exc:
            print(record_uri)
            print(traceback.format_exc())
            logging.debug(record_uri)
            logging.exception('Error: ')
            continue
    print('Total update attempts: ' + str(i))
    print('Records updated successfully: ' + str(x))
    logging.debug('Total update attempts: ' + str(i))
    #add count of successful updates to log file
    logging.debug('Records updated successfully: ' + str(x))
    utilities.keeptime(starttime)  
    print('All Done!')

if __name__ == "__main__":
    utilities.error_log()
    update_coordinates()
