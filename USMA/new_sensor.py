#!/usr/bin/env python

"""
joriordan@alienvault.com
Script to connect a sensor to a new controller
Script will login with the specified account and password
Sensor will be marked as configured
"""

import re
import argparse
import getpass
import subprocess
import os
import json
import time
from os.path import expanduser
#########################################################################################################


def get_args():
    """Get command line args from the user.
    """
    parser = argparse.ArgumentParser(
        description='Sensor Key and user details')

    parser.add_argument('-s', '--sensor',
                        required=True,
                        action='store',
                        help='Sensor IP or DNS')

    parser.add_argument('-k', '--key',
                        required=True,
                        action='store',
                        help='Sensor Key')

    #parser.add_argument('-d', '--domain',
                        #required=True,
                        #action='store',
                        #help='Domain to connect to')

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
                        default='USMA-Sensor',
                        action='store',
                        help='Sensor Name')

    parser.add_argument('-c', '--desc',
                        required=False,
			default='USMA Sensor',
                        action='store',
                        help='Sensor Description')

    parser.add_argument('-f', '--force',
                        required=False,
                        action='store_true',
                        help='Force the connection')

    args = parser.parse_args()

    if not args.password:
        args.password = getpass.getpass(
            prompt='Enter password for user %s: ' %
                   (args.user))
    return args

#########################################################################################################
def runCommand(bashCommand):

   # Runs the command and returns the json output and the raw output
   # If there is no json data we retun false for that variable
   # If the bash command fails we print some error data and exit

   try: # Try and run the command, if it doesn't work then except subprocess will catch it and return 1 
      output = subprocess.check_output(bashCommand, shell=True)
      try: # Try and convert the output to a json object. If the output isn't json we get a ValueError so we return false. 
         json_data = json.loads(output)
         if 'error' in json_data: # If something goes wrong the json will have a key called error. Print it's contents and exit
            print "Error: " + json_data['error']
            exit()
         else:
            return json_data, output # Else if it's not an error return the json and raw data
      except ValueError, e: # If the json data isn't valid data
         return False, output # Return false and the raw output
   except subprocess.CalledProcessError as bashError: # If the bash command fails give an error and exit
      print "Error: Error while executing bash command"
      print "Error: " + bashCommand                                                                                          
      print "Error: Code", bashError.returncode, bashError.output
      exit()


#########################################################################################################

def login(domain, user, pwd, home):

   #Get Cookie
   try:
      print "Info: Securely connecting to " + domain + " to get certificates and cookies"
      print " "
      print " "
      bashCommand = 'curl -v -s -k -X GET -H "Content-Type: application/json" "https://' + domain + '/api/1.0/user" -b ' + home + '/.sensor/cookie.txt -c ' + home + '/.sensor/cookie.txt'
      output = subprocess.check_output(bashCommand, shell=True)   
      print " "
      print " "
      print "Info: Successfully got certificates and a cookie" 
   except subprocess.CalledProcessError as bashError:
      print "Error: Error while executing bash command"
      print "Error: " + bashCommand
      print "Error: Code", bashError.returncode, bashError.output
      exit()

   # Extract XSRF-TOKEN from cookie. This will be needed for subsequent API calls
   # https://stackoverflow.com/questions/10477294/how-do-i-search-for-a-pattern-within-a-text-file-using-python-combining-regex
   regex = re.compile("XSRF-TOKEN\s+(\S+)")
   for i, line in enumerate(open(home + '/.sensor/cookie.txt')):
      for match in re.finditer(regex, line):
          token = match.group(1)

   # Login
   try:
      print "Info: Logging into " + domain + " as " + user
      bashCommand = 'curl -s -k -X POST -H \'Content-Type: application/json\' -H "X-XSRF-TOKEN: ' + token + '" -d \'{"email":"' + user + '", "password":"' + pwd + '"}\' "https://' + domain + '/api/1.0/login" -b ' + home + '/.sensor/cookie.txt -c ' + home + '/.sensor/cookie.txt'
      print bashCommand
      print "Info: Successfully logged into " + domain
      output = subprocess.check_output(bashCommand, shell=True)
      # If the bash command fails print and error and exit
   except subprocess.CalledProcessError as bashError:
      print "Error: Error while executing bash command"
      print "Error: " + bashCommand
      print "Error: Code", bashError.returncode, bashError.output
      exit()

   return token

