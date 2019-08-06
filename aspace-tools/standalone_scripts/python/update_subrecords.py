import time, requests, json, csv

def login():
    api_url = input('Please enter the ArchivesSpace API URL: ')
    username = input('Please enter your username: ')
    password = input('Please enter your password: ')
    auth = requests.post(api_url+'/users/'+username+'/login?password='+password).json()
    #if session object is returned then login was successful; if not it failed.
    if 'session' in auth:
        session = auth["session"]
        headers = {'X-ArchivesSpace-Session':session, 'Content_Type':'application/json'}
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

def opencsvdict():
    '''This function opens a csv file in DictReader mode'''
    input_csv = input('Please enter path to CSV: ')
    file = open(input_csv, 'r', encoding='utf-8')
    csvin = csv.DictReader(file)
    return csvin

def opentxt():
    filepath = input('Please enter path to output text file: ')
    filename = open(filepath, 'a' )
    return filename

def update_subrecord_component(subrecord, component):
    starttime = time.time()
    values = admin.login()
    csvfile = admin.opencsv()
    txtout = admin.opentxt()
    x = 0
    y = 0
    for row in csvfile:
        x = x + 1
        resource_uri = row[0]    
        updated_text = row[1]
        try:
            resource_json = requests.get(values[0] + resource_uri, headers=values[1]).json()
            print(resource_json)
            #This doesn't need the position because it will update any value...careful!
            for date in resource_json[subrecord]:
                date[component] = updated_text
                resource_data = json.dumps(resource_json)
                resource_update = requests.post(values[0]+ resource_uri, headers=values[1], data=resource_data).json()
                print(resource_update)
                if 'status' in resource_update.keys():
                    y = y + 1
                if 'error' in resource_update.keys():
                    txtout.write('error: could not update ' + str(resource_uri) + '\n')
                    #this isn't working
                    txtout.write('log: ' + str(resource_update.get('error')) + '\n')
        except:
            txtout.write('could not locate object ' + str(resource_uri) + '\n')
            continue
    elapsedtime = time.time() - starttime
    m, s = divmod(elapsedtime, 60)
    h, m = divmod(m, 60)
    txtout.write('Total time elapsed: ')
    txtout.write('%d:%02d:%02d' % (h, m, s))
    txtout.write('\n' + 'Total update attempts: ' + str(x) + '\n')
    #add count of successful updates to log file
    txtout.write('Records updated successfully: ' + str(y) + '\n')
    txtout.close()

def update_subrecord_components(subrecord, *field):
    starttime = time.time()
    values = admin.login()
    csvfile = admin.opencsvdict()
    txtout = admin.opentxt()
    x = 0
    y = 0
    for row in csvfile:
        x = x + 1
        record_uri = row['uri']
        try:
            record_json = requests.get(values[0] + record_uri, headers=values[1]).json()
            for f in field:
                for key, value in row.items():
                    if f == key:
                        if key == 'repository':
                            record_json[subrecord][0][key] = {'ref': value}
                        else:
                            #this needs the position because it doesn't update every one, just the first.
                            #all the more reason we need IDs for this stuff.                                       
                            record_json[subrecord][0][key] = value
            record_data = json.dumps(record_json)
            record_update = requests.post(values[0] + record_uri, headers=values[1], data=record_data).json()
            print(record_update)
            if 'status' in record_update.keys():
                y = y + 1
            if 'error' in record_update.keys():
                txtout.write('error: could not update ' + str(record_uri) + '\n')
                txtout.write('log: ' + str(record_update.get('error')) + '\n')
        except:
            txtout.write('could not locate object ' + str(record_uri))
            continue            
    elapsedtime = time.time() - starttime
    m, s = divmod(elapsedtime, 60)
    h, m = divmod(m, 60)
    txtout.write('Total time elapsed: ')
    txtout.write('%d:%02d:%02d' % (h, m, s))
    txtout.write('\n' + 'Total update attempts: ' + str(x) + '\n')
    #add count of successful updates to log file
    txtout.write('Records updated successfully: ' + str(y) + '\n')
    txtout.close()

