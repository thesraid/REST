#!/usr/bin/env python


"""
joriordan@alienvault.com
Script to crreate a controller and reset the password

"""

import requests
import json
import urllib3
import argparse
import time
import os
from termcolor import colored


# Disable SSL warnings
urllib3.disable_warnings()

###########################################################################################
"""
Get command line args from the user.
"""
def get_args():
    parser = argparse.ArgumentParser(
        description='Login Details and Controller password')

    parser.add_argument('-p', '--password',
                        required=True,
                        action='store',
                        help='Desired user password')

    parser.add_argument('-k', '--key',
                        nargs='+',
                        required=True,
                        action='store',
                        help='Controller Keys seperated by spaces')

    args = parser.parse_args()

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
      for obj, value in response.items():
         if obj == "error":
            print colored ("ERROR: " + (response['error']), "red")
            print "RAW:", response
            exit()
         else:
            key = (response[searchString])
   except KeyError:
      key = jsonSearch(response, 'error')
      exit()

   return key


###########################################################################################
"""
Main module
"""
def main():

   args = get_args()

   pwd=args.password
   key_list=args.key

   # Write the results to a file in the current directory
   print colored ("INFO: Writing to results.txt", "green")
   results_file = open('results.txt','a+')

   for key in key_list:
      """ Create a session - stores cookies """
      s = requests.Session()
   
      """ Frequently used json and URLS """
      key_raw = {"key":key}
      key_json = json.dumps(key_raw)
      lic_head = {'Content-Type': 'application/json', 'cache-control': 'no-cache'}
      lic_url = 'https://update.alienvault.cloud/licensing/activate'
      global users_url
      """ 
      Set further down as I don't know the controller URL yet 
      login_url = ???
      users_url = ???
      """
   
      output = "activation in progress"
   
      while output != "node activated":
         response = s.post(lic_url, headers=lic_head, data=key_json, verify=False)
         output = jsonSearch(response.json(), 'message')
         print colored ("      WAIT: " + output, "blue")
         if output == "Invalid Authentication Code":
            exit()
         if output != "node activated":
            time.sleep(120)
   
      connection = jsonSearch(response.json(), 'connection')
      inital_pass = jsonSearch(connection, 'initialPassword') 
      inital_user = jsonSearch(connection, 'initialUser') 
      controller = "https://" + jsonSearch(connection, 'masterNode') 
   
   
      print colored ("INFO: Inital Password - " + inital_pass, "green")
      print colored ("INFO: Inital User     - " + inital_user, "green")
      print colored ("INFO: Controller      - " + controller, "green")
   
      login_url = controller + '/api/1.0/login'
      user_url = controller + '/api/1.0/user'
      users_url = controller + '/api/1.0/users'
      userme_url = controller + '/api/1.0/users/me'
   
      """
      Find the XSRF-TOKEN in the cookie
      This has to be passed in the header of every future request
      """
      s, headers = getToken(s)
   
      """ Login using the username, cookie and XSRF token """
      data_raw = {'email':inital_user, 'password':inital_pass}
      data = json.dumps(data_raw)
      print colored ("INFO: Logging in", "green")
      try:
         response = s.post(login_url, headers=headers, data=data)
      except:
         print response.text
         exit()
   
      """ Get the user ID """
      data_raw = {'email':inital_user, 'password':inital_pass}
      data = json.dumps(data_raw)
      print colored ("INFO: Getting User Info", "green")
      try:
         response = s.get(user_url, headers=headers, data=data)
      except:
         print response.text
         exit()

      loginAttempts = jsonSearch(response.json(),'loginAttempts')
      blockedTimestamp = jsonSearch(response.json(),'blockedTimestamp')
      emailOptin = jsonSearch(response.json(),'emailOptin')
      changePassword = jsonSearch(response.json(),'changePassword')
      intercomHash = jsonSearch(response.json(),'intercomHash')
      licenseKey = jsonSearch(response.json(),'licenseKey')
      wizard = jsonSearch(response.json(),'wizard')
      id_ = jsonSearch(response.json(),'id')
      email = jsonSearch(response.json(),'email')
      multiFactorAuthentication = jsonSearch(response.json(),'multiFactorAuthentication')
      timestamp = jsonSearch(response.json(),'timestamp')
     
      """
      print "DUMP:" 
      print loginAttempts
      print blockedTimestamp
      print emailOptin
      print changePassword
      print intercomHash
      print licenseKey
      print wizard
      print id_
      print email
      print multiFactorAuthentication
      print timestamp
      print inital_pass
      print 'True'
      print pwd
      print userme_url
      """
   
      """ Change password """
      s, headers = getToken(s)
      data_raw = {'loginAttempts':loginAttempts, 'blockedTimestamp':blockedTimestamp, 'emailOptin':emailOptin, 'changePassword': changePassword, 'intercomHash':intercomHash, 'licenseKey':licenseKey, 'id':id_, 'email':email, 'multiFactorAuthentication':multiFactorAuthentication, 'timestamp':timestamp, 'currentUserPassword':inital_pass, 'updatePassword':'true', 'password':pwd}
      data = json.dumps(data_raw)
      print colored ("INFO: Changing password", "green")
      try:
         response = s.put(userme_url, headers=headers, data=data)
      except:
         print response.text
         exit()

      result = jsonSearch(response.json(),'result')
      print colored ("INFO: Result - " + result, "green")

      results_file.write('KEY: ' + key + '       URL: ' + controller + '       USER: ' + inital_user + '       OLDPASS: ' + inital_pass + '       PASS: ' + pwd + '\n')
      results_file.close()
 
  
###########################################################################################

""" Start program """
if __name__ == "__main__":
    main()