#########################################################################################################
def findJSONKey(bashCommand, search_key, search_string, key):

   # Search Key : Key you have data for i.e. "name"
   # Search String: Data for the key you know i.e. "Prod-Sensor"
   # Key: Key you want to get the data for i.e. "uuid"
   
   json_data, output = runCommand(bashCommand)  

   obj_string = "NOT FOUND"   
 
   if not json_data:
      print "Error: Didn't receive json output"
      exit()
   else:
      for obj in json_data:
         if obj[search_key] == search_string:
            #print "Info:  The " + search_key + " with the value " + search_string + " has a " + key + " with a value of " + obj[key]
            obj_string = obj[key]

   return obj_string

#########################################################################################################

def syspasswd(sensor,pwd):

   temp_key = open('temp_key','w+')
   temp_key.write("-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEAzXitzhYq5x0GgJJBk3EUrExo1kDar6++fPrUJ6tkOVrSCYx/\n80ahwtreyT3iV5SG4BXvvwbEVAtFumLq3XGv1fcBacHSTRY3R4XN7ChTKDx0/XFe\n8dbWocowBW8zz8QhVSXbQCA7GshhXjdpbroHocwfa8WhOYXXd86+5MvnAHXuwqJg\nefIhgUg9Yu9hSJFv2o9/TxFOn/OooJzr2QV2gHM4mFCOP6khAYhw6UlO7vlpvGXj\nTnaJ1T4eKDE9HinMxFXeUUsPWHHX0a1uanWxEqJWAJRhdvCyH/dqlUqxnJn7Dpol\nOx0L5QB1AHDqfhz6wEbC1gp/DtYaN+JulK3rUQIDAQABAoIBAGHX3awNklCL2dTP\n0LpNVvLVT/b22yxeG++X4f8h9o/5V5uEdEl8kPshDoX2Ghpqd++tgoUMy+DZnVKs\nV/srb/gLr3iU+3gJ5DkC1pRmf3LhlzQ5EGVJUNuqVEPCOIHve4/4fveCYaLXWMZs\nzKAVphy9/xhq++NQgNJkeTKqhk4I/2BT3Cd6bunjPRQ6+zalONane4Nr0wQSzpRm\nVWFdFEc2W9UMo1TcDhKp6zqhngRwvc3BuVz0r0olNSBkEu7VTrSc9wZUjl4t4ufb\n2ou6wPalBfzIbtU+ADLg2T6N0wWQyoPurdxowGK1cLomBAA0a/yviCaMunN4qD9s\nJBNnwyECgYEA+vfcPv+w5+aANi6sIwjhAtaVHU6FBchUEA9pqURVPhGDPyC1GnXn\nyLwxsO9bLihmRIHxJgoKAwqb6NZ2GEgcAtJWRgZnJRfr8k1Tfq8b47QfE0xZz7lT\nBALY6+Qg9kTeqEchFQxgA1AWf5PqSDAiP09ulKpQC1cC++xYErQlX8MCgYEA0ZdM\nS6WDQZNIVPkigFGqp7enjBvrMKC2vVLAVmbczHJDOgNy0+pPVN5wsFIGE1ayGgTY\nTGeMhC0ZQa0ivLt5XfpNdgJ6OLdVZDCwzZxVK4dIKSlQuHpgihQvhfsx2zVQOVgI\ngMSzeorkJ9OhwIGfSIYT7KDDCmO8DcHTLE2ii1sCgYBKzr0Q7kh+J4AKJola/BeO\nMAZMsQ4HtjoQe3ekY+EA2lmD5Kz3ETQg6q/pLL/CF3q8avtFunJXi78DfYHAJSZs\nVOQwhVIThXjoRdJgjbPDgPpOV1DiETzEklC0p9CHd+niwSkETCcGdcXvC1knYWmj\n83pjyAyKBMq36zApixck3wKBgGmA/dj+gioaV8jeeG2brooqut6ely+tVw/KfiOA\nOBl6Uzj6z2y5gCG6r4MyZviJJbJPSgp7/ZHzmckjvF7BCIE0JJYI/TlboFKE6Bs4\nXO9CdCK0N3wFrl8TdjC9mAU+uxmCpRUc7zP6gotBzyS2m1XImHL/Ie8y8VEDhqfA\nlNgNAoGBAILVG3WC6zX2YRIQTLlq9I4/URngoxzUz3Vn9oIKeVgHH1OQm9YzE2mA\nk46uPvzYLL/F1hcjmIvQtlqpqjfneN8vIPfmZvVOrq0XQqgbcoZ0R2GQe+ZSSxvs\nOQ4jEY7uUDbmuXU+IHgfNvJKbJQiUtyLE3cmJWLYcscmuP1Ebbe6\n-----END RSA PRIVATE KEY-----")
   temp_key.close()

   os.system('chmod 600 temp_key')

   bashCommand = 'ssh -oStrictHostKeyChecking=no -i temp_key root@' + sensor + ' \'echo "sysadmin:' + pwd + '" | chpasswd\''
   os.system(bashCommand)

   os.remove('temp_key')

#########################################################################################################
def main():

   # Variable to store the password token. 
   # This is a token we get when we deploy the sensor which will allow us to set the inital password
   PWDTOKEN = "EMPTY"
   # This variable will be used to store the domain
   domain = "EMPTY"

   # Get the command line argumants and store them in the args variable
   args = get_args()

   # Assign each argument to a variable
   key=args.key
   sensor=args.sensor
   #domain=args.domain
   user=args.user
   pwd=args.password
   name=args.name
   desc=args.desc
   force=args.force

   if force:
      print "Info: Not checking if the sensor is already connected"

   # Make a directory in the users home to store cookies
   home = expanduser("~")
   if not os.path.exists(home + '/.sensor'):
      os.makedirs(home + '/.sensor')

   # Remove any old cookie as it's no longer needed
   bashCommand = 'touch ' + home + '/.sensor/cookie.txt;rm ' + home + '/.sensor/cookie.txt'
   json_data, output = runCommand(bashCommand)

   # Check if the sensor is already connected to something
   # If it is we will exit
   bashCommand = 'curl -s -k -X GET "http://' + sensor + '/api/1.0/status"' # The command to run
   json_data, output = runCommand(bashCommand) # Run the command and receive the json and raw output. json = false if no json received
   if json_data: # If we received json data...
      if json_data['status'] == 'notConnected': # If the value for the status key is notConnected
         print "Info: " + sensor + " is not connected to a controller"
      else: # If the value for the status key is something other than connected
         if force:
            print "Info: Forcing connection"
         else:
            print "Error: " + sensor + " is already connected to " + json_data['masterNode']
            exit()
         #print "Error: " + sensor + " is already connected to " + json_data['masterNode'] # Print the name of the controller it's connected to
         #exit()
   else: # If we did not recive json data print the output and exit
      print "Error: No valid json output received"
      print "Error: This may mean the Web service on "  + sensor + " has not started yet"
      print output
      exit()
   
   # Connect the sensor to the controller using the key
   print "Info: Starting connection"
   bashCommand = 'curl -s -k -X POST -H "Content-Type: application/json" -d \'{"key":"' + key + '","name":"' + name + '","description":"' + desc + '"}\' "http://' + sensor + '/api/1.0/activate"'
   json_data, output = runCommand(bashCommand)  # Run the command and receive the json and raw output. json = false if no json received
   print output # Just print the output. There is no error checking as I don't know what an error looks like as I didn't have enough licenses to test errors. Later checks will fail better

   # Get the current status of the connection
   bashCommand = 'curl -s -k -X GET -H "Content-Type: application/json" "http://' + sensor + '/api/1.0/status"'
   json_data, output = runCommand(bashCommand)    
   connected = False # Set a boolean that we will mark as true when connected
   # Wait while the connection is in progress
   while (not connected): # While we are not connected
      if not json_data: # If we don't recieve json data that's okay as sometimes we get a bad gateway error back but everything is still ok
         print "Info: Waiting for " + name + " to configure ..."
         time.sleep(15)
         json_data, output = runCommand(bashCommand) # run the status check command again
      elif json_data: # If we do jet json data back let's have a look at some keys
         if 'error' in json_data: # If something goes wrong the json will have a key called error. Print it's contents and exit
            print "Error: " + json_data['error']
            exit()
         elif json_data['status'] == "connectedConfiguring": # If the status is connectedConfiguring grab the password reset token that's included with the json
            print "Info: connected Configuring"
            if json_data['resetToken']: # Make sure the token is present. Sometimes connectedConfiguring won't have it
               #print "Info: Token data found"
               #print json_data['resetToken']
               #print output
               PWDTOKEN = json_data['resetToken'] # Save the token for later
            time.sleep(15)
            json_data, output = runCommand(bashCommand) # Run the check status command again as we still haven't connected
         elif json_data['status'] != "connected": # If the status is anything other than connected print a wait message
            print "Info: Waiting for the controller to start..."
            time.sleep(15)
            json_data, output = runCommand(bashCommand) # Run the check status command again as we still haven't connected
         elif json_data['status'] == "connected": # We have connected
            domain = json_data['masterNode']
            print "Info: Connected to " + domain
            print output
            print "AV-Action-Token: " + PWDTOKEN # Print he token that we found in the connectedConfiguring stage
            connected = True # Mark connected as true to break the while loop



   # Try to login to the controller to set a cookie and get a token
   # The login will fail as we have no password yet but we will get a good cookie
   # The login function sets a cookie and tries to login. 
   # It returns a token that will need to be included in all future API calls
   token = login(domain, user, pwd, home)

   # Reset the password using the AV-Action-Token that we save in the while loop while waiting for the sensor to connect
   # The AV-Action-Token is sent as part of the header
   bashCommand = 'curl -s -k -X POST -H \'Content-Type: application/json\' -H "AV-Action-Token: ' + PWDTOKEN  + '" -H "X-XSRF-TOKEN: ' + token + '" -d \'{"password":"' + pwd + '"}\' "https://' + domain + '/api/1.0/token/passwordReset" -b ' + home + '/.sensor/cookie.txt -c ' + home + '/.sensor/cookie.txt'
   json_data, output = runCommand(bashCommand)
   print "Info: Output from password reset"
   print output

   # Login to the controller and get a token
   token = login(domain, user, pwd, home)

   # Curl command for getting a list of sensors
   bashCommand = 'curl -s -k -X GET -H \'Content-Type: application/json\' -H "X-XSRF-TOKEN: ' + token + '" -d \'{"email":"' + user + '", "password":"' + pwd + '"}\' "https://' + domain + '/api/1.0/sensors" -b ' + home + '/.sensor/cookie.txt -c ' + home + '/.sensor/cookie.txt'
   # Run the above command
   # Find the UUID for the sensor
   sensor_uuid = findJSONKey(bashCommand, 'name', name, 'uuid')

   # Mark sensor as configured in the controller
   bashCommand = 'curl -s -k -X PATCH -H \'Content-Type: application/json\' -H "X-XSRF-TOKEN: ' + token + '" -d \'{"setupStatus": "Complete"}\' "https://' + domain + '/api/1.0/sensors/' + sensor_uuid + '" -b ' + home + '/.sensor/cookie.txt -c ' + home + '/.sensor/cookie.txt'
   json_data, output = runCommand(bashCommand)

   # Confirm system is marked as configured
   # Curl command for getting a list of sensors
   bashCommand = 'curl -s -k -X GET -H \'Content-Type: application/json\' -H "X-XSRF-TOKEN: ' + token + '" -d \'{"email":"' + user + '", "password":"' + pwd + '"}\' "https://' + domain + '/api/1.0/sensors" -b ' + home + '/.sensor/cookie.txt -c ' + home + '/.sensor/cookie.txt'
   # Run the above command
   # Find the setup status for the sensor
   sensor_status = findJSONKey(bashCommand, 'name', name, 'setupStatus')
   print "Info: sensor status is " + sensor_status

   # Write the account details to a file
   print "Opening Lab_Login_Details.txt"
   student_file = open('Lab_Login_Details.txt','w+')

   student_file.write('STUDENT LAB DETAILS\r\n')
   student_file.write('-------------------\r\n')
   student_file.write('\r\n')
   student_file.write('\r\n')
   student_file.write('USM Anywhere URL: ' + domain + '\r\n')
   student_file.write('USM Anywhere Username: ' + user + '\r\n')
   student_file.write('USM Anywhere Password: ' + pwd + '\r\n')
   student_file.write('\r\n')
   student_file.write('\r\n')
   student_file.write('USM Sensor Username: sysadmin\r\n')
   student_file.write('USM Sensor Password: ' + pwd + '\r\n')

   print 'STUDENT LAB DETAILS'
   print '-------------------'
   print ' '
   print ' '
   print 'USM Anywhere URL: ' + domain
   print 'USM Anywhere Username: ' + user
   print 'USM Anywhere Password: ' + pwd
   print ' '
   print ' '
   print 'USM Sensor Username: sysadmin'
   print 'USM Sensor Password: ' + pwd


   student_file.close()

   print 'Copying file to windows'
   bashCommand = 'smbclient //192.168.250.14/Lab_Details "Password!" -c "put Lab_Login_Details.txt" -U Administrator'
   json_data, output = runCommand(bashCommand)

   # Log into the sensor using the precreated key and set the password to Password
   syspasswd(sensor,pwd)


   # Remove the cookie as it's no longer needed
   bashCommand = 'rm ' + home + '/.sensor/cookie.txt'
   json_data, output = runCommand(bashCommand)
   print "Complete: You may now log into " + domain + " as " + user + " with the password " + pwd

#########################################################################################################

# Start program
if __name__ == "__main__":
    main()

#########################################################################################################
