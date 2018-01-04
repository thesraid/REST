#!/usr/bin/env python

"""
joriordan@alienvault.com
Script will login with the specified account and password
Apps will be run

"""

import requests
import json
import urllib3
import argparse
import time
from termcolor import colored
from argparse import RawTextHelpFormatter


# Disable SSL warnings
urllib3.disable_warnings()

###########################################################################################
"""
Get command line args from the user.
"""
def get_args():
    parser = argparse.ArgumentParser(
        description='Login Details and Controller domain',
        formatter_class=RawTextHelpFormatter)

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

    parser.add_argument('-a', '--actions',
                        nargs='+',
                        required=True,
                        action='store',
                        help='App Actions to run.\nValid choices are \n\tAWSEvents\n\tSpyCloudEvents\n\tOktaEvents\n\tSuricataEvents\n\tPaloAltoEvents\n\tAssets\n\tGSuiteEvents\n\tCiscoUmbrellaEvents\n\tOffice365Events\n\tVulnerabilities\n\tAzureEvents\n\tSyslogEvents\n\tConfigurationIssues')

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

   global domain
   domain=args.domain
   user=args.user
   pwd=args.password
   app_actions=args.actions

   """ Create a session - stores cookies """
   s = requests.Session()

   """ Frequently used vars, json and URLS """
   name= "USMA-Sensor"
   desc= "USMA Sensor"
   global users_url 
   users_url = 'https://' + domain + '/api/1.0/users'
   login_url = 'https://' + domain + '/api/1.0/login'
   sensors_url = 'https://' + domain + '/api/1.0/sensors'
   key_url = 'https://' + domain + '/api/1.0/sensors/key'
   sensor_uuid_url = 'To be added later'
   otx_url = 'https://' + domain + '/api/1.0/threatIntelligence/AlienvaultOTX'
   assets_url = 'https://' + domain + '/api/1.0/assets'
   assetGroups_url = 'https://' + domain + '/api/1.0/assetGroups'
   assetDiscovery_url = 'https://' + domain + '/api/1.0/apps/nmap/assetDiscovery?sensorId='
   scheduler_url = 'https://' + domain + '/api/1.0/scheduler'
   status_url = 'https://' + domain + '/api/1.0/status'
   authScan_url = 'https://' + domain + '/api/1.0/apps/joval/groupScan'
   search_url = 'https://' + domain + '/api/1.0/search/aql'
   credentials_url = 'https://' + domain + '/api/1.0/credentials'
   pci_assets = ['192.168.250.13', '192.168.250.14', '192.168.250.17']
   pci_asset_ids = []
   pci_asset_objs = []
   win_assets = ['192.168.250.14', '192.168.250.17']
   win_asset_ids = []
   lin_assets = ['192.168.250.13']
   lin_asset_ids = []

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
   Get Sensor UUID
   """
   print colored ("INFO: Searching for sensor", "green")
   s, headers = getToken(s)
   try:
      response = s.get(sensors_url, headers=headers, data=data)
   except:
      print colored ("Error: Cannot access " + sensors_url, "red")
      print "RAW: " + response.text
      exit()

   """ 
   Receive a list of details about sensors
   Iterate through the list of objects to find one with the name of our sensor
   Then pull out it's uuid
   """
   sensor_uuid = False
   for obj in response.json():
      if obj['name'] == name:
         sensor_uuid = obj['uuid']
   
   if sensor_uuid: 
      print colored ("INFO: Found sensor", "green")
      sensor_uuid_url = 'https://' + domain + '/api/1.0/sensors/' + sensor_uuid
   else:
      print colored ("Error: Unable to find a sensor on " + domain, "red")
      exit()
   
   """
   Run demo app action
   """
   for action in app_actions:
      print colored ("INFO: Running Demo App Action - " + action, "green")
      app_raw = {"scenario":"All","scheduledJobId":""}
      app_data = json.dumps(app_raw)
      app_url = 'https://' + domain + '/api/1.0/apps/demo-app/demoAppActionCreate' + action + '?sensorId=' + sensor_uuid
      s, headers = getToken(s)
      try:
         response = s.post(app_url, headers=headers, data=app_data)
      except:
         print colored ("Error: Cannot access " + app_url, "red")
         print "RAW: " + response.text
         exit()



   print colored ("INFO: Script completed", "green")


###########################################################################################

""" Start program """
if __name__ == "__main__":
    main()
