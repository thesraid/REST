#!/usr/bin/env python

"""
joriordan@alienvault.com
Script to log into a controller and delete all views
"""

import requests
import json
import urllib3
import argparse
import time
from termcolor import colored


# Disable SSL warnings
urllib3.disable_warnings()

###########################################################################################
"""
Get command line args from the user.
"""
def get_args():
    parser = argparse.ArgumentParser(
        description='Login Details and Controller domain')

    parser.add_argument('-d', '--domain',
                        required=True,
                        #type=int,
                        #default=443,
                        action='store',
                        help='Domain to connect to')

    parser.add_argument('-u', '--user',
                        required=True,
                        action='store',
                        help='User name to connect with')

    parser.add_argument('-p', '--password',
                        required=False,
                        action='store',
                        help='Password to use when connecting')

    args = parser.parse_args()

    if not args.password:
        args.password = getpass.getpass(
            prompt='Enter password for domain %s and user %s: ' %
                   (args.domain, args.user))
    return args

###########################################################################################
""" 
Find the XSRF-TOKEN in the cookie
This has to be passed in the header of every future request
"""

def getToken(s):
   s.get(users_url)
   for name, value in s.cookies.items():
     if name == 'XSRF-TOKEN':
        token = value
   headers = {'Content-Type': 'application/json','X-XSRF-TOKEN': token}
   return s, headers

###########################################################################################

"""
Main module
"""
def main():

   args = get_args()

   global domain
   domain=args.domain
   user=args.user
   pwd=args.password

   """ Create a session - stores cookies """
   s = requests.Session()

   """ Frequently used vars, json and URLS """
   global users_url
   users_url = 'https://' + domain + '/api/1.0/users'
   login_url = 'https://' + domain + '/api/1.0/login'
   views_url = 'https://' + domain + '/api/1.0/views'

   """
   Find the XSRF-TOKEN in the cookie
   This has to be passed in the header of every future request
   """
   s, headers = getToken(s)

   """ Login using the username, cookie and XSRF token """
   print colored ("INFO: Logging in", "green")
   data_raw = {"email":user, "password":pwd}
   data = json.dumps(data_raw)
   try:
      response = s.post(login_url, headers=headers, data=data)
   except:
      print colored ("Error: Cannot access " + login_url, "red")
      print "RAW: " + response.text
      exit()


   """
   Get list of views on the system
   """
   s, headers = getToken(s)
   try:
      response = s.get(views_url + "/me", headers=headers, data=data)
   except:
      print colored ("Error: Cannot access " + views_url + "/me", "red")
      print "RAW: " + response.text
      exit()

   """
   Iterate through each item in the list and delete it
   """
   for obj in response.json():
      if obj['editable'] == True:
         view_id = obj['id']

         data_raw = {"email":user, "password":pwd}
         data = json.dumps(data_raw)

         try:
            print "Deleting", obj['name']
            response = s.delete(views_url + "/" + view_id, headers=headers, data=data)
         except:
            print colored ("Error: Cannot access " + views_url, "red")
            print "RAW: " + response.text
            exit()

   print colored ("INFO: Script completed", "green")


###########################################################################################

""" Start program """
if __name__ == "__main__":
    main()
