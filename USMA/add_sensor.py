#!/usr/bin/env python

"""
"""

"""
import sys
import os
import subprocess
import syslog
import time
import re
import atexit
import argparse
import getpass
from datetime import date, datetime, timedelta
from shutil import copyfile
from pyVim import connect
from pyVmomi import vmodl
from pyVmomi import vim
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

"""
Default global variables
Any of these can be changed if required
"""

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

   #print "Command: " + bashCommand

   try: # Try and run the command, if it doesn't work then except subprocess will catch it and return 1 
      output = subprocess.check_output(bashCommand, shell=True)
      try: # Try and convert the output to a json object. If the output isn't json we get a ValueError so we return false. 
         json_data = json.loads(output)
         if 'error' in json_data: # If something goes wrong the json will have a key called error. Print it's contents and exit
            print "Error: " + json_data['error']
            exit()
         else:
            return json_data, output
      except ValueError, e:
         return False, output
   except subprocess.CalledProcessError as bashError:         
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
      print output
   except subprocess.CalledProcessError as bashError:
      print "Error: Error while executing bash command"
      print "Error: " + bashCommand
      print "Error: Code", bashError.returncode, bashError.output
      exit()

   return token

#########################################################################################################
def findJSONKey(bashCommand, search_key, search_string, key):
   
   json_data, output = runCommand(bashCommand)  
   
   if not json_data:
      print "Error: Didn't receive json output"
      exit()
   else:
      for obj in json_data:
         if obj[search_key] == search_string:
            print "Info:  The " + search_key + " with the value " + search_string + " has a " + key + " with a value of " + obj[key]
            obj_string = obj[key]

   return obj_string

#########################################################################################################
def main():

   args = get_args()

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
   bashCommand = 'curl -s -k -X GET "http://' + sensor + '/api/1.0/status"'
   json_data, output = runCommand(bashCommand)
   if json_data:
      if json_data['status'] == 'notConnected':
         print "Info: " + sensor + " is not connected to a controller"
      else:
         print "Info: " + sensor + " is already connected to " + json_data['masterNode']
         exit()
   else:
      print "Error: No valid json output received"
      print output
      exit()
   
   # Connect the sensor to the controller using the key
   # The is no output from this command when it runs successfully
   print "Info: Starting connection"
   bashCommand = 'curl -s -k -X POST -H "Content-Type: application/json" -d \'{"key":"' + key + '","masterNode":"' + domain + '","name":"' + name + '","description":"' + desc + '"}\' "http://' + sensor + '/api/1.0/connect"'
   json_data, output = runCommand(bashCommand)
   if not json_data:
      print "Info: Started connection to " + domain
      print output
   else:
      print "Error: " + output
      
   
   
   # Wait while the connection is in progress
   bashCommand = 'curl -s -k -X GET -H "Content-Type: application/json" "http://' + sensor + '/api/1.0/status"'
   connected = False
   #while (not json_data or json_data['status'] != "connected"):
   while (not connected):
      if not json_data:
         print "Info: Waiting for " + name + " to connect to " + domain + "..."
         time.sleep(60)
         json_data, output = runCommand(bashCommand)
      elif json_data:
         if 'error' in json_data: # If something goes wrong the json will have a key called error. Print it's contents and exit
            print "Error: " + json_data['error']
            exit()
         elif json_data['status'] != "connected":
            print "Info: Connecting " + name + " to " + domain + "..."
            time.sleep(60)
            json_data, output = runCommand(bashCommand)
         elif json_data['status'] == "connected":
            print "Info: Connected!"
            connected = True
            # Hopefully the output of this command will contain log in details

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
