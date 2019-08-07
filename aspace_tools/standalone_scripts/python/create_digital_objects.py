#/usr/bin/python3
#~/anaconda3/bin/python

'''This script creates new digital objects with links to archival objects, a digital library,
and thumbnail representations of digital library materials'''

import requests, csv, json, time, traceback, logging

def error_log(filepath=None):
    """Initiates an error log."""
    if sys.platform == "win32":
        if filepath == None:
            logger = '\\Windows\\Temp\\error_log.log'
        else:
            logger = filepath
    else:
        if filepath == None:
            logger = '/tmp/error_log.log'
        else:
            logger = filepath
    logging.basicConfig(filename=logger, level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s %(name)s %(message)s')

def login(url=None, username=None, password=None):
    """Logs into the ArchivesSpace API"""
    import requests
    try:
        if url is None and username is None and password is None:
            url = input('Please enter the ArchivesSpace API URL: ')
            username = input('Please enter your username: ')
            password = input('Please enter your password: ')
        auth = requests.post(url+'/users/'+username+'/login?password='+password).json()
        #if session object is returned then login was successful; if not it failed.
        if 'session' in auth:
            session = auth["session"]
            h = {'X-ArchivesSpace-Session':session, 'Content_Type': 'application/json'}
            print('Login successful!')
            logging.debug('Success!')
            return (url, h)
        else:
            print('Login failed! Check credentials and try again.')
            logging.debug('Login failed')
            logging.debug(auth.get('error'))
            #try again
            u, heads = login()
            return u, heads
    except:
        print('Login failed! Check credentials and try again!')
        logging.exception('Error: ')
        u, heads = login()
        return u, heads


#Open a CSV in reader mode
def opencsv(input_csv=None):
    """Opens a CSV in reader mode."""
    try:
        if input_csv is None:
            input_csv = input('Please enter path to CSV: ')
        if input_csv == 'quit':
            quit()
        file = open(input_csv, 'r', encoding='utf-8')
        csvin = csv.reader(file)
        headline = next(csvin, None)
        return headline, csvin
    except:
        logging.exception('Error: ')
        logging.debug('Trying again...')
        print('CSV not found. Please try again. Enter "quit" to exit')
        h, c = opencsv()
        return h, c

#Create digital objects and archival object instances
def create_digital_objects():
    uri_list = []
    for i, row in enumerate(csvfile, 1):
        archival_object_uri = row[0]
        dig_lib_url = row[1]
        thumbnail_url = row[2]
        dig_object_id = row[3]
        dig_object_title = row[4]
        try:
            new_digital_object = {'jsonmodel_type': 'digital_object',
                                  'publish': True, 
                                  'file_versions': [{'file_uri': dig_lib_url, 'jsonmodel_type': 'file_version', 
                                                     'xlink_show_attribute': 'new', 'publish': True}, 
                                                     {'file_uri': thumbnail_url, 'jsonmodel_type': 'file_version', 
                                                                                      'xlink_show_attribute': 'embed', 'publish': True}],
                                  'digital_object_id': dig_object_id,
                                  'title': dig_object_title}
            record_update = requests.post(api_url + '/repositories/' + str(repo_num) + '/digital_objects', headers=headers, json=new_digital_object).json()
            '''If the digital object is created successfully, then have to create a new archival object instance in order
            to link the two - cannot do it in the digital object JSON itself, only the archival object JSON'''
            #The 'status' key only appears if an update is successful
            if 'status' in record_update:
                #get the URI for the new digital object
                new_do_uri = record_update.get('uri')
                #adds to list of URIs - will write these to outfile
                uri_list.append(new_do_uri)
                update_ao_instance(api_url, headers, new_do_uri, archival_object_uri)
            #if digital object not created, write error to log and print to console
            elif 'error' in record_update:
                logging.debug('error: could not create digital object for id ' + str(dig_object_id))
                logging.debug(str(record_update.get('error')))
                print(record_update)
        #if an exception is raised at any point, write to error log, print to console, and continue.
        except Exception:
            print(dig_object_id)
            print(traceback.format_exc())
            logging.debug(dig_object_id)
            logging.exception('Error')
            continue
    #Writes a list of URLs to the new digital objects (staff interface view) to the outfile
    for uri in uri_list:
        urisplit = uri.split('/')
        logging.debug(values[0][:-3] + urisplit[-2] + '/' + urisplit[-1])
    print('All Done!')

def update_ao_instance(api_url, headers, new_do_uri, archival_object_uri):
    record_json = requests.get(api_url + archival_object_uri, headers=headers).json()
    new_ao_instance = {'jsonmodel_type': 'instance', 'instance_type': 'digital_object',
                       'digital_object': {'ref': new_do_uri}}
    record_json['instances'].append(new_ao_instance)
    ao_update = requests.post(api_url + archival_object_uri, headers=headers, data=record_json).json()
    #if not successful, write error to log and print to console
    if 'error' in ao_update:
        logging.debug('error: could not create digital object instance for ' + str(new_do_uri))
        logging.debug(str(ao_update.get('error')))
        print(ao_update)

def main():
    error_log()
    api_url, headers = login()
    repo_num = input('Please enter your repository number: ')
    header_row, csvfile = opencsv()
    create_digital_objects(api_url, headers, repo_num, csvfile)


if __name__ == "__main__":
    main()
