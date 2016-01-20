#!/usr/bin/env python3
import mf2py
import re
import requests
import logging
from concurrent.futures import ThreadPoolExecutor
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin 

def all_hcards(items):
    hcards = []
    for item in items:
        if isinstance(item, dict):
            if 'h-card' in item['type']:
                hcards.append(item)
            hcards += all_hcards(item.get('children', []))
            hcards += all_hcards(item.get('properties', {}).get('attendee', []))
    return hcards
        

def find_screen_name(url):
    try:
        print('fetching', url)
        r = requests.get(url, timeout=10)
        p = mf2py.parse(url=url)
        for me in p.get('rels', {}).get('me', []):
            m = re.match(r'https?://(?:www.)?twitter.com/@?([\w]+)/?', me)
            if m:
                return m.group(1)
    except:
        logging.error('problem fetching %s', url)
    

all_urls = []

print('fetching irc-people')
p = mf2py.parse(url='https://indiewebcamp.com/irc-people')
for hcard in all_hcards(p.get('items', [])):
    urls = hcard.get('properties', {}).get('url', [])
    if urls:
        all_urls.append(urls[0])

print('fetching guest lists')
r = requests.get('https://indiewebcamp.com/Category:Guest_List')
soup = BeautifulSoup(r.text)
guest_lists = []
for a in soup.find_all('a'):
    if 'Guest_List' in a.get('href', ''):
        guest_lists.append(urljoin('https://indiewebcamp.com/', a.get('href')))

for guest_list in sorted(set(guest_lists)):
    print('fetching', guest_list)
    p = mf2py.parse(url=guest_list)
    for hcard in all_hcards(p.get('items', [])):
        urls = hcard.get('properties', {}).get('url', [])
        if urls:
            all_urls.append(urls[0])

with open('domains.json', 'w') as f:
    json.dump(sorted(set(filter(None, all_urls))), f, indent=True)

with ThreadPoolExecutor(max_workers=25) as executor:
    screen_names = executor.map(find_screen_name, sorted(set(filter(None, all_urls))))

with open('names.json', 'w') as f:
    json.dump(list(set(filter(None, screen_names))), f, indent=True)
