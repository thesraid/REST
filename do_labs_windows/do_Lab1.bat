@echo off
REM joriordan@alienvault.com
set /p domain=Enter Domain: 
plink.exe root@192.168.250.13 -pw Password1! /root/scripts/resetScripts/add_sensor.py -s 192.168.250.18 -d %domain% -u usm-anywhere-training@alienvault.com -p Password1!
plink.exe root@192.168.250.13 -pw Password1! /root/scripts/resetScripts/analyst_lab1.py -d %domain% -u usm-anywhere-training@alienvault.com -p Password1! -o 3e7fd931d2459ad2d0de1ea5c1edcc3ecb73fe265641ae82120edf5e74bb80cd
pause
