#!/usr/bin/env python

"""
joriordan@alienvault.com
Script will login with the specified account and password
Sensor will be configured

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

    parser.add_argument('-o', '--otx',
                        required=True,
                        action='store',
                        help='OTX Key')

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
   for obj, value in response.json().items():
      if obj == "error":
         print colored ("ERROR: " + (response.json()['error']), 'red')
         print response.text
         exit()
      else:
         key = (response.json()[searchString])

   return key


###########################################################################################
"""
Iterate through a json dictionary and print out every key/value
"""

def myprint(d):
   for k, v in d.items():
      if isinstance(v, dict):
         myprint(v)
      else:
         print("{0} : {1}".format(k, v))

   return

###########################################################################################
"""
Main module
"""
def main():

   args = get_args()

   domain=args.domain
   user=args.user
   pwd=args.password
   otx=args.otx

   """ Create a session - stores cookies """
   s = requests.Session()

   """ Frequently used vars, json and URLS """
   name= "USMA-Sensor"
   desc= "USMA Sensor"
   data_raw = {"email":user, "password":pwd}
   data = json.dumps(data_raw)
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
   search_url = 'https://' + domain + '/api/1.0/search/aql'
   authScan_url = 'https://' + domain + '/api/1.0/apps/joval/groupScan'
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
   response = s.post(login_url, headers=headers, data=data)


   """
   Get Sensor UUID
   """
   print colored ("INFO: Searching for sensor", "green")
   s, headers = getToken(s)
   response = s.get(sensors_url, headers=headers, data=data)
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



   """ ### EXERCISE 1 ### """



   """
   Create an asset group called USMA-Sensor-Network
   This emulates one of the results of searching for assets using the wizard
   We grab the assetGroup ID as well to be used later
   """
   print colored ("INFO: Creating an asset group for 192.168.250.0/25 called USMA-Sensor-Network", "green")
   group_raw = {'name':'USMA-Sensor-Network','description':'Dynamic asset group created from CIDR 192.168.250.0/25','excludeFromScan':'false','static':'false','AssetMemberOfAssetGroup':[],'addRule':{'define':{'a':{'type':'Asset'},'n':{'type':'NetworkInterface','join':'a','relationship':'AssetHasNetworkInterface','fromLeft':'true'}},'where':[{'and':{'in':{'n.ipAddress':'192.168.250.0/25'},'==':{'a.knownAsset':'true'}}}],'return':{'assets':{'value':'a.id'}}},'metadata':{'state':{'facet':'assets','title':'Investigate','chart':'false','page':{'current':1,'total':None},'limit':20,'bindings':{'match_all':[],'filters':{'assetSearch':{'value':[{'field':'n.ipAddress','operator':'in','values':['192.168.250.0/25']}]},'stats':{'value':None},'knownAsset':{'value':'true'},'operatingSystem':{'value':None},'deviceType':{'value':None},'assetOriginType':{'value':None},'AssetMemberOfAssetGroup':{'value':None},'assetService':{'value':None},'assetSoftware':{'value':None},'assetInstance':{'value':None},'assetRegion':{'value':None},'assetOriginUUID':{'value':None}},'sort':{'dateUpdated':'desc'}},'collapse':{'filters':'false'},'filters':['assetSearch','stats','assetOriginUUID','assetOriginType','AssetMemberOfAssetGroup','assetInstance','assetRegion','operatingSystem','deviceType','assetService','assetSoftware'],'columns':['noes_checkbox','asset_bookmark','asset_name','AssetHasCredentials','AssetHasDomainName','AssetHasNetworkInterface','assetOriginUUID','jobs','deviceType','alarmCount','eventCount','vulnerabilityCount','configurationCount','dateUpdated'],'column_names':{}}},'isCidrGroup':'true','groupType':'network'}
   group_data = json.dumps(group_raw)
   s, headers = getToken(s)
   response = s.post(assetGroups_url, headers=headers, data=group_data)
   assetGroupID = jsonSearch(response, 'result')

   """
   Perform an Asset Discovery Scan of the above asset group
   """
   """print colored ("INFO: Running an asset discovery scan on USMA-Sensor-Network", "green")
   scan_raw = {'uuid':assetGroupID,'scan_profile':'fast'}
   scan_data = json.dumps(scan_raw)
   s, headers = getToken(s)
   response = s.post(assetDiscovery_url + sensor_uuid, headers=headers, data=scan_data)
   scanJobID = jsonSearch(response, 'jobs')

   """
   """
   Print the progress of the Scan of the above asset group
   """
   """
   status = "In Progress"
   while status != 'Successful':
      time.sleep(20)
      s, headers = getToken(s)
      response = s.get(status_url + '/' + scanJobID[0], headers=headers, data=data)
      status = jsonSearch(response, 'status')
      log = jsonSearch(response, 'log')
      print colored ("      Status: " + status + " " + log, "green")
   """
   """
   Create a scheduled task to run a daily scan
   """
   print colored ("INFO: Creating a scheduled task to scan USMA-Sensor-Network daily", "green")
   scheduler_raw = {'sensor':sensor_uuid,'app':'nmap','action':'assetDiscovery','name':'Daily Scan for USMA-Sensor-network','description':None,'type':'groupScan','schedule':'0 0 23 1/1 * ? *','params':{'uuid':assetGroupID,'scan_profile':'fast'}}
   scheduler_data = json.dumps(scheduler_raw)
   s, headers = getToken(s)
   response = s.post(scheduler_url, headers=headers, data=scheduler_data)
   

   """
   Add the OTX key
   """
   print colored ("INFO: Adding the OTX key to the sensor", "green")
   otx_raw = {'appName':'AlienvaultOTX','properties':{'otxPassword':otx}}
   otx_data = json.dumps(otx_raw)
   s, headers = getToken(s)
   response = s.put(otx_url, headers=headers, data=otx_data)

   """
   Mark the sensor as configured
   """
   print colored ("INFO: Marking the asset as configured", "green")
   setup_raw = {'setupStatus': 'Complete'}
   setup_data = json.dumps(setup_raw)
   s, headers = getToken(s)
   response = s.patch(sensor_uuid_url, headers=headers, data=setup_data)




   """ ### EXERCISE 2 ### """



   """
   Query the Asset Group for the IDS of the 3 machines we want to add to the PCI group 
   """
   print colored ("INFO: Searching for PCI assets by IP address", "green")
   s, headers = getToken(s)
   search_raw = {'define':{'a':{'type':'Asset'},'g':{'type':'AssetGroup','join':'a','relationship':'AssetMemberOfAssetGroup','fromLeft':'true'},'s':{'type':'Service','join':'a','relationship':'AssetHasService','fromLeft':'true'},'c':{'type':'CPEItem','join':'a','relationship':'AssetHasCPEItem','fromLeft':'true'}},'where':[{'and':{'==':{'a.knownAsset':'true'}}}],'return':{'assets':{'object':'a','page':{'start':0,'count':20},'inject':{'AssetHasNetworkInterface':{'relationship':'AssetHasNetworkInterface','fromLeft':'true','inject':{'NetworkInterfaceHasHostname':{'relationship':'NetworkInterfaceHasHostname','fromLeft':'true'}}},'AssetHasCredentials':{'relationship':'AssetHasCredentials','fromLeft':'true'}},'sort':['a.dateUpdated desc']},'agg_operatingSystem':{'aggregation':'a.operatingSystem','sort':['count desc','value asc']},'agg_deviceType':{'aggregation':'a.deviceType','sort':['count desc','value asc']},'agg_assetOriginType':{'aggregation':'a.assetOriginType','sort':['count desc','value asc']},'agg_AssetMemberOfAssetGroup':{'aggregation':'g.id','sort':['count desc','value asc']},'agg_assetService':{'aggregation':'s.data','sort':['count desc','value asc']},'agg_assetSoftware':{'aggregation':'c.name','sort':['count desc','value asc']},'agg_assetOriginUUID':{'aggregation':'a.assetOriginUUID','sort':['count desc','value asc']}}}
   search_data = json.dumps(search_raw)
   response = s.post(search_url, headers=headers, data=search_data)
   
   """
   The for statement delves into the json to find the key "results" which is a child of the key "assets"
   The "results" key is stored in the variable called obj
   The value of "results" key is actually a dict of key/value pairs. So obj is now a dict. Think of a dict as a second embedded json file
   The if statement looks into the dict for the value "name" which has the key of our target asset. When it finds that object it prints the value of the key id. 
   {
   "assets": {
		"total": 6,
		"first": 0,
		"last": 5, 
		"results": [{  < START OF EMBEDDED JSON (dict) FILE - JSON is treated a dict in Python
				"vulnerabilityCount": "0",
				"hipaa": "false",
				"operatingSystemSource": "Asset Scan",
				"name": "192.168.250.13",
				"assetOriginType": "nmap",
				"operatingSystem": "Linux 3.8 - 4.9",
				"id": "7494fb04-be73-4821-8c23-10cc7135af1a",
				"dateCreated": "1508425234639",
  				.
				.
				.
				.
   target = "192.168.250.13"
   for obj in response.json()['assets']['results']:
      if obj['name'] == target:
         print obj["id"]
   
   Same code as above but in a loop. One for each asset name we want to find
   """
   for asset in pci_assets:
      for obj in response.json()['assets']['results']:
         if obj['name'] == asset:
            print colored ("      INFO: Found " + asset, "green")
            pci_asset_ids.append(obj["id"])
            pci_asset_objs.append(obj)

   """
   Add each pci asset to the PCI group
   """
   print colored ("INFO: Adding PCI assets to the PCI group", "green")
   s, headers = getToken(s)
   pci_raw = {'assets':pci_asset_ids,'tags':[{'name':'pci','type':'Boolean','value':'true'}]}
   pci_data = json.dumps(pci_raw)
   response = s.patch(assets_url, headers=headers, data=pci_data)

   """
   Create a static group with the same assets as members
   """
   print colored ("INFO: Adding internal assets to a new static group", "green")
   s, headers = getToken(s)
   group_raw = {'name':'All Internal Assets','description':'All Internal Servers for Vulnerability Scan','nmapExcludeFromScan':'false','groupType':'network','static':'true','addRule':{},'metadata':{},'members':3, 'AssetMemberOfAssetGroup':pci_asset_objs,'isCidrGroup':'false'}
   group_data = json.dumps(group_raw)
   response = s.post(assetGroups_url, headers=headers, data=group_data)
   group_id = jsonSearch(response, 'result')  



   """ ### EXERCISE 3 ### """




   """
   Create Linux SSH Credentials
   """
   print colored ("INFO: Creating Linux SSH credentials", "green")
   s, headers = getToken(s)
   cred_raw = {'id':None,'type':'SSH','name':'Linux SSH','description':'These are login credentials for the Linux VM','user':'root','password':'Password1!','port':22,'key':'','passphrase':None,'escalationType':'SUDO','escalationUsername':None,'escalationPassword':'','domain':None,'authMethod':'password'}
   cred_data = json.dumps(cred_raw)
   response = s.post(credentials_url, headers=headers, data=cred_data)
   lin_cred_id = jsonSearch(response, 'id')
   
   """
   Create Windows RM Credentials
   """
   print colored ("INFO: Creating Windows RM credentials", "green")
   s, headers = getToken(s)
   cred_raw = {"id":None,"type":"WINDOWS","name":"Win2K12 Prod","description":"These are login credentials for the Win2K12 production assets","user":"Administrator","password":"Password1!","port":5985,"key":"","passphrase":None,"escalationType":None,"escalationUsername":None,"escalationPassword":"","domain":None,"authMethod":None}
   cred_data = json.dumps(cred_raw)
   response = s.post(credentials_url, headers=headers, data=cred_data)
   win_cred_id = jsonSearch(response, 'id')

   """
   Find the two windows assets IDs
   """
   print colored ("INFO: Finding Windows assets", "green")
   s, headers = getToken(s)
   search_raw = {'define':{'a':{'type':'Asset'},'g':{'type':'AssetGroup','join':'a','relationship':'AssetMemberOfAssetGroup','fromLeft':'true'},'s':{'type':'Service','join':'a','relationship':'AssetHasService','fromLeft':'true'},'c':{'type':'CPEItem','join':'a','relationship':'AssetHasCPEItem','fromLeft':'true'}},'where':[{'and':{'==':{'a.knownAsset':'true'}}}],'return':{'assets':{'object':'a','page':{'start':0,'count':20},'inject':{'AssetHasNetworkInterface':{'relationship':'AssetHasNetworkInterface','fromLeft':'true','inject':{'NetworkInterfaceHasHostname':{'relationship':'NetworkInterfaceHasHostname','fromLeft':'true'}}},'AssetHasCredentials':{'relationship':'AssetHasCredentials','fromLeft':'true'}},'sort':['a.dateUpdated desc']},'agg_operatingSystem':{'aggregation':'a.operatingSystem','sort':['count desc','value asc']},'agg_deviceType':{'aggregation':'a.deviceType','sort':['count desc','value asc']},'agg_assetOriginType':{'aggregation':'a.assetOriginType','sort':['count desc','value asc']},'agg_AssetMemberOfAssetGroup':{'aggregation':'g.id','sort':['count desc','value asc']},'agg_assetService':{'aggregation':'s.data','sort':['count desc','value asc']},'agg_assetSoftware':{'aggregation':'c.name','sort':['count desc','value asc']},'agg_assetOriginUUID':{'aggregation':'a.assetOriginUUID','sort':['count desc','value asc']}}}
   search_data = json.dumps(search_raw)
   response = s.post(search_url, headers=headers, data=search_data)

   for asset in win_assets:
      for obj in response.json()['assets']['results']:
         if obj['name'] == asset:
            print colored ("      INFO: Found " + asset, "green")
            win_asset_ids.append(obj["id"])

   """
   Assign the two windows systems the newly created credentials
   """
   print colored ("INFO: Assigning credentials to Windows assets", "green")
   s, headers = getToken(s)
   win_raw = win_asset_ids
   win_data = json.dumps(win_raw)
   response = s.post(credentials_url + '/' + win_cred_id + '/assets', headers=headers, data=win_data)

   """
   Find the two linux asset IDs
   """
   print colored ("INFO: Finding the Linux asset", "green")
   s, headers = getToken(s)
   search_raw = {'define':{'a':{'type':'Asset'},'g':{'type':'AssetGroup','join':'a','relationship':'AssetMemberOfAssetGroup','fromLeft':'true'},'s':{'type':'Service','join':'a','relationship':'AssetHasService','fromLeft':'true'},'c':{'type':'CPEItem','join':'a','relationship':'AssetHasCPEItem','fromLeft':'true'}},'where':[{'and':{'==':{'a.knownAsset':'true'}}}],'return':{'assets':{'object':'a','page':{'start':0,'count':20},'inject':{'AssetHasNetworkInterface':{'relationship':'AssetHasNetworkInterface','fromLeft':'true','inject':{'NetworkInterfaceHasHostname':{'relationship':'NetworkInterfaceHasHostname','fromLeft':'true'}}},'AssetHasCredentials':{'relationship':'AssetHasCredentials','fromLeft':'true'}},'sort':['a.dateUpdated desc']},'agg_operatingSystem':{'aggregation':'a.operatingSystem','sort':['count desc','value asc']},'agg_deviceType':{'aggregation':'a.deviceType','sort':['count desc','value asc']},'agg_assetOriginType':{'aggregation':'a.assetOriginType','sort':['count desc','value asc']},'agg_AssetMemberOfAssetGroup':{'aggregation':'g.id','sort':['count desc','value asc']},'agg_assetService':{'aggregation':'s.data','sort':['count desc','value asc']},'agg_assetSoftware':{'aggregation':'c.name','sort':['count desc','value asc']},'agg_assetOriginUUID':{'aggregation':'a.assetOriginUUID','sort':['count desc','value asc']}}}
   search_data = json.dumps(search_raw)
   response = s.post(search_url, headers=headers, data=search_data)

   for asset in lin_assets:
      for obj in response.json()['assets']['results']:
         if obj['name'] == asset:
            print colored ("      INFO: Found " + asset, "green")
            lin_asset_ids.append(obj["id"])

   """
   Assign the linux system the newly created credentials
   """
   print colored ("INFO: Assigning credentials to the Linux asset", "green")
   s, headers = getToken(s)
   lin_raw = lin_asset_ids
   lin_data = json.dumps(lin_raw)
   response = s.post(credentials_url + '/' + lin_cred_id + '/assets', headers=headers, data=lin_data)


   """
   Perform a vulnerability scan against the internal assets static group
   """
   print colored ("INFO: Starting Authenticated Scan for the Internal Assets Group", "green")
   s, headers = getToken(s)
   authScan_raw = {'uuid':group_id}
   authScan_data = json.dumps(authScan_raw)
   response = s.post(authScan_url, headers=headers, data=authScan_data)


   print colored ("INFO: Script completed", "green")


###########################################################################################

""" Start program """
if __name__ == "__main__":
    main()
