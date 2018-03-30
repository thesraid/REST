@echo off
REM joriordan@alienvault.com
echo Enter the Fully Qualified Domain name (not URL)
echo Example: training-eu-1-20170101.alienvault.cloud
set /p domain=Enter Domain: 
echo You will see no output below until the sensor is added
echo You can connect to http://192.168.250.18 to view the progress
echo You can also connect to https://%domain%/#/settings/deployment/sensors to see the sensor being added
plink.exe root@192.168.250.13 -pw Password1! /root/scripts/resetScripts/add_sensor.py -s 192.168.250.18 -d %domain% -u usm-anywhere-training@alienvault.com -p Password1!
REM echo You can ignore any windows warnings above saying that alienvault.com cannot be found
echo You will see no output below until the Asset Scan is complete
echo You can connect to https://%domain%/#/asset-groups to see the Scan taking place
echo View the Scan History of USMA-Sensor-Network to view progress
plink.exe root@192.168.250.13 -pw Password1! /root/scripts/resetScripts/analyst_lab1.py -d %domain% -u usm-anywhere-training@alienvault.com -p Password1! -o 3e7fd931d2459ad2d0de1ea5c1edcc3ecb73fe265641ae82120edf5e74bb80cd
pause
