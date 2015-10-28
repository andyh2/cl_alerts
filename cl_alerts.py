"""
Logs into your craigslist account and manages email alerts for 
multiple keywords across multiple regions.

python3 cl_alerts.py add keywords.txt
"""
from urllib.parse import quote_plus
import re
import requests
import sys
from getpass import getpass
from collections import OrderedDict

USAGE = 'python3 cl_alerts.py add|del_all [keywords.txt]'

CA_CITIES = [
            'bakersfield', 
            'chico', 
            'fresno', 
            'goldcountry', 
            'hanford', 
            'humboldt', 
            'imperial', 
            'inlandempire', 
            'losangeles', 
            'mendocino', 
            'merced', 
            'modesto', 
            'monterey', 
            'orangecounty', 
            'palmsprings', 
            'redding', 
            'reno', 
            'sacramento', 
            'sandiego', 
            'slo', 
            'santabarbara', 
            'santamaria', 
            'sfbay', 
            'siskiyou', 
            'stockton', 
            'susanville', 
            'ventura', 
            'visalia', 
            'yubasutter']
LOGIN_URL = 'https://accounts.craigslist.org/login'
LOGIN_HOME_URL = 'https://accounts.craigslist.org/login/home'
SFBAY_URL = 'http://sfbay.craigslist.org/'
SEARCH_URL_FRMT = 'http://{city}.craigslist.org/search/sss?excats=7-13-22-2-25-4-19-1-1-1-1-1-1-3-6-10-1-1-1-2-2-8-1-1-1-1-1-4-1-3-1-3-1-1-1-1-7-1-1-1-1-1-1-1-1-1-1-1-2-1-1-1-1-1-2-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-3-1-1-1-1-1&sort=rel&query={query}'
SHOW_SEARCHES_URL = 'https://accounts.craigslist.org/login/home?show_tab=searches'
EMAIL_ALERT_URL = 'https://accounts.craigslist.org/savesearch/alert'

s = requests.Session()

def login(email, password):
  s.get(SFBAY_URL)
  s.get(LOGIN_URL)

  data = OrderedDict([
    ('step', 'confirmation'),
    ('rt', ''),
    ('rp', ''),
    ('p', 0),
    ('inputEmailHandle', email),
    ('inputPassword', password)
    ])

  r = s.post(LOGIN_URL, data=data,  headers={'Referer': LOGIN_URL})
  if r.url != LOGIN_HOME_URL:
    raise Exception('Invalid login')

def add_alert(query):
  for city in CA_CITIES:
    print('Added alert in {} for "{}"'.format(city, query))
    search_url = SEARCH_URL_FRMT.format(city=city, query=query)
    r = s.get(EMAIL_ALERT_URL, params={'URL': search_url})
    if 'save search confirmation' in r.text:
      csrf_matches = re.search(r'name="_csrf" value="(.*)"', r.text)
      data = {'_csrf': csrf_matches.group(1)}
      r = s.post(r.url, data=data, headers={'Referer': r.url})

def remove_all_alerts():
  r = s.get(SHOW_SEARCHES_URL)
  for match in re.finditer(r'\/savesearch\/delete\?subID=[0-9]+', r.text):
    r = s.get('https://accounts.craigslist.org{}'.format(match.group(0)))

def main():
  command = queries_file = None
  try:
    command = sys.argv[1].lower()
    queries_file = sys.argv[2]
  except IndexError:
    if command != 'del_all': # del_all command does not require second arg 
      print('Usage: ', USAGE)
      return

  email = input('Craigslist account email: ')
  password = getpass('Craigslist account password: ')
  login(email, password)

  f = open(queries_file, 'r')
  if command == 'add':
    for query in f.readlines():
      add_alert(query.strip())
  elif command == 'del_all':
    remove_all_alerts()

if __name__ == '__main__':
  main()