#!/usr/bin/python3

import csv
import json
import logging
import sys

import requests
from rich import print

'''

Admin tools

'''

class LoginError(Exception):

  def __init__(self, status_code, url, username, message=f"Login failed!"):
      self.status_code = status_code
      self.url = url
      self.username = username
      self.message = message
      super().__init__(self.message)

  def __str__(self):
      return f"{self.message} URL: {self.url}, Username: {self.username}, Status code: {self.status_code}"

class ArchivesSpaceError(Exception):
  def __init__(self, uri, status_code, aspace_message, message=f"ArchivesSpace Error!"):
      self.uri = uri
      self.status_code = status_code
      self.aspace_message = aspace_message
      self.message = message
      super().__init__(self.message)

  def __str__(self):
      return f"{self.message} URI: {self.uri}, Status code: {self.status_code}, Message: {self.aspace_message.get('error')}"

def get_rowcount(fp):
    with open(fp, encoding='utf8') as input_file:
        return len(list(csv.reader(input_file))) - 1

def progress_bar(it, count=None, prefix="", size=60, out=sys.stdout):
    # modified this a bit: https://stackoverflow.com/a/34482761
    if count is None:
        count = len(it)
    def show(counter):
        advance = int(size*counter/count)
        percent_done = counter/count
        print("{}{}{} {}/{} {:.2%}".format(prefix, u"█"*advance, "."*(size-advance), counter, count, percent_done), 
                end='\r', file=out, flush=True)
    show(0)
    for i, item in enumerate(it):
        yield item
        show(i+1)
    print("\n", flush=True, file=out)

def get_record(api_url, uri, sesh):
    record = sesh.get(f"{api_url}{uri}")
    if record.status_code == 200:
        return json.loads(record.text)
    else:
        raise ArchivesSpaceError(uri, record.status_code, json.loads(record.text))

def post_record(api_url, uri, sesh, record_json, row, writer):
    record = sesh.post(f"{api_url}{uri}", json=record_json)
    # what if the text cannot be converted to json? need to make sure it works
    if record.status_code == 200:
        result = json.loads(record.text)
        if result.get('status') == 'Created':
            row['info'] = result['uri']
        writer.writerow(row)
    else:
        raise ArchivesSpaceError(uri, record.status_code, json.loads(record.text))

def delete_record(uri, sesh, record_json):
    record_json = get_record(uri, sesh)
    delete = sesh.delete(uri, json=record_json)
    if delete.status_code == 200:
        return json.loads(delete.text)
    else:
        raise ArchivesSpaceError(uri, record.status_code, json.loads(delete.text))

def create_backups(dirpath, uri, record_json):
    with open(f"{dirpath}/{uri[1:].replace('/','_')}.json", 'a', encoding='utf8') as outfile:
        json.dump(record_json, outfile, sort_keys=True, indent=4)

def check_config():
    path_to_this_file = os.path.dirname(os.path.realpath(sys.argv[0]))
    config_path = os.path.join(path_to_this_file, 'config.json')
    if os.path.exists(config_path):
        with open(config_path, encoding='utf8') as config_file:
            return json.load(config_file)

def get_data_path(config, data_type):
    if config:
        csv_path = config.get(data_type)
        if csv_path not in (None, ''):
            return csv_path
        else:
            return input(f'Please enter path to {data_type}: ')
    else:
        return input(f'Please enter path to {data_type}: ')

def get_login_inputs():
    url = input('Please enter the ArchivesSpace API URL: ')
    username = input('Please enter your username: ')
    password = input('Please enter your password: ')   
    return url, username, password

def check_credentials(config):
    if config:
        if (config.get('api_url') in (None, '')) or (config.get('username') in (None, '')) or (config.get('password') in (None, '')):
            return get_login_inputs()
        else:
            return config['api_url'], config['username'], config['password']
    else:
        return get_login_inputs()

def start_session(config):
    url, username, password = check_credentials(config)
    session = requests.Session()
    session.headers.update({'Content_Type': 'application/json'})
    auth_request = session.post(f"{url}/users/{username}/login?password={password}")
    if auth_request.status_code == 200:
        print(f'Login successful!: {url}')
        session_token = json.loads(auth_request.text)['session']
        session.headers['X-ArchivesSpace-Session'] = session_token
        return url, session
    else:
        raise LoginError(auth_request.status_code, url, username)

def handle_result(row, record_post):
    if record_post.get('status') == 'Created':
        row['info'] = record_post['uri']
    return row

def handle_error(error, row):
    row['info'] = error
    return row
                    
def get_endpoints():
    pass

def main():
    fp = "/Users/aliciadetelich/Desktop/all_ru_1160_files.csv"
    rowcount = get_rowcount(fp)
    with open(fp, encoding='utf8') as input_file:
        reader = csv.reader(input_file)
        for row in progress_bar(reader, count=rowcount, prefix="Processing file: "):
            time.sleep(0.3)


if __name__ == '__main__':
    main()


