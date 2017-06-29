#!/usr/bin/env python

import requests
import json
s = requests.Session()
data = {'email':'docs-team@alienvault.com','password':'Password'}
login_url = 'https://docs-team-005-20161612.alienvault.cloud/api/1.0/login'
user_url = 'https://docs-team-005-20161612.alienvault.cloud/api/1.0/user'
sensors_url = 'https://docs-team-005-20161612.alienvault.cloud/api/1.0/sensors'
#response = s.post(url, data=data)
response = s.get(user_url)
#print response.status_code
#print response.text
#print s.cookies
for name, value in s.cookies.items():
   #print name, value
   if name == 'XSRF-TOKEN':
      token = value
#print response.json()
#print token 

headers = {'Content-Type': 'application/json','X-XSRF-TOKEN': token}
print headers
response = s.post(login_url, headers=headers, data=json.dumps(data))
print response.text

response = s.get(sensors_url, headers=headers)
print response.text
