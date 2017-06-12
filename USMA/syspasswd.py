#!/usr/bin/env python

# Script to reset the sysadmin password

import argparse
import getpass
import os


#########################################################################################################

def get_args():
    """Get command line args from the user.
    """
    parser = argparse.ArgumentParser(
        description='Sensor, Username and Password')

    parser.add_argument('-s', '--sensor',
                        required=True,
                        action='store',
                        help='Sensor IP or DNS')

    parser.add_argument('-u', '--user',
                        required=True,
                        action='store',
                        help='User name to connect with')

    parser.add_argument('-p', '--password',
                        required=False,
                        action='store',
                        help='Password to use when connecting')

    args = parser.parse_args()

    if not args.password:
        args.password = getpass.getpass(
            prompt='Enter password for domain %s and user %s: ' %
                   (args.domain, args.user))
    return args

#########################################################################################################
def main():

   args = get_args()
   sensor=args.sensor
   user=args.user
   pwd=args.password

   temp_key = open('temp_key','w+')
   temp_key.write("-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEAzXitzhYq5x0GgJJBk3EUrExo1kDar6++fPrUJ6tkOVrSCYx/\n80ahwtreyT3iV5SG4BXvvwbEVAtFumLq3XGv1fcBacHSTRY3R4XN7ChTKDx0/XFe\n8dbWocowBW8zz8QhVSXbQCA7GshhXjdpbroHocwfa8WhOYXXd86+5MvnAHXuwqJg\nefIhgUg9Yu9hSJFv2o9/TxFOn/OooJzr2QV2gHM4mFCOP6khAYhw6UlO7vlpvGXj\nTnaJ1T4eKDE9HinMxFXeUUsPWHHX0a1uanWxEqJWAJRhdvCyH/dqlUqxnJn7Dpol\nOx0L5QB1AHDqfhz6wEbC1gp/DtYaN+JulK3rUQIDAQABAoIBAGHX3awNklCL2dTP\n0LpNVvLVT/b22yxeG++X4f8h9o/5V5uEdEl8kPshDoX2Ghpqd++tgoUMy+DZnVKs\nV/srb/gLr3iU+3gJ5DkC1pRmf3LhlzQ5EGVJUNuqVEPCOIHve4/4fveCYaLXWMZs\nzKAVphy9/xhq++NQgNJkeTKqhk4I/2BT3Cd6bunjPRQ6+zalONane4Nr0wQSzpRm\nVWFdFEc2W9UMo1TcDhKp6zqhngRwvc3BuVz0r0olNSBkEu7VTrSc9wZUjl4t4ufb\n2ou6wPalBfzIbtU+ADLg2T6N0wWQyoPurdxowGK1cLomBAA0a/yviCaMunN4qD9s\nJBNnwyECgYEA+vfcPv+w5+aANi6sIwjhAtaVHU6FBchUEA9pqURVPhGDPyC1GnXn\nyLwxsO9bLihmRIHxJgoKAwqb6NZ2GEgcAtJWRgZnJRfr8k1Tfq8b47QfE0xZz7lT\nBALY6+Qg9kTeqEchFQxgA1AWf5PqSDAiP09ulKpQC1cC++xYErQlX8MCgYEA0ZdM\nS6WDQZNIVPkigFGqp7enjBvrMKC2vVLAVmbczHJDOgNy0+pPVN5wsFIGE1ayGgTY\nTGeMhC0ZQa0ivLt5XfpNdgJ6OLdVZDCwzZxVK4dIKSlQuHpgihQvhfsx2zVQOVgI\ngMSzeorkJ9OhwIGfSIYT7KDDCmO8DcHTLE2ii1sCgYBKzr0Q7kh+J4AKJola/BeO\nMAZMsQ4HtjoQe3ekY+EA2lmD5Kz3ETQg6q/pLL/CF3q8avtFunJXi78DfYHAJSZs\nVOQwhVIThXjoRdJgjbPDgPpOV1DiETzEklC0p9CHd+niwSkETCcGdcXvC1knYWmj\n83pjyAyKBMq36zApixck3wKBgGmA/dj+gioaV8jeeG2brooqut6ely+tVw/KfiOA\nOBl6Uzj6z2y5gCG6r4MyZviJJbJPSgp7/ZHzmckjvF7BCIE0JJYI/TlboFKE6Bs4\nXO9CdCK0N3wFrl8TdjC9mAU+uxmCpRUc7zP6gotBzyS2m1XImHL/Ie8y8VEDhqfA\nlNgNAoGBAILVG3WC6zX2YRIQTLlq9I4/URngoxzUz3Vn9oIKeVgHH1OQm9YzE2mA\nk46uPvzYLL/F1hcjmIvQtlqpqjfneN8vIPfmZvVOrq0XQqgbcoZ0R2GQe+ZSSxvs\nOQ4jEY7uUDbmuXU+IHgfNvJKbJQiUtyLE3cmJWLYcscmuP1Ebbe6\n-----END RSA PRIVATE KEY-----")
   temp_key.close()

   os.system('chmod 600 temp_key')   

   bashCommand = 'ssh -oStrictHostKeyChecking=no -i temp_key root@' + sensor + ' \'echo "' + user + ':' + pwd + '" | chpasswd\''
   os.system(bashCommand)

   os.remove('temp_key')

#########################################################################################################

# Start program
if __name__ == "__main__":
    main()

#########################################################################################################
