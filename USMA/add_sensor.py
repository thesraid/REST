#!/usr/bin/env python

"""
joriordan@alienvault.com
Script to connect a sensor to an existing controller
Script will login with the specified account and password
Sensor will be marked as configured

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

    parser.add_argument('-s', '--sensor',
                        required=True,
                        action='store',
                        help='Sensor IP or DNS')

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

    parser.add_argument('-n', '--name',
                        required=False,
                        default='USMA-Sensor-Prod',
                        action='store',
                        help='Sensor Name')

    parser.add_argument('-c', '--desc',
                        required=False,
                        default='USMA Sensor Prod',
                        action='store',
                        help='Sensor Description')

    parser.add_argument('-f', '--force',
                        required=False,
                        action='store_true',
                        help='Force the connection')

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

   sensor=args.sensor
   domain=args.domain
   user=args.user
   pwd=args.password
   name=args.name
   desc=args.desc
   force=args.force

   if force:
      print "INFO: Not checking if the sensor is already connected"

   """ Create a session - stores cookies """
   s = requests.Session()

   """ Frequently used json and URLS """
   data_raw = {"email":user, "password":pwd}
   data = json.dumps(data_raw)
   sensor_status = 'http://' + sensor + '/api/1.0/status'
   sensor_connect =  'http://' + sensor + '/api/1.0/connect'
   global users_url 
   users_url = 'https://' + domain + '/api/1.0/users'
   login_url = 'https://' + domain + '/api/1.0/login'
   sensors_url = 'https://' + domain + '/api/1.0/sensors'
   key_url = 'https://' + domain + '/api/1.0/sensors/key'


   """
   Check to see if the sensor is already connected to something
   """
   try:
      response = s.get(sensor_status)
   except:
      print colored ("Error: Cannot access " + sensor_status, "red")
      print "RAW: " + response.text
      exit()
 
   status = jsonSearch(response, 'status')

   if status == 'notConnected':
      print colored ("INFO: " + sensor + " is not connected to a controller", "green")
   else:
      if force:
         print colored ("INFO: Forcing connection", "green")
      else:
         masterNode = jsonSearch(response, 'masterNode')
         print colored ("Error: " + sensor + " is already connected to " + masterNode, "red")
         exit()

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
   # Generate a sensor key 
   """
   print colored ("INFO: Generating a sensor key", "green")
   s, headers = getToken(s)
   try:
      response = s.post(key_url, headers=headers, data=data)
   except:
      print colored ("Error: Cannot access " + key_url, "red")
      print "RAW: " + response.text
      exit()

   key = jsonSearch(response, 'id')

   """
   # Connect the sensor to the controller using the key
   # The is no output from this command when it runs successfully
   """
   print colored ("INFO: Starting connection to controller", "green")
   data_raw = {"key":key, "masterNode":domain, "name":name, "description":desc}
   data = json.dumps(data_raw)
   try:
      response = s.post(sensor_connect, headers=headers, data=data)
   except:
      print colored ("Error: Cannot access " + sensor_connect, "red")
      print "RAW: " + response.text
      exit()

   print response.text

   """
   # View status of the connection
   """
   status = "NotConnected"
   while (status != "connected"):  
      response = s.get(sensor_status)
      if response.status_code == 502:
         print colored ("      Status: Waiting for sensor services to restart", "green")
      else:
         status = jsonSearch(response, 'status')
         print colored ("      Status: " + status, "green")
      time.sleep(30)

   print colored ("      Status: " + status, "green")
  
###########################################################################################

""" Start program """
if __name__ == "__main__":
    main()
