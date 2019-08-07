import csv, requests, json, traceback, logging, sys

def error_log(filepath=None):
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
    return logger

def login():
    api_url = input('Please enter the ArchivesSpace API URL: ')
    username = input('Please enter your username: ')
    password = input('Please enter your password: ')
    auth = requests.post(api_url+'/users/'+username+'/login?password='+password).json()
    #if session object is returned then login was successful; if not it failed.
    if 'session' in auth:
        session = auth["session"]
        headers = {'X-ArchivesSpace-Session':session}
        print('Login successful!')
        return (api_url, headers)
    else:
        print('Login failed! Check credentials and try again')
        return

def opencsv():
    '''This function opens a csv file'''
    input_csv = input('Please enter path to CSV: ')
    file = open(input_csv, 'r', encoding='utf-8')
    csvin = csv.reader(file)
    next(csvin, None)
    return csvin

def opentxt():
    filepath = input('Please enter path to output text file: ')
    filename = open(filepath, 'a', encoding='utf-8')
    return filename

def setdirectory():
    directory = input('Please enter path to backup directory: ')
    return directory

def openjson(directory, filename):
    filepath = open(directory + '/' + filename + '.json', 'w', encoding='utf-8')
    return filepath

def replace_note_by_id():
    error_log()
    #replaces a note's content in ArchivesSpace using a persistent ID
    api_url, headers = login()
    csvfile = opencsv()
    dirpath = setdirectory()
    for i, row in enumerate(csvfile, 1):
        record_uri = row[0]
        persistent_id = row[1]
        new_text = row[2]
        try:
            record_json = requests.get(api_url + record_uri, headers=headers).json()
            outfile = openjson(dirpath, record_uri[1:].replace('/','_'))
            json.dump(record_json, outfile)
            for note in record_json['notes']:
                if note['jsonmodel_type'] == 'note_multipart':
                    if note['persistent_id'] == persistent_id:
                        note['subnotes'][0]['content'] = new_text
                elif note['jsonmodel_type'] == 'note_singlepart':
                    if note['persistent_id'] == persistent_id:
                        note['content'] = [new_text]
            record_update = requests.post(api_url + record_uri, headers=headers, json=record_json).json()
            if 'error' in record_update:
                logging.debug('error: could not update ' + str(resource_uri) + '\n')
                logging.debug('log: ' + str(resource_update.get('error')) + '\n')
        except Exception as exc:
            print('Something went wrong. Could not update ' + str(record_uri))
            print(traceback.format_exc())
            logging.debug('Something went wrong. Could not update ' + str(record_uri) + '\n')
            logging.exception('Error: ')
            continue

replace_note_by_id()
