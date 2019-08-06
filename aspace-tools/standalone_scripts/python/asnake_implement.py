#/usr/bin/python3
#~/anaconda3/bin/python

from asnake.client import ASnakeClient
import json, requests, time, csv, traceback
#remove pprint later...for debugging etc. now
import pprint

#Pretty empty now...                
class ASCreateTools():

    def __init__(self):
        self.client = ASnakeClient()
        self.auth = self.client.authorize()

class ASUpdateTools():
    
    def __init__(self):
        self.client = ASnakeClient()
        self.auth = self.client.authorize()
        #Any better way to get this data?
        self.records = ['resource', 'archival_object', 'digital_object', 'digital_object_component']
        self.subrecords = ['extent', 'file_version', 'instance', 'external_document',
                           'date', 'external_id']
        self.notes = ['multipart', 'singlepart', 'bioghist', 'index', 'abstract',
                      'bibliography']
    
    '''thinking about validating against the schema to get record types, etc.
    also possibly including methods for csv templates
    
    Currently cannot mix updates to top-level records and subrecords. Will perhaps
    add this functionality to the ASCreateTools class once I figure out how to do it.
    '''
    
    '''file i/o, error handling'''
    
    '''opens a csv file in DictReader mode'''
    def opencsvdict(self):
        input_csv = input('Please enter path to CSV: ')
        file = open(input_csv, 'r', encoding='utf-8')
        csvin = csv.DictReader(file)
        return(csvin)
    
    '''opens a text file in write mode'''
    def opentxt(self):
        filepath = input('Please enter path to output text file: ')
        filename = open(filepath, 'a', encoding='utf-8')
        return filename
    
    '''error handling
    To-Do - add ASnake logging'''
    def handle_errors(self, record_uri, exc, txtfile):
        print(record_uri)
        print(traceback.format_exc())
        print(exc)
        txtfile.write(record_uri + '\n')
        txtfile.write(str(traceback.format_exc()) + '\n')
        txtfile.write(str(exc) + '\n')
    
    '''various methods that can be passed to the update_data method'''
        
    '''for simple updates to top-level records'''
    def top_level(self, row, json_rec):
        for key, value in row.items():
            if key != 'uri':
                json_rec[key] = value
        return(json_rec)

    '''if all positions are the same, just add 0 or whatever to the list, else include that in an input spreadsheet. 
    Fairly easy to find position using enumerate and a get request and append to existing data in CSV form. Can
    then refer to the row in the variable assignment'''
    def subrecord(self, row, json_rec, *subrecpos):
        for key, value in row.items():
            if subrecpos != []:
                print(subrecpos)
            if key != 'uri':
                json_rec[subrecpos[0]][int(subrecpos[1])][key] = value
        return(json_rec)

    '''create new subrecord to append to existing top-level (resource, archival object, etc.) record; 
    i.e. new date, extent, file version, etc.'''
    def new_subrecord(self, row, json_rec, *subrec):
        '''the keys here are going to be something like date.begin'''
        json_form = {key: value for key, value in row.items() if key != 'uri'}
        #[0] gets inside the list...assumes you won't be adding different types of subrecord
        json_rec[subrec[0]].append(json_form)
        pprint.pprint(json_rec)
        return(json_rec)
    
    '''update notes using URI + persistent ID'''
    def notes(self, row, json_rec):
        for key, value in row.items():
            if key == 'persistent_id':
                if value == json_rec['notes']['persistent_id']:
                    pass
    
    '''Append data to a subrecord value list, or replace a a top level item(s)
    Must be sure to use the authorize method before this one...'''
    def update_data(self, method, *subrec_position):
        starttime = time.time()
        csvfile = self.opencsvdict()
        txtfile = self.opentxt()
        for i, row in enumerate(csvfile):
            try:
                uri = row['uri']
                record_json = self.client.get(uri).json()
                json_formed = method(row, record_json, *subrec_position)
                json_data = json.dumps(json_formed)
                record_post = self.client.post(uri, json_data).json()
                print(record_post)
            except Exception as exc:
                self.handle_errors(uri, exc, txtfile)
                continue

class ASDeleteTools():
    pass

