#!/usr/bin/env python

"""
joriordan@alienvault.com
Takes a list of conrollers and checks if the specified sensor exists and is configured
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

    parser.add_argument('-d', '--domain',
                        nargs='+',
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
      #print bashCommand
      print "Info: Successfully logged into " + domain
      output = subprocess.check_output(bashCommand, shell=True)
      #print output
   except subprocess.CalledProcessError as bashError:
      print "Error: Error while executing bash command"
      print "Error: " + bashCommand
      print "Error: Code", bashError.returncode, bashError.output
      exit()

   return token

#########################################################################################################
def findJSONKey(bashCommand, search_key, search_string, key):

   obj_string = "NOT FOUND"
   
   json_data, output = runCommand(bashCommand)  
   
   if not json_data:
      print "Error: Didn't receive json output"
      exit()
   else:
      for obj in json_data:
         if obj[search_key] == search_string:
            print "Info: The " + search_key + " with the value " + search_string + " has a " + key + " with a value of " + obj[key]
            obj_string = obj[key]

   return obj_string

#########################################################################################################
def main():

   args = get_args()

   domain_list=args.domain
   user=args.user
   pwd=args.password
   name=args.name

   # Write the results to a file in the current directory
   sensors_file = open('Confirm_Sensors.txt','w+')
   sensors_file.write('SENSOR RESULTS\n')
   sensors_file.write('--------------\n')
   
   for domain in domain_list:
      # Make a directory in the users home to store cookies and other temp files
      home = expanduser("~")
      if not os.path.exists(home + '/.sensor'):
         os.makedirs(home + '/.sensor')

      # Remove any old cookie as it's no longer needed
      bashCommand = 'touch ' + home + '/.sensor/cookie.txt;rm ' + home + '/.sensor/cookie.txt'
      json_data, output = runCommand(bashCommand)

      # Login to the controller and get a token
      token = login(domain, user, pwd, home)

      # Curl command for getting a list of sensors
      bashCommand = 'curl -s -k -X GET -H \'Content-Type: application/json\' -H "X-XSRF-TOKEN: ' + token + '" -d \'{"email":"' + user + '", "password":"' + pwd + '"}\' "https://' + domain + '/api/1.0/sensors" -b ' + home + '/.sensor/cookie.txt -c ' + home + '/.sensor/cookie.txt'
      # Run the above command
      # Find the UUID for the sensor
      sensor_uuid = findJSONKey(bashCommand, 'name', name, 'uuid')

      # Confirm system is marked as configured
      # Curl command for getting a list of sensors
      bashCommand = 'curl -s -k -X GET -H \'Content-Type: application/json\' -H "X-XSRF-TOKEN: ' + token + '" -d \'{"email":"' + user + '", "password":"' + pwd + '"}\' "https://' + domain + '/api/1.0/sensors" -b ' + home + '/.sensor/cookie.txt -c ' + home + '/.sensor/cookie.txt'
      # Run the above command
      # Find the setup status for the sensor
      sensor_status = findJSONKey(bashCommand, 'name', name, 'setupStatus')
      print "Info: sensor status is " + sensor_status
      sensors_file.write(domain + " : " + name + " : " + sensor_status + "\n")

      # Remove the cookie as it's no longer needed
      bashCommand = 'rm ' + home + '/.sensor/cookie.txt'
      json_data, output = runCommand(bashCommand)

   sensors_file.close()

#########################################################################################################

# Start program
if __name__ == "__main__":
    main()

#########################################################################################################
