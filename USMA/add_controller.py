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
import datetime
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
                        required=False,
                        default='Password1!',
                        action='store',
                        help='Desired user password')

    parser.add_argument('-k', '--key',
                        nargs='+',
                        required=True,
                        action='store',
                        help='Controller Keys seperated by spaces')

    parser.add_argument('-u', '--user',
                        required=False,
                        action='store',
                        help='Additional users name in email format')

    parser.add_argument('-o', '--outputfile',
                        required=False,
                        default="results.txt",
                        action='store',
                        help='Name of output file where results are written')


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
      print colored ("ERROR: " + (response['error']), "red")
      print "RAW:", response
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
   name=args.user
   outputfile=args.outputfile

   # Write the results to a file in the current directory
   print colored ("INFO: Writing to " + outputfile, "green")
   results_file = open(outputfile, 'a+')
   results_file.write('=======================================================================\n')
   today = str(datetime.date.today())
   results_file.write(today)
   results_file.write('		\n')
   results_file.close()

   for key in key_list:

      results_file = open(outputfile,'a+')
      
      print " "
      print colored ("INFO: Key - " + key, "green")
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

      # Check to see if it's already activated
      try:
         response = s.post(lic_url, headers=lic_head, data=key_json, verify=False)
         output = jsonSearch(response.json(), 'message')
      except:
         print "      WARNING: Timed out connecting to update.alienvault.cloud"
         # time.sleep(5)

      #try:
      #   response
      #except NameError:
      #   print "."
      #else:
      #   output = jsonSearch(response.json(), 'message')
      

      if output == "node activated":
         print colored("WARN: Node is already activated", "yellow")
         connection = jsonSearch(response.json(), 'connection')
         controller = "https://" + jsonSearch(connection, 'masterNode')
         print colored("WARN: " +  controller, "yellow")
         continue

  
      tries = 0 
      while (output != "node activated") and (tries < 10):
         try:
            response = s.post(lic_url, headers=lic_head, data=key_json, verify=False)
         except:
            print "      WARNING: Timed out connecting to update.alienvault.cloud"
            time.sleep(5)

         try:
            response
         except NameError:
            print "."
         else:
            output = jsonSearch(response.json(), 'message')

         print colored (str(tries) + "      WAIT: " + output, "blue")
         if output == "Invalid Authentication Code":
            print colored("ERROR: The above authentication code is not valid. Exiting...", "red")
            exit()
         if output != "node activated":
            time.sleep(120)

         tries += 1

      if tries == 10:
         print colored("********************************", "yellow")
         print colored("ERROR: Unable to reconnect to controller. Controller may be up. Manual password reset from controller webpage required", "yellow")
         print colored("********************************", "yellow")
         break
   
      connection = jsonSearch(response.json(), 'connection')
      inital_pass = jsonSearch(connection, 'initialPassword') 
      inital_user = jsonSearch(connection, 'initialUser') 
      controller = "https://" + jsonSearch(connection, 'masterNode') 
   
   
      print colored ("INFO: Initial Password - " + inital_pass, "green")
      print colored ("INFO: Initial User     - " + inital_user, "green")
      print colored ("INFO: Controller      - " + controller, "green")

      """ Figure out the API Version and set the URLS below accordingly """
      api_url = controller + '/api/version'
      response = s.get(api_url)
      api = response.json()['apiVersion']
      #print "Login RAW: " + response.text
   
      login_url = controller + '/api/' + api + '/login'
      user_url = controller + '/api/' + api + '/user'
      users_url = controller + '/api/' + api + '/users'
      userme_url = controller + '/api/' + api + '/users/me'
   
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
         print colored ("INFO: Logged in", "green")
      except:
         print response.text
         exit()


      """ Start of change password block """   
      if api == "1.0":
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
      
      elif api == "2.0":

         """ Get the user ID """
         data_raw = {'email':inital_user, 'password':inital_pass}
         data = json.dumps(data_raw)
         print colored ("INFO: Getting User Info", "green")
         try:
            response = s.get(userme_url, headers=headers, data=data)
         except:
            print response.text
            exit()

         userId = jsonSearch(response.json(),'id')
         #print "ID: " + userId

         password_url = controller + '/api/' + api + '/users/' + userId + '/password'
         """ Change password """
         s, headers = getToken(s)
         data_raw = {'currentPassword':inital_pass, 'password':pwd}
         data = json.dumps(data_raw)
         print colored ("INFO: Changing password", "green")
         try:
            response = s.put(password_url, headers=headers, data=data)
         except:
            print response.text
            exit()

         try:
            result = jsonSearch(response.json(),'error')
            print colored ("ERROR: " + result, "red")
            exit()
         except:
            if '"' + userId + '"' == response.text:
               print colored ("INFO: Password changed to " + pwd, "green")
            else:
               print colored ("ERROR: " + response.text, "red")
               exit()

         #result = response.text
         #print colored ("INFO: Result - " + result, "green")

      """   End of password change block """

      """
      # Create the list of users
      """

      if name is not None:
         print colored ("INFO: Creating the second user", "green")
         s, headers = getToken(s)
         data_user = {"changePassword":"false","fullName":name,"email":name,"enabled":"true","roles":[{"name":"manager"}],'updatePassword':'true', 'password':pwd}
         data = json.dumps(data_user)
         try:
            response = s.post(users_url, headers=headers, data=data)
         except:
            print colored ("Error: Cannot access " + users_url, "red")
            print "RAW: " + response.text
            exit()
     
         result = jsonSearch(response.json(),'fullName')
         print colored ("INFO: " + result + " created", "green")


      if name is not None:
         results_file.write('KEY: ' + key + '       URL: ' + controller + '       USER: ' + inital_user + '       OLDPASS: ' + inital_pass + '       PASS: ' + pwd + '       XTRAUSR: ' + name + '\n')
         results_file.close()
      else:
         results_file.write('KEY: ' + key + '       URL: ' + controller + '       USER: ' + inital_user + '       OLDPASS: ' + inital_pass + '       PASS: ' + pwd + '\n')
         results_file.close()


      controllers_file = open('/var/log/controllers.log', 'a+')
      controllers_file.write(controller + '\n')
      controllers_file.close()
 
  
###########################################################################################

""" Start program """
if __name__ == "__main__":
    main()
