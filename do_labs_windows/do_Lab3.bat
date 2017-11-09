@echo off
REM joriordan@alienvault.com
echo We will perform a bruteforce attach
REM plink.exe root@192.168.2.15 -pw Password1! /root/scripts/SSH_Overload.sh
REM timeout /t 10
REM plink.exe root@192.168.250.13 -pw Password1! /root/scripts/Malicious_Scan.sh
REM timeout /t 10
plink.exe root@192.168.2.15 -pw Password1! /usr/bin/nikto -h 192.168.250.14
REM timeout /t 10
REM START C:\Users\Administrator\Desktop\scripts\Backup_Delete_Event_Log.exe
pause