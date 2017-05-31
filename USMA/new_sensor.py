#!/usr/bin/env python

"""
Script to connect a sesnor to a new controller
Script will login with the specified account and password
Sensor will be marked as configured

joriordan@alienvault.com
2017-05-31

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
        description='Sensor Key and Controller domain')

    parser.add_argument('-s', '--sensor',
                        required=True,
                        action='store',
                        help='Sensor IP or DNS')

    parser.add_argument('-k', '--key',
                        required=True,
                        action='store',
                        help='Sensor Key')

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
                        default='USMA-Sensor',
                        action='store',
                        help='Sensor Name')

    parser.add_argument('-c', '--desc',
                        required=False,
			default='USMA Sensor',
                        action='store',
                        help='Sensor Description')


    args = parser.parse_args()

    if not args.password:
        args.password = getpass.getpass(
            prompt='Enter password for domain %s and user %s: ' %
                   (args.domain, args.user))
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
def main():

   # Variable to store the password token. 
   # This is a token we get when we deploy the sensor which will allow us to set the inital password
   PWDTOKEN = "EMPTY"

   # Get the command line argumants and store them in the args variable
   args = get_args()

   # Assign each argument to a variable
   key=args.key
   sensor=args.sensor
   domain=args.domain
   user=args.user
   pwd=args.password
   name=args.name
   desc=args.desc

   # Make a directory in the users home to store cookies and other temp files
   home = expanduser("~")
   if not os.path.exists(home + '/.sensor'):
      os.makedirs(home + '/.sensor')

   # Check if the sensor is already connected to something
   # If it is we will exit
   bashCommand = 'curl -s -k -X GET "http://' + sensor + '/api/1.0/status"' # The command to run
   json_data, output = runCommand(bashCommand) # Run the command and receive the json and raw output. json = false if no json received
   if json_data: # If we received json data...
      if json_data['status'] == 'notConnected': # If the value for the status key is notConnected
         print "Info: " + sensor + " is not connected to a controller"
      else: # If the value for the status key is something other than connected
         print "Info: " + sensor + " is already connected to " + json_data['masterNode'] # Print the name of the controller it's connected to
         exit()
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
         print "Info: Waiting for " + name + " to connect to " + domain + "..."
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
            print "Info: Waiting for " +  domain + " to start..."
            time.sleep(15)
            json_data, output = runCommand(bashCommand) # Run the check status command again as we still haven't connected
         elif json_data['status'] == "connected": # We have connected
            print "Info: Connected!"
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

#########################################################################################################

# Start program
if __name__ == "__main__":
    main()

#########################################################################################################
