#/usr/bin/python3
#~/anaconda3/bin/python

'''TO-DO
Abstraction
Class

Was thinking about adding a dictionary input for the different project index column values

Just add the repo uri to the config file rather than repeat it several times in the dict
'''

import csv, ast, json, traceback, requests, time, logging, sys, subprocess, os, yaml, pprint

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

class Pindex():
    #load a configuration file here?
    def __init__(self, resource_id, config_file=None):
        self.config_file = self._get_config(config_file)
        self.baseurl = self.config_file['api_url']
        self.un = self.config_file['username']
        self.pw = self.config_file['password']
        self.repo_uri = self.config_file['repo_uri']
        self.resource_id = resource_id
        self.project_json = self.read_json(self.config_file['jsonpath'])
        self.exclusions = ['Location', 'Title', 'Date', 'State', 'Job', 'Project Type', 'Collaborator', 
                            'Photographer', 'Barcode', 'Restricted', 'Range', 'Client']
        #include args here? rather than adding as an attribute; think I need baseurl at least
        self.headers = self.login()

    def _get_config(self, cfg):
        if cfg != None:
            cfg_file = yaml.load(open(cfg, 'r', encoding='utf-8'))
            return cfg_file
        else:
            cfg_file = yaml.load(open('config.yml', 'r', encoding='utf-8'))
            return cfg_file

    #only gets the json bit for the collection being worked on - should create a new instance for
    #each project
    def read_json(self, fp):
        with open(fp) as jsonfile:
            data = json.load(jsonfile)
            return data[self.resource_id]

    #Call this in __init__ to save the session; maybe add something to allow for user input?
    def login(self):
        try:
            auth = requests.post(self.baseurl+'/users/'+self.un+'/login?password='+self.pw).json()
            #if session object is returned then login was successful; if not it failed.
            if 'session' in auth:
                session = auth["session"]
                h = {'X-ArchivesSpace-Session':session, 'Content_Type': 'application/json'}
                print('Login successful!')
                logging.debug('Success!')
                return h
            else:
                print('Login failed! Check credentials and try again')
                logging.debug('Login failed')
                logging.debug(auth.get('error'))
        except:
            print('Login failed! Check credentials and try again!')
            logging.exception('Error: ')

    '''open a csv in reader mode. Can add optional message to help distinguish between multiple csvs

    Use a different open csv function here this isn't the best one'''
    #Open a CSV in reader mode
    def opencsv(self, input_csv=None):
        try:
            if input_csv is None:
                input_csv = input('Please enter path to CSV: ')
            file = open(input_csv, 'r', encoding='utf-8')
            csvin = csv.reader(file)
            headline = next(csvin, None)
            return headline, csvin
        except:
            logging.exception('Error: ')
            logging.debug('Trying again...')
            print('CSV not found. Please try again.')
            h, c = opencsv()
            return h, c

    #Open a CSV in dictreader mode
    def opencsvdict(self, input_csv=None):
        try:
            if input_csv is None:
                input_csv = input('Please enter path to CSV: ')
            file = open(input_csv, 'r', encoding='utf-8')
            csvin = csv.DictReader(file)
            return csvin
        except:
            logging.exception('Error: ')
            logging.debug('Trying again...')
            print('CSV not found. Please try again.')
            c = self.opencsvdict()
            return c

    def opencsvdictout(self, output_csv=None, col_names=None):
        try:
            if output_csv is None:
                output_csv = input('Please enter path to CSV: ')
            file = open(output_csv, 'a', newline='', encoding='utf-8')
            if col_names != None:
                csvin = csv.DictWriter(file, col_names)
                csvin.writeheader()
            else:
                csvin = csv.DictWriter(file)
            return csvin
        except:
            logging.exception('Error: ')
            logging.debug('Trying again...')
            print('CSV not found. Please try again.')
            c = self.opencsvdictout()
            return c

    #Open a CSV file in writer mode
    def opencsvout(self, output_csv=None):
        try:
            if output_csv is None:
                output_csv = input('Please enter path to output CSV: ')
            fileob = open(output_csv, 'a', encoding='utf-8', newline='')
            csvout = csv.writer(fileob)
            return (fileob, csvout)
        except:
            logging.exception('Error: ')
            print('\nError creating outfile. Please try again.\n')
            f, c = opencsvout()
            return (f, c)

    def openjson(self, directory, filename):
        filepath = open(directory + '/' + filename + '.json', 'a', encoding='utf-8')
        return filepath

    def keeptime(self, start):
        elapsedtime = time.time() - start
        m, s = divmod(elapsedtime, 60)
        h, m = divmod(m, 60)
        logging.debug('Total time elapsed: ' + '%d:%02d:%02d' % (h, m, s) + '\n')

    def setdirectory(self):
        directory = input('Please enter path to output directory: ')
        return directory

    '''Creates new archival objects out of project index lists - top level only, no instances attached yet
    '''

    def _check_dates(self, date_value, split_type):
        split_date = date_value.split(split_type)
        #need to make sure that there are no other n.d. types here
        #should I do commas first or 2nd??
        for d in split_date:
            #doesn't seem like this happens much 
            if '-' in d:
                new_date = d.split('-')
                split_date.append(new_date)
                split_date.remove(d)
            elif ',' in d:
                if ', ' in d:
                    new_date = d.split(', ')
                else:
                    new_date = d.split(',')
                split_date = split_date.append(new_date)
                split_date.remove(d)
        return split_date

    def create_project_objects(self):
        starttime = time.time()
        csvfile = self.opencsvdict(input_csv=self.project_json['project_index_report'])
        fieldnames = csvfile.fieldnames
        print(fieldnames)
        csvoutfile = self.opencsvdictout(output_csv= self.project_json['project_index_w_ao_uris'], col_names=fieldnames)
        x = 0
        for i, row in enumerate(csvfile, 1):
            try:
                title = row['Title']
                date = row['Date']
                logging.debug('Working on row ' + str(i) + ': ' + title)
                new_ao = {'title': title, 'level': 'file', 'repository': {'ref': self.repo_uri},
                        'resource': {'ref': self.project_json['resource_uri']}, 'parent': {'ref': self.project_json['project_series']},
                        'jsonmodel_type': 'archival_object','publish': True, 'dates': []}
                if date != '':
                    if ',' in date:
                        #NoneType error here
                        if ', ' in date:
                            split_date = self._check_dates(date, ', ')
                        else:
                            split_date = self._check_dates(date, ',')
                        for d in split_date:
                            if type(d) is list:
                                new_date = {'jsonmodel_type': 'date', 'date_type': 'single', 'label': 'creation',
                                                'begin': d[0], 'end': d[1]}
                            else:
                                new_date = {'jsonmodel_type': 'date', 'date_type': 'single', 'label': 'creation',
                                                'begin': d}
                            new_ao['dates'].append(new_date)
                    elif '-' in date:
                        split_date = self._check_dates(date, '-')
                        new_ao['dates'] = [{'jsonmodel_type': 'date', 'date_type': 'inclusive', 'label': 'creation',
                                             'begin': split_date[0], 'end': split_date[1]}]
                    elif '-' not in date and ',' not in date:
                        new_ao['dates'] = [{'jsonmodel_type': 'date', 'begin': date, 'label': 'creation',
                                             'date_type': 'single'}]
                ao_create = requests.post(self.baseurl + self.repo_uri + '/archival_objects', headers=self.headers, json=new_ao).json()
                print(ao_create)
                if 'status' in ao_create:
                    x += 1
                    logging.debug('Created: ' + ao_create['uri'])
                    row['uri'] = ao_create['uri']
                if 'error' in ao_create:
                    logging.debug(str(i))
                    logging.debug('Error: ' + str(ao_create.get('error')) + '\n')
            except Exception as exc:
                print(i)
                print(traceback.format_exc())
                logging.debug(i)
                logging.exception('Error: ')
                continue
            logging.debug('Writing to file...')
            csvoutfile.writerow(row)
        logging.debug('Total update attempts: ' + str(i))
        logging.debug('Records updated successfully: ' + str(x))
        self.keeptime(starttime)
        print('All Done!')

    '''uri_action and add_uris_to_csv takes a csv of project file top containers and links them to an edited
    form of the project index
    csvlist ex: /Users/aliciadetelich/Dropbox/project_indexes/3557_ms1842_tc_report.csv
    csvlist2 ex: /Users/aliciadetelich/Dropbox/project_indexes/mssa_ms_1842_project_index.csv 

    '''

    def _hyphen_value(self, thing):
        split_range = thing.split('-')
        low_range = int(split_range[0])
        high_range = int(split_range[1])
        all_ranges = list(range(low_range, high_range + 1))
        return all_ranges

    '''check to see if any of these modifications work...'''
    def _uri_action(self, column_value):
        '''I think but am not sure that all of the top container reports should be in the same format

        make sure that the aliases I created for some of these variables are unnecessary. I can't remember
        now why I did it that way.
        Do a dictreader for this too since all the headers are the same. Actually can't since I need
        it as a list; how about just open the file and iterate rather than creating a generator
        '''
        header_row, tc_report = self.opencsv(input_csv=self.project_json['tc_report'])
        tc_report = [row for row in tc_report]
        if ',' in column_value:
            if ', ' in column_value:
                split_values = column_value.split(", ")
            else:
                split_values = column_value.split(",")
            for enum, item in enumerate(split_values):
                if '-' in item:
                    all_ranges = self._hyphen_value(item)
                    split_values = split_values + all_ranges
                    split_values.remove(item)
            column_value = split_values
            for enum, box in enumerate(column_value):
                for i in tc_report:
                    tc_uri = i[0]
                    container_num = i[1]
                    if str(box).strip() == container_num:
                        column_value[enum] = tc_uri
        else:
            if '-' in column_value:
                all_ranges = self._hyphen_value(column_value)
                column_value = all_ranges
                for box in column_value:
                    for i in tc_report:
                        tc_uri = i[0]
                        container_num = i[1]
                        if str(box) == container_num:
                            column_value = tc_uri
            else:
                for i in tc_report:
                    tc_uri = i[0]
                    container_num = i[1]
                    if column_value.strip() == container_num:
                        column_value = tc_uri
        return column_value

    #this function calls the uri action function repeatedly
    #should refactor this even though I won't really use it more than a couple more times
    def add_uris(self):
        project_index = self.opencsvdict(input_csv=self.project_json['project_index_w_ao_uris'])
        fieldnames = project_index.fieldnames
        #do I need to close this also?? Do I need to write the fieldnames to the outfile??
        #did I finish this before? Wait, should work because also using a CSV dict; so maybe should do that
        csvoutfile = self.opencsvdictout(output_csv=self.project_json['dirpath'], col_names=fieldnames)
        for row in project_index:
            for item in row:
                if item.strip() not in self.exclusions:
                    if row[item] != '':
                        row[item] = self._uri_action(row[item])
            csvoutfile.writerow(row)
        #fileobject.close()

    '''These functions take the CSV output of the previous two functions and creates archival object which sit below
     each project index object
     WAIT - I need the dirpath though...maybe just assume that I will use a particular filename even if it isn't created
     yet
    ex: /Users/aliciadetelich/Dropbox/project_indexes/mssa_ms_1842_matched.csv
    '''

    def _ao_create(self, count, column_value, ao, title):
        new_ao = {'title': title, 'level': 'file', 'repository': {'ref': self.config_file['repo_uri']},
                      'resource': {'ref': self.project_json['resource_uri']}, 'parent': {'ref': ao},
                      'jsonmodel_type': 'archival_object', 'publish': True}
        if '[' in column_value:
            #converts the string representation of the list to a list
            tc_list = ast.literal_eval(column_value)
            #list comprehension to create an instance list
            new_ao['instances'] = [{'sub_container': {'jsonmodel_type': 'sub_container',
                                             'top_container': {'ref': tc.strip()}},
                           'instance_type': 'mixed_materials',
                           'jsonmodel_type': 'instance'} for tc in tc_list]
        else:
            new_ao['instances'] = [{'sub_container': {'jsonmodel_type': 'sub_container', 
                                                    'top_container': {'ref': column_value.strip()}},
                                    'instance_type': 'mixed_materials', 'jsonmodel_type': 'instance'}]
        new_ao_post = requests.post(self.baseurl + self.config_file['repo_uri'] + '/archival_objects', headers=self.headers, json=new_ao).json()
        print(new_ao_post)
        if 'status' in new_ao_post:
            count += 1
            logging.debug('Created: ' + new_ao_post['uri'])
        if 'error' in new_ao_post:
            logging.debug(str(ao))
            logging.debug(str(column_value))
            logging.debug('Error: ' + str(new_ao_post.get('error')) + '\n')
        return count

    #this function calls the one above it to create archival objects and top container records
    #can remove the column entry from the json dict thing - then can just use json loads too

    #COULD leave in the location and other stuff if I have a list of things to exclude; i.e.
    #if item not in exclusions. 

    def create_aos_tcs(self):
        starttime = time.time()
        csvfile = self.opencsvdict(input_csv=self.project_json['dirpath'])
        x = 0
        for i, row in enumerate(csvfile, 1):
            try:
                for item in row:
                    #did I try if not row['uri'] - I thought I did and it didn't work...
                    if item == 'uri':
                        ao_uri = row['uri']
                    if item != 'uri':
                        #this is a little convoluted but should work?? Don't want to delete everything...
                        #also need to add photographer, etc.
                        if item not in self.exclusions:
                            if row[item] != '':
                                x = self._ao_create(x, row[item], ao_uri, item)
            except Exception:
                logging.debug(ao_uri)
                logging.exception('Error: ')
                print(ao_uri)
                print(traceback.format_exc())
                continue
        logging.debug('Projects processed: ' + str(i))
        logging.debug('Records created: ' + str(x))
        self.keeptime(starttime)
        print('All Done!')

    def delete_instances(self):
        ao_json = requests.get(self.baseurl + self.project_json['project_series'], headers=self.headers).json()
        outfile = self.openjson(self.project_json['project_dir'], self.project_json['project_series'][1:].replace('/','_'))
        json.dump(ao_json, outfile)
        ao_json['instances'] = []
        record_post = requests.post(self.baseurl + self.project_json['project_series'], headers=self.headers, json=ao_json).json()
        print(record_post)

error_log(filepath='log.log')
