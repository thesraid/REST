#!/bin/bash

mapfile -t myArray < sales-server-list.txt
#printf '%s\n' "${myArray[@]}"
for x in "${myArray[@]}"
do
   #echo $x
   #./create_accounts.py -u USM-Anywhere-Training@alienvault.com -p Password1! -n SalesDemo1 SalesDemo2 SalesDemo3 SalesDemo4 SalesDemo5 -d $x
   #./confirm_sensor.py -u USM-Anywhere-Training@alienvault.com -p Password1! -d $x  
   ./run_demo_action.py -d $x -u usm-anywhere-training@alienvault.com -p Password1! -a AWSEvents SpyCloudEvents OktaEvents SuricataEvents PaloAltoEvents Assets GSuiteEvents CiscoUmbrellaEvents Office365Events AzureEvents SyslogEvents ConfigurationIssues Vulnerabilities Vulnerabilities Vulnerabilities Vulnerabilities Vulnerabilities Vulnerabilities Vulnerabilities Vulnerabilities Vulnerabilities
   echo ""
done
