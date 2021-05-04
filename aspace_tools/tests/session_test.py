#!/usr/bin/python3

import json
import requests


api_url = ''
username = ''
password = ''

def as_session(api_url, username, password):
    session = requests.Session()
    session.headers.update({'Content_Type': 'application/json'})
    response = session.post(api_url + '/users/' + username + '/login',
                 params={"password": password, "expiring": False})
    if response.status_code != 200:
        print('Error! Unable to authenticate.')
    else:
        session_toke = json.loads(response.text)['session']
        session.headers['X-ArchivesSpace-Session'] = session_toke
    return session


sesh = as_session(api_url, username, password)
req = sesh.get(api_url + '/repositories/12').json()
print(req)


req = sesh.get(api_url + '/repositories/5').json()
print(req)


req = sesh.get(api_url + '/repositories/11').json()
print(req)
