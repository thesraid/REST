#!/usr/bin/env python

"""
joriordan@alienvault.com
Script to create accounts on a controller and set the password

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

    parser.add_argument('-n', '--names',
                        nargs='+',
                        required=True,
                        default='USMA-Sensor',
                        action='store',
                        help='List of users to create')

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
Searches a json list for a particular key-value pair
Exits if the response contains an error key
"""

def jsonSearch(response, searchString):
   try:
      for obj, value in response.json().items():
         if obj == "error":
            print colored ("ERROR: " + (response.json()['error']), 'red')
            print "Raw Log: " + response.text
            exit()
         else:
            key = (response.json()[searchString])
   except KeyError:
      print colored ("ERROR: " + response.text, "red")
      exit()

   return key


###########################################################################################
"""
Main module
"""
def main():

   args = get_args()

   domain=args.domain
   user=args.user
   pwd=args.password
   names_list=args.names

   """ Create a session - stores cookies """
   s = requests.Session()

   """ Frequently used json and URLS """
   data_raw = {"email":user, "password":pwd}
   data = json.dumps(data_raw)
   global users_url 
   users_url = 'https://' + domain + '/api/1.0/users'
   login_url = 'https://' + domain + '/api/1.0/login'
   sensors_url = 'https://' + domain + '/api/1.0/sensors'
   key_url = 'https://' + domain + '/api/1.0/sensors/key'


   """
   Find the XSRF-TOKEN in the cookie
   This has to be passed in the header of every future request
   """
   s, headers = getToken(s)

   """ Login using the username, cookie and XSRF token """
   print colored ("INFO: Logging into " + domain, "green")
   try:
      response = s.post(login_url, headers=headers, data=data)
   except:
      print colored ("Error: Cannot access " + login_url, "red")
      print "RAW: " + response.text
      exit()

   """ 
   # Create the list of users
   """
   print colored ("INFO: Creating the users", "green")
   for name in names_list:
      s, headers = getToken(s)
      data_user = {"changePassword":"false","fullName":name,"email":name + "@alienvault.com","enabled":"true","roles":[{"name":"manager"}],'updatePassword':'true', 'password':pwd}
      print data_user
      data = json.dumps(data_user)
      try:
         print colored ("INFO: Creating the user " + name, "green")
         response = s.post(users_url, headers=headers, data=data)
      except:
         print colored ("Error: Cannot access " + users_url, "red")
         print "RAW: " + response.text
         exit()

  
###########################################################################################

""" Start program """
if __name__ == "__main__":
    main()
