@echo off
REM joriordan@alienvault.com
echo In order for this script to work you need to PuTTY to Linux at least one
echo Use PuTTY on the Desktop to connect to Linux now.
echo You do not need to log in. You can immeditely close the window
pause
echo Enter the Fully Qualified Domain name (not URL)
echo Example: training-eu-1-20170101.alienvault.cloud
set /p domain=Enter Domain: 
plink.exe root@192.168.250.13 -pw Password1! /root/scripts/resetScripts/analyst_lab2.py -d %domain% -u usm-anywhere-training@alienvault.com -p Password1!
timeout /t 5
echo We will perform two failed logins below
plink.exe -batch root@192.168.250.13 -pw WRONGPASSWORD
timeout /t 10
plink.exe -batch root@192.168.250.13 -pw WRONGPASSWORD
pause
