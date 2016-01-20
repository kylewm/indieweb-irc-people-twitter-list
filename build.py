#!/usr/bin/env python3

import requests
from requests_oauthlib import OAuth1
import json

import keys

LIST_ID = '215009864'

oauth = OAuth1(
    client_key=keys.APP_KEY, client_secret=keys.APP_SECRET,
    resource_owner_key=keys.USER_KEY,
    resource_owner_secret=keys.USER_SECRET)

with open('names.json', 'r') as f:
    names = json.load(f)

names = sorted(set(names))
    
for ii in range(0, len(names), 100):
    section = names[ii:ii+100]
    print('adding', section[0], 'through', section[-1])
    r = requests.post('https://api.twitter.com/1.1/lists/members/create_all.json', params={
        'slug': 'IndieWebCamp',
        'owner_screen_name': 'kylewmahan',
        'screen_name': ','.join(section),
    }, auth=oauth)
    print('result', r)
        