'''create JSON and CSV templates for creating, updating (and occasionally deleting) AS data'''
class ASTemplates():
    
    def __init__(self):
        self.client = ASnakeClient()
        self.auth = self.client.authorize()
    
    def all_schemas(self):
        schemas = self.client.get('/schemas').json()
        pprint.pprint(schemas)
        return(schemas)
    
    '''in date json records the subrecord is pluralized (i.e. dates), but in the schema for that
    subrecord it is singular (i.e. date). Can be used recursively'''    
    def some_schemas(self, *schemas):
        schema_list = []
        for schema in schemas:
            schema = self.client.get('/schemas/' + str(schema)).json()
            p = schema['properties']
            key_dict = {key:value for key, value in p.items() if key != '_inherited'}
            schema_list.append(key_dict)
        return(schema_list)

    '''get full templates for top-level records by parsing the AS JSON schema
    In previous version I used some kind of recursive function to get the subrecs within subrecs...
    how did I do this? Maybe don't want to do the same thing since it was over 200 lines of code
    
    Should some of this be broken out into separate functions so can be run again?
    '''
    
    def get_subschema(self, keyval, recdic):
        #need to fix this 
        subschema = self.some_schemas(keyval)
        subdict = {k: None for k, v in subschema[0].items()}
        recdic[keyval] = [subdict]
        return(subdict, subschema)
    
    def full_records(self, *records):
        record_dict = {}
        for record in records:
            '''get the schema for an individual record. Or should I get the whole thing, since I'll need to
            retrieve the subrecords'''
            schema = self.client.get('/schemas').json()
            #limits to only the properties of a record. Do I really want to store this as a separate list?'''
            props = schema[record]['properties']
            some_types = ['string', 'boolean', 'integer']
            #loop through the properties sub-dictionary of the record schema'''
            for key, value in props.items():
                #add something to skip date-time types, so the create and mod times don't show up.
                #skips inherited values - these are indicated in the key
                if 'inherited' in key:
                    continue
                #skips anything that is read only - indicated in the values dict. does not get everything
                if 'readonly' in value.keys():
                    continue
                if value['type'] == 'array':
                    #checks for any refs - caputres things like subjects, linked agents
                    if 'subtype' in value['items'].keys():
                        record_dict[key] = {'ref': None}
                    else:
                        '''this gets subrecords such as date, extent, etc. Also need to check these for their own subrecords;
                        this currently causes an error when trying to call 'agent_person', etc.'''
                        if 'object' in value['items']['type']:
                            #this does not catch the names or anything that's weirdly named, such as dates_of_existence
                            try:
                                subdictionary = self.get_subschema(key[:-1], record_dict)
                                for k in subdictionary[0].keys():
                                    #maybe also some wildcard searching?
                                    if k in schema.keys():
                                        print(k)
                                        #trying to get the items 
                                        #also need to do something about 'location' in the external documents...i.e. if it finds
                                        #a string instead of an object
                                        #this isn't a perfect use of location - there are two kinds; the location in the top container
                                        #schema is a ref, but the location in the external document is some file path or whatever;
                                        #want to eventually check to find the type and then go from there...
                                        pprint.pprint(subdictionary[1])
                                        #notworking
                                        if k in subdictionary[1].keys():
                                            if 'subtype' in subdictionary[1][0][k].keys():
                                                subdictionary[0][k] = {'ref': None} 
                                        #sublist = ['location', 'repository', 'digital_object']
                                        #if k in sublist:
                                        #    subdictionary[0][k] = [{'ref': None}]
                                        else:
                                            subsubdict = self.get_subschema(k, subdictionary[0])                                        
                                    #what about recursion here?? Found some roundabout way to do it in the old version
                            except:
                                #because names are stupid...
                                if 'name' in key:
                                    print(key)
                                #because things aren't named consistently because why tf would they be?
                                elif 'date' in key:
                                    self.get_subschema('date', record_dict)
                    #need to add something for notes (and names??) here...does not return anything right now.
                elif value['type'] in some_types:
                    record_dict[key] = None
                #this captures things that have refs as values, but is different than subjects/linked agents, such
                #as repository, series, parent, etc.
                elif value['type'] == 'object':
                    if 'subtype' in value.keys():
                        record_dict[key] = {'ref': None}
                else:
                    print('extra: ' + str(key))
        pprint.pprint(record_dict)
    
    def template_tocsv(self):
        pass